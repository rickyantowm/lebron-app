from django.urls import path
from example_app.views import index, search_result, get_player_detail


urlpatterns = [
    path('', index, name='index'),
    path('search_result', search_result, name='search_result'),
    path('search_result/player/<wiki_uri>/<entity_uri>', get_player_detail, name= "get_player_detail")
]