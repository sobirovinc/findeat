import random

import requests
from decouple import config
from requests.exceptions import Timeout, RequestException

google_maps_api_key = config('google_maps_api_key')
api_key = config('gourmet_api_key')
url = 'https://webservice.recruit.co.jp/hotpepper/gourmet/v1/'

# function gets any parameter and gives back a json response
def gourmet(parameters):
    params = {
        'key': api_key,
        'format': 'json'
    }

    # the form might give true or false but the api wants 0 or 1, so we have to check and convert
    if parameters.get('credit_card'):
        parameters['credit_card'] = 1

    if parameters.get('parking'):
        parameters['parking'] = 1

    # adding given parameters to the parameters that built in
    params.update(parameters)

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"error status code_________________ {response.status_code}")
        return None


# function gives back only nearby shops based in users location
def places_nearby(lat, lng):
    params = {
        'key': api_key,
        'format': 'json',
        'lat': lat,
        'lng': lng,
        'count': 8
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"Error status code: {response.status_code}"


# function gives back only one shop that found by id if it exists
def search_by_id(shop_id):
    try:
        response = requests.get(url, params={
            'key': api_key,
            'id': shop_id,
            'format': 'json',
        }, timeout=5)

        if response.status_code == 200:  # if success
            data = response.json()
            return data.get('results', {}).get('shop', [None])[0]
    except Timeout:
        print(f"timeout while fetching shop with id _________{shop_id}")
    except RequestException as e:
        print(f"error fetching shop_________________________ {shop_id}: {e}")

    return None


# function gives results as a dictionary/json based given parameters
def suggestion(lat, lng, liked_params):
    genres = liked_params.get('genre', [])
    budgets = liked_params.get('budget', [])

    if not genres or not budgets:
        return []  # nothing to suggest

    # getting unique sets from given liked_params and storing it in list
    all_combinations = list(set((g, b) for g in genres for b in budgets))
    random.shuffle(all_combinations)

    suggestions = []

    # search by given parameters
    for genre, budget in all_combinations:
        # loop stopper, it stops the loop when it got 8 result
        if len(suggestions) >= 8:
            break

        search_params = {
            'lat': lat,
            'lng': lng,
            'range': 3,
            'genre': genre,
            'budget': budget,
        }
        # print(f"trying... genre={genre}, budget={budget}")
        data = gourmet(search_params)
        try:
            shops = data['results']['shop']
            if shops:
                suggestions.append(shops[0])  # take only first
        except (KeyError, TypeError):
            # if error just skip
            continue
    # print(f"suggestion !!!!!!! {suggestions}")
    return suggestions


