from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .scripts import pokemon_api_helper

@require_GET
def load_data(request):
    query_param = request.GET.get('ebay_api_key')
    cards_info = pokemon_api_helper.fetch_pokemon_cards()  # Run the Python script to generate data
    return JsonResponse({'cards_info': cards_info})

def home(request):
    return render(request, 'home.html')