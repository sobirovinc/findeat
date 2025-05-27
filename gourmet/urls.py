from django.urls import path

from gourmet.views import HomePageView, nearby_places_view, GourmetDetailView, history, like_unlike, liked_shops, \
    suggestions_view

app_name = 'gourmet'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('nearby-places/<str:lat>/<str:lng>/', nearby_places_view, name='nearby_places'),
    path('detail/<str:shop_id>/', GourmetDetailView.as_view(), name='gourmet_detail'),
    path('like-unlike/', like_unlike, name='like_unlike'),
    path('history/', history, name='history'),
    path('liked-shops/', liked_shops, name='liked_shops'),
    path('suggestions/<str:lat>/<str:lng>/<str:shop_id>/', suggestions_view, name='suggestion_with_id'),
    path('suggestions/<str:lat>/<str:lng>/', suggestions_view, name='suggestion')
]