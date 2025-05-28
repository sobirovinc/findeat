from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .api_functions import places_nearby, gourmet, google_maps_api_key, search_by_id, suggestion
from .forms import GourmetSearchForm
from .models import Like
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator


class HomePageView(View):
    def get(self, request):
        form = GourmetSearchForm()
        # ip_address = request.META['REMOTE_ADDR']
        # print(f"IP address {ip_address}")

        context = {
            'form': form,
            'loader_count': list(range(0, 4))
        }
        return render(request, 'gourmet/home_page.html', context)

    def post(self, request):
        form = GourmetSearchForm(request.POST)
        params = {}
        if form.is_valid():
            for k, v in form.cleaned_data.items():
                # checking if values is exists, and if exists adding to params dict to send it api
                print(f"{k}:{v}")
                if v is not None and v != '' and v != False:
                    params[k] = v

                # we find nearby places only if range is set
                #     because logically setting the lat and lng would stop finding shops by name
                if params.get('range'):
                    lat = request.POST.get('lat')
                    lng = request.POST.get('lng')
                    if lat and lng:
                        params['lat'] = lat
                        params['lng'] = lng

            start = request.POST.get('start') or '1'
            params['start'] = start

            result = gourmet(params)
            try:
                results_data = result['results']
                results_start = int(results_data.get('results_start', 1))
                results_returned = int(results_data.get('results_returned', 0))
                results_available = int(results_data.get('results_available', 0))

                result_ends = results_start + results_returned - 1
                next_page_start = results_start + results_returned
                prev_page_start = max(1, results_start - results_returned)

            # if not legit result, set automatically
            except (KeyError, TypeError, ValueError) as e:
                print("error:", e)
                result_ends = 0
                next_page_start = 0
                prev_page_start = 1
                results_available = 0

            form = GourmetSearchForm()
            context = {
                'params': params,
                'result_ends': result_ends,
                'results_start': results_start,
                'results_available': results_available,
                'next_page_start': next_page_start,
                'prev_page_start': prev_page_start,
                'data': result,
                'form': form
            }

            return render(request, 'gourmet/results_page.html', context)

        # print("form is not valid:", form.errors)
        return render(request, 'gourmet/error_page.html')


def nearby_places_view(request, lat, lng):
    result = places_nearby(lat, lng)

    return JsonResponse(result)


class GourmetDetailView(View):
    def get(self, request, shop_id):
        visitor_id = request.visitor_id

        like_count = Like.objects.filter(shop_id=shop_id).count()
        user_liked = Like.objects.filter(shop_id=shop_id, visitor_id=visitor_id).exists()

        shop_data = search_by_id(shop_id)

        if not shop_data:
            return render(request, 'gourmet/error_page.html')

        # adding shop_id to recent history in session
        history = request.session.get('recent_shops', [])
        if shop_id in history:
            history.remove(shop_id)  # Remove
        history.insert(0, shop_id)  # and move it to the front
        request.session['recent_shops'] = history[:8]  # keep max 8

        context = {
            'shop': shop_data,
            'like_count': like_count,
            'user_liked': user_liked,
            'google_maps_api_key': google_maps_api_key,
        }

        return render(request, 'gourmet/details_page.html', context)


@require_POST
def like_unlike(request):
    visitor_id = request.visitor_id
    shop_id = request.POST.get('shop_id')

    if not shop_id:
        return JsonResponse({'success': False, 'error': 'No shop_id'}, status=400)

    like, created = Like.objects.get_or_create(visitor_id=visitor_id, shop_id=shop_id)

    # check if like already exists or not
    if not created:  # if exists
        like.delete()  #delete the existing like  //  unlike
        liked = False
    else:   # if not exists

        # add current shops budget and genre code to the liked params
        liked_params = request.session.get('liked_params', {
            'genre': [],
            'sub_genre': [],
            'budget': []
        })

        try:
            shop_data = search_by_id(shop_id)

            if shop_data:
                if shop_data.get('genre'):
                    liked_params['genre'].append(shop_data['genre']['code'])

                if shop_data.get('budget'):
                    liked_params['budget'].append(shop_data['budget']['code'])

                request.session['liked_params'] = liked_params
        except Exception as e:
            print(f"Error liked_params: {e}")
        # set like
        liked = True

    like_count = Like.objects.filter(shop_id=shop_id).count()

    context = {
        'success': True,
        'liked': liked,
        'like_count': like_count
    }

    return JsonResponse(context)


