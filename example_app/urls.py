from django.urls import path
from example_app.views import *


urlpatterns = [
    path('', index, name='index'),
    path('search_result', search_result, name='search_result'),
    path('search_result/player/<wiki_uri>/<entity_uri>', get_player_detail, name= "get_player_detail"),
    path('search_result/college/<college_uri>', get_detail_college, name="get_detail_college"),
    path('search_result/team/<team_uri>', get_detail_team, name="get_detail_team"),
]