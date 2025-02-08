from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .scripts import pokemon_api_helper, tcgplayer_cards_info

@require_GET
def load_data(request):
    ebay_api_key = request.GET.get('ebay_api_key')
    graded_check = request.GET.get('graded_check', "All")
    set_to_check = request.GET.get('set_to_check', "All")
    minimum_bid_price = request.GET.get('min_bid_price', 10)
    maximum_bid_percentage = request.GET.get('max_bid_percentage', 0.8)
    time_left_hours = request.GET.get('time_left_hours', 1)
    tcg_player_cards = tcgplayer_cards_info.cards_info
    cards_info = pokemon_api_helper.fetch_pokemon_cards(
        ebay_api_key=ebay_api_key,
        tcg_player_cards=tcg_player_cards,
        graded_check=graded_check,
        set_to_check=set_to_check,
        minimum_bid_price=minimum_bid_price,
        maximum_bid_percentage=maximum_bid_percentage,
        time_left_hours=time_left_hours
    ) 
    return JsonResponse({'cards_info': cards_info})

def home(request):
    return render(request, 'home.html')