# flight/urls.py

from django.urls import path
from .views import index, scrape_data

urlpatterns = [
    path('', index, name='index'),
    path('scrape/', scrape_data, name='scrape_data'),
]