def suggestions_view(request, lat, lng, shop_id=None):
    try:
        visitor_id = request.visitor_id
        liked_objects = Like.objects.filter(visitor_id=visitor_id)

        liked_shops = []
        for obj in liked_objects:
            liked_shop_id = obj.shop_id
            if liked_shop_id and liked_shop_id != "undefined":
                shop = search_by_id(liked_shop_id)
                if isinstance(shop, dict):  # check if search_by_id gave back dictionary
                    liked_shops.append(shop)
                else:
                    # print(f"invalid shop data for shop_id______________ {liked_shop_id}: {shop}")
                    continue

        # if no likes yet, but visiting a shop detail page then suggest similar to that shop //mostly for the new users
        if not liked_shops and shop_id:
            shop_data = search_by_id(shop_id)
            if shop_data:
                genre = shop_data.get('genre', {}).get('code')
                budget = shop_data.get('budget', {}).get('code')

                if genre and budget:
                    parameters = {
                        'genre': genre,
                        'budget': budget
                    }
                    data = gourmet(parameters)
                    return JsonResponse({'suggestions': data}, safe=False)

        # no likes yet, no shop_id  show nearby places (in the homepage)
        if not liked_shops:
            nearby_places = places_nearby(lat, lng)
            return JsonResponse({'suggestions': nearby_places}, safe=False)

        # user has liked some shops already then base suggestions on preferences
        genres = []
        budgets = []

        for shop in liked_shops:
            genre_info = shop.get('genre')
            budget_info = shop.get('budget')

            if genre_info and isinstance(genre_info, dict):
                genres.append(genre_info.get('code'))

            if budget_info and isinstance(budget_info, dict):
                budgets.append(budget_info.get('code'))

        liked_params = {
            'genre': genres,
            'budget': budgets
        }

        suggestions_data = suggestion(lat, lng, liked_params)
        return JsonResponse({'suggestions': suggestions_data}, safe=False)

    except Exception as e:
        import traceback
        print("Error in suggestions_view:", traceback.format_exc())
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


def history(request):
    # if history exists in cookies // if not create a list for history
    shop_ids = request.session.get('recent_shops', [])
    history = []

    for shop_id in shop_ids:
        if shop_id != 'undefined':
            shops = search_by_id(shop_id)
            history.append(shops)
    return JsonResponse({'history': history})


# def update_history(request, shop_id):
#     history = request.session.get('recent_shops', [])
#     if shop_id in history:
#         history.remove(shop_id)
#     history.insert(0, shop_id)
#     request.session['recent_shops'] = history[:8]  # it keeps only latest 8


def liked_shops(request):
    visitor_id = request.visitor_id
    liked_objects = Like.objects.filter(visitor_id=visitor_id)
    # print(f'liked_objects!!!!!!!!!!!!!!! {liked_objects}')

    liked_inner = []

    for obj in liked_objects:
        # print(f'obj!!!!!!!! {obj}')
        shop_id = obj.shop_id
        # print(shop_id)
        if shop_id != 'undefined':
            shops = search_by_id(shop_id)
            # print(shops)
            liked_inner.append(shops)

    # djangos built in paginator
    page_size = request.GET.get('page_size', 10)
    paginator = Paginator(liked_inner, page_size)
    page_num = request.GET.get('page', 1)
    liked = paginator.get_page(page_num)
    # print(f'page_obj !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{liked}')

    context = {
        'liked': liked,
        'page_obj': liked,
        'liked_objects_count': len(liked_objects)
    }

    return render(request, 'gourmet/liked_shops.html', context)





