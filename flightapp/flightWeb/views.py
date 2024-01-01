# flight/views.py

from django.shortcuts import render
from django.http import JsonResponse
from .models import FlightData
from .utils.scrape_logic import scrape_logic

def index(request):
    flights = FlightData.objects.all()
    return render(request, 'flight/index.html', {'flights': flights})

def scrape_data(request):
    # Your scraping logic here
    # Call data_scraping() function and save the data to FlightData model
    scrape_logic()

    return JsonResponse({'status': 'success'})
