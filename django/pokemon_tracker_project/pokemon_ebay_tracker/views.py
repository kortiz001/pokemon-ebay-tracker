import json
import pytz
from decimal import Decimal
from datetime import datetime, date
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .scripts import pokemon_tracker, tcgplayer_cards_info, tcgplayer_cards_info_psa_check
from .models import EbayAPIKey, SavedItem, SearchExclusion

@require_GET
def load_data(request):
    search_exclusions = SearchExclusion.objects.values()

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
        time_left_hours=time_left_hours,
        search_exclusions=search_exclusions
    ) 
    return JsonResponse({'cards_info': cards_info["cards"], 'api_counter': cards_info["api_counter"]})

def write_saved_item(request):
    try:
        # Getting parameters from the GET request
        ebay_id = request.GET.get('ebay_id')
        name = request.GET.get('name')
        image_url = request.GET.get('image_url')
        ebay_url = request.GET.get('ebay_url')
        sold_url = request.GET.get('sold_url')
        buy_it_now_url = request.GET.get('buy_it_now_url')
        price = request.GET.get('price')
        max_bid_price = request.GET.get('max_bid_price')
        time_left = request.GET.get('time_left')
        end_time = request.GET.get('end_time')
        ungraded_price = request.GET.get('ungraded_price')
        grade7_price = request.GET.get('grade7_price')
        grade8_price = request.GET.get('grade8_price')
        grade9_price = request.GET.get('grade9_price')
        grade95_price = request.GET.get('grade95_price')
        grade10_price = request.GET.get('grade10_price')

        eastern = pytz.timezone('US/Eastern')
        if end_time:
            dt = datetime.fromisoformat(end_time[:-1])
            eastern_dt = dt.astimezone(eastern)
            date = eastern_dt.strftime('%Y-%m-%d')

            end_time = end_time[:-5] + 'Z'

        # Check if all required fields are present
        if not ebay_id or not name or not price or not max_bid_price:
            return JsonResponse({"message": "Missing required parameters"}, status=400)

        # Save to the database
        saved_item = SavedItem(
            ebay_id=ebay_id,
            date=date,
            name=name,
            image_url=image_url,
            ebay_url=ebay_url,
            sold_url=sold_url,
            buy_it_now_url=buy_it_now_url,
            price=price,
            max_bid_price=max_bid_price,
            time_left=time_left,
            end_time=end_time,
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
    
def delete_saved_item(request):
    try:
        ebay_id = request.GET.get('ebay_id')
        SavedItem.objects.filter(ebay_id=ebay_id).delete()
        return JsonResponse({"message": "Saved item deleted successfully"})
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

def write_search_exclusion(request):
    try:
        # Getting parameters from the GET request
        search_exclusion = request.GET.get('search_exclusion')

        # Check if all required fields are present
        if not search_exclusion:
            return JsonResponse({"message": "Missing required parameters"}, status=400)

        try:
            SearchExclusion.objects.get(exclusion=search_exclusion)
            print("Exclusion already exists")
        except SearchExclusion.DoesNotExist:
            SearchExclusion.objects.create(exclusion=search_exclusion)
            print("Exclusion created successfully")

        return JsonResponse({"message": "Search exclusion created successfully"})

    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
    
def delete_search_exclusion(request):
    try:
        search_exclusion = request.GET.get('search_exclusion')
        SearchExclusion.objects.filter(exclusion=search_exclusion).delete()
        return JsonResponse({"message": "Search exclusion deleted successfully"})
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

def save_api_key(request):
    try:
        api_key = request.GET.get('ebay_api_key')
        
        EbayAPIKey.objects.update_or_create(
            id=1,
            defaults={'api_key': api_key}
        )

        return JsonResponse({"message": "API key saved successfully"})
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
    
def search_exclusions(request):
    search_exclusions = SearchExclusion.objects.all()
    return render(request, 'exclusions.html', {'search_exclusions': search_exclusions})
    
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
    ebay_api_key = EbayAPIKey.load()
    ebay_api_key = ebay_api_key.api_key
    saved_items = list(objects.values())
    saved_items_json = json.dumps(saved_items, default=decimal_default)
    return render(request, 'tracker.html', {'saved_items': saved_items_json, 'ebay_api_key': ebay_api_key})

def saved(request):
    today = date.today()
    saved_items = SavedItem.objects.filter(date__gte=today)
    return render(request, 'saved.html', {'saved_items': saved_items})

def psa_tracker(request):
    tcg_player_cards = tcgplayer_cards_info_psa_check.cards_info

    return render(request, 'psa_tracker.html', {'cards_info': tcg_player_cards})