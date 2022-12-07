from django.urls import path
from example_app.views import index, search_result


urlpatterns = [
    path('', index, name='index'),
    path('search_result', search_result, name='search_result'),
]