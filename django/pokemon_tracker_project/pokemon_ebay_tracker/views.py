import json
from decimal import Decimal
from datetime import datetime, date
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .scripts import pokemon_tracker, tcgplayer_cards_info
from .models import SavedItem

@require_GET
def load_data(request):
    ebay_api_key = request.GET.get('ebay_api_key')
    graded_check = request.GET.get('graded_check', "All")
    set_to_check = request.GET.get('set_to_check', "All")
    minimum_bid_price = request.GET.get('min_bid_price', 10)
    max_market_value = request.GET.get('max_market_value', 150)
    maximum_bid_percentage = request.GET.get('max_bid_percentage', 80)
    time_left_hours = request.GET.get('time_left_hours', 1)
    listing_type = request.GET.get('listing_type', "Auction")
    tcg_player_cards = tcgplayer_cards_info.cards_info
    cards_info = pokemon_tracker.fetch_pokemon_cards(
        ebay_api_key=ebay_api_key,
        listing_type=listing_type,
        tcg_player_cards=tcg_player_cards,
        graded_check=graded_check,
        set_to_check=set_to_check,
        minimum_bid_price=minimum_bid_price,
        max_market_value=max_market_value,
        maximum_bid_percentage=maximum_bid_percentage,
        time_left_hours=time_left_hours
    ) 
    return JsonResponse({'cards_info': cards_info["cards"], 'api_counter': cards_info["api_counter"]})

def write_saved_item(request):
    try:
        # Getting parameters from the GET request
        ebay_id = request.GET.get('ebay_id')
        date = request.GET.get('date')
        name = request.GET.get('name')
        image_url = request.GET.get('image_url')
        ebay_url = request.GET.get('ebay_url')
        price = request.GET.get('price')
        max_bid_price = request.GET.get('max_bid_price')
        time_left = request.GET.get('time_left')
        ungraded_price = request.GET.get('ungraded_price')
        grade7_price = request.GET.get('grade7_price')
        grade8_price = request.GET.get('grade8_price')
        grade9_price = request.GET.get('grade9_price')
        grade95_price = request.GET.get('grade95_price')
        grade10_price = request.GET.get('grade10_price')

        # Check if all required fields are present
        if not ebay_id or not name or not price or not max_bid_price:
            return JsonResponse({"message": "Missing required parameters"}, status=400)

        # Use datetime.datetime.strptime to convert the date string into a date object
        date_object = datetime.strptime(date, '%Y-%m-%d').date()  # Correct usage of strptime

        # Save to the database
        saved_item = SavedItem(
            ebay_id=ebay_id,
            date=date_object,
            name=name,
            image_url=image_url,
            ebay_url=ebay_url,
            price=price,
            max_bid_price=max_bid_price,
            time_left=time_left,
            ungraded_price=ungraded_price,
            grade7_price=grade7_price,
            grade8_price=grade8_price,
            grade9_price=grade9_price,
            grade95_price=grade95_price,
            grade10_price=grade10_price
        )
        saved_item.save()

        return JsonResponse({"message": "Saved item created successfully"})

    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

def home(request):
    return render(request, 'home.html')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, date):
        return obj.isoformat()
    raise TypeError

def tracker(request):
    current_date = date.today()
    objects = SavedItem.objects.filter(date=current_date)
    saved_items = list(objects.values())
    saved_items_json = json.dumps(saved_items, default=decimal_default)
    return render(request, 'tracker.html', {'saved_items': saved_items_json})

def saved(request):
    today = date.today()
    saved_items = SavedItem.objects.filter(date=today)
    return render(request, 'saved.html', {'saved_items': saved_items})