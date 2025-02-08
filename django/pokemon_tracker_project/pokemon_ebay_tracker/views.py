from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .scripts import pokemon_api_helper, tcgplayer_cards_info

@require_GET
def load_data(request):
    ebay_api_key = request.GET.get('ebay_api_key')
    tcg_player_cards = tcgplayer_cards_info.cards_info
    cards_info = pokemon_api_helper.fetch_pokemon_cards(ebay_api_key, tcg_player_cards)  # Run the Python script to generate data
    return JsonResponse({'cards_info': cards_info})

def home(request):
    return render(request, 'home.html')