import datetime
import requests
from pokemontcgsdk import Card, Set, RestClient

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')
API_TOKEN = "v^1.1#i^1#f^0#p^1#r^0#I^3#t^H4sIAAAAAAAAAOVYbWwURRi+u15bmno0fBQsqKkLokJub3b3rre34a5ce2Ar197JtbUUlOzHLN12v9yda3sGm9rEGj+iqeEHWBFi0BglImgkMUaNP9RfagiNwUAMxE9QMAZiQBPd3R7lWglfvcQm3p/LvPPOO8/zzPvOzA4YKqtYOdI08ofPXe7ZMwSGPG43UQkqykpXzS3xLCl1gQIH956h5UPe4ZKfVpusIuvMBmjqmmrC2gFFVk3GMUaxrKEyGmtKJqOyCjQZxDOZeEuSIXHA6IaGNF6TsdrmRBTjKFYIB1mCEDmBC/O0ZVUvxWzToliQChEEDFMhlguGODpo9ZtmFjarJmJVFMVIQIb8gPSDcBtBMwTFUCGcjIAurLYDGqakqZYLDrCYA5dxxhoFWK8OlTVNaCArCBZrjq/LpOLNibWtbasDBbFieR0yiEVZc2qrURNgbQcrZ+HVpzEdbyaT5XlomlggNjHD1KBM/BKYm4DvSE3RPFlHQZ4kRQ7yVFGUXKcZCouuDsO2SIJfdFwZqCIJ5a4lqCUG1wN5lG+1WiGaE7X23wNZVpZECRpRbG1DfGM8ncZi62GfpKYM5Ne1Xqhoqj+9IeEnBDJCcEAg/HV1EJJ0mM7PMxEsL/K0iRo1VZBsyczaVg01QAs0nC4NKJDGckpZM8dFZAMq8CPBJQnpYJe9pBNrmEXdqr2qULF0qHWa116AydEIGRKXRXAywvQOR6Eoxuq6JGDTO51MzCfPgBnFuhHSmUCgv78f76dwzdgaIAEgAp0tyQzfDRUWc3ztWrf9pWsP8EsOFR5aI02JQTndwjJgZaoFQN2KxUJEMByO5HWfCis23fovQwHnwNR6KFZ9iDzJiRGhjg5FglAsSn3E8ikasGFAjs35FdbohUiXWR76eSvNsgo0JMGKJZIULUK/UBcR/cGIKPq5kFDnJ0QIAYQcx0fo/1GZXG+iZyBvQFSkTC9Slud612Uak+sVmGhvVBKGkgDJTFLpkAOBVraHVTp6UKfUwCYjYroler21cEXyjbJkKdNmzV8sAexaL44ITZqJoDAjehle02FakyU+N7sWmDKENGugXAbKsmWYEcm4rjcXa6cuEr0b2yVujnYxD6j/5HC6IivTztjZxcoeb1oBWF3C7fMH5zUloLHWvcOuddu8xUE9I96SdWmdVawtkhNsJWHiuok7lHGzj8cNaGpZw7po4yn7+tVmJblqHWfI0GQZGh3EjMtZUbKI5WQ42+q6CAkusbPsrCXCFB0JkYAIzYgX75ykW2bbllS0ndgbv+ErdWDq533M5fyIYfcnYNj9ocftBqvBXcQycGdZSbu35JYlpoQgLrEibkpbVeur1YB4L8zprGR4Fri+nJsUHm9Knh/isocePFdPu3wFrwt7HgK3Tr4vVJQQlQWPDeC2yz2lRNViHxkCJAgTNEFRoS6w7HKvl1jkXXhHctznfW+xvsK3/7Hzbu2b0VjVZ8A36eR2l7q8w27XwUcy1HZlfXV0/serDp0Dm5/fvdR1cezwmfE4M3b3QXj8g8qqHQ/XNOzcPbzt7Bz+q1Mtb5sv15SfTR0Xystvb0ceauzEs0+vmX9k15NzRuQq96sXN518dM38eQMb3/17Yc+i+/Y+E4j/2lfz2vJvN6ZW0Iuw+u9+bMuUx6vcNZXbyn2Hzp5+qu/0yeTIF9v/fLNrRffvX69s3Dm2K3pgfPjE5tScHaNHR/96ZS0QFsud/ZE36i8MuuiKC3vrBz0flXUcbX2n/f3B7VUHzikHif5Nv5y6/7el+8jRT9WfqwdLmvYteOnFe0JN3x+ruHdu/Q+pzrf2+6qPiNXjrz/xwoJ5S1s+TzccPqM8lzt2cmIt/wE90YvY9xEAAA=="

def fetch_pokemon_cards():
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
