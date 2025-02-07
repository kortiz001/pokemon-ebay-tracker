from django.shortcuts import render
from .scripts import pokemon_api_helper

def home(request):
    cards_info = pokemon_api_helper.fetch_pokemon_cards()  # Call the function to get data
    return render(request, 'home.html', {'cards_info': cards_info})