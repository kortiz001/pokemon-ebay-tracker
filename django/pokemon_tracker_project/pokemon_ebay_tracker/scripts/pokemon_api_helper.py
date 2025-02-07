import datetime
import requests
from pokemontcgsdk import Card, Set, RestClient

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')

def fetch_pokemon_cards(ebay_api_key):
    API_TOKEN = ebay_api_key
    query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

    sets = [
        {"name": "151", "code": "sv3pt5"},
        {"name": "Temporal Forces", "code": "sv5"},
        {"name": "Paldea Evolved", "code": "sv2"},
        {"name": "Crown Zenith Galarian Gallery", "code": "swsh12pt5gg"},
        {"name": "Evolving Skies", "code": "swsh7"},
        {"name": "Crown Zenith", "code": "swsh12pt5"},
        {"name": "Surging Sparks", "code": "sv8"},
        {"name": "Prismatic Evolutions", "code": "sv8pt5"}
    ]

    cards_info = []

    for set in sets:
        cards = Card.where(q=f'set.name:"{set.get("name")}" supertype:pokemon')
        
        for card in cards:
            if card.tcgplayer is None:
                continue

            tcg_player = card.tcgplayer
            tcg_player_prices = tcg_player.prices
            for price_type in ['normal', 'holofoil', 'reverse_holofoil']:
                if getattr(tcg_player_prices, price_type):
                    tcg_player_market = getattr(tcg_player_prices, price_type).market
                    break
            else:
                continue

            if tcg_player_market > 20:
                try:
                    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
                    headers = {
                        "Authorization": "Bearer " + API_TOKEN,
                        "Content-Type": "application/json"
                    }

                    params = {
                        "q": f"{card.name} {card.number}/{card.set.printedTotal}",
                        "filter": [
                            "buyingOptions:{AUCTION}",
                            f"price:[0..{tcg_player_market * 0.80:.2f}]",
                            "priceCurrency:USD",
                            f"itemEndDate:[..{query_end_time}]",
                            "conditionIds:{2750|4000}"
                        ]
                    }

                    response = requests.get(url, headers=headers, params=params)

                    if response.status_code == 200:
                        response_dict = response.json()
                        if response_dict and 'itemSummaries' in response_dict:
                            for item in response_dict['itemSummaries']:
                                item_id = item['itemId']
                                
                                url = f"https://api.ebay.com/buy/browse/v1/item/{item_id}"
                                response = requests.get(url, headers=headers, params=params)
                                
                                if response.status_code == 200:
                                    response = response.json()

                                    if response.get("seller").get("feedbackPercentage") == "0.0":
                                        continue

                                    end_time = datetime.datetime.strptime(response.get("itemEndDate"), '%Y-%m-%dT%H:%M:%S.%fZ')
                                    end_time = end_time.replace(tzinfo=datetime.timezone.utc)
                                    time_left = (end_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
                                    minutes, seconds = divmod(time_left, 60)

                                    cards_info.append({
                                        "card_name": card.name,
                                        "view_item_url": response['itemWebUrl'],
                                        "time_left": f"{int(minutes)} minutes {int(seconds)} seconds",
                                        "current_bid_price": response["currentBidPrice"]["value"],
                                        "market_value": tcg_player_market,
                                        "image_url": response.get("image").get("imageUrl")
                                    })
                    else:
                        print(f"Error: {response.status_code}")
                        print(response.text)

                except requests.exceptions.RequestException as e:
                    print(e)
    
    return cards_info
