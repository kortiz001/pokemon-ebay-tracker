import datetime
import requests
from pokemontcgsdk import Card, Set, RestClient

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')

def fetch_pokemon_cards(ebay_api_key):
    API_TOKEN = ebay_api_key
    query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

    sets = [
        {"name": "Guardians Rising", "code": "sm2"},
        {"name": "Burning Shadows", "code": "sm3"},
        {"name": "Shining Legends", "code": "sm35"},
        {"name": "Crimson Invasion", "code": "sm4"},
        {"name": "Ultra Prism", "code": "sm5"},
        {"name": "Forbidden Light", "code": "sm6"},
        {"name": "Celestial Storm", "code": "sm7"},
        {"name": "Dragon Majesty", "code": "sm75"},
        {"name": "Lost Thunder", "code": "sm8"},
        {"name": "Team Up", "code": "sm9"},
        {"name": "Detective Pikachu", "code": "det1"},
        {"name": "Unbroken Bonds", "code": "sm10"},
        {"name": "Unified Minds", "code": "sm11"},
        {"name": "Hidden Fates", "code": "sm115"},
        {"name": "Hidden Fates Shiny Vault", "code": "sma"},
        {"name": "Cosmic Eclipse", "code": "sm12"},
        {"name": "SWSH Black Star Promos", "code": "swshp"},
        {"name": "Sword & Shield", "code": "swsh1"},
        {"name": "Rebel Clash", "code": "swsh2"},
        {"name": "Darkness Ablaze", "code": "swsh3"},
        {"name": "Champion's Path", "code": "swsh35"},
        {"name": "Vivid Voltage", "code": "swsh4"},
        {"name": "Shining Fates", "code": "swsh45"},
        {"name": "Shining Fates Shiny Vault", "code": "swsh45sv"},
        {"name": "Battle Styles", "code": "swsh5"},
        {"name": "Chilling Reign", "code": "swsh6"},
        {"name": "Evolving Skies", "code": "swsh7"},
        {"name": "Celebrations", "code": "cel25"},
        {"name": "Celebrations: Classic Collection", "code": "cel25c"},
        {"name": "Fusion Strike", "code": "swsh8"},
        {"name": "Brilliant Stars", "code": "swsh9"},
        {"name": "Brilliant Stars Trainer Gallery", "code": "swsh9tg"},
        {"name": "Astral Radiance", "code": "swsh10"},
        {"name": "Astral Radiance Trainer Gallery", "code": "swsh10tg"},
        {"name": "Lost Origin", "code": "swsh11"},
        {"name": "Lost Origin Trainer Gallery", "code": "swsh11tg"},
        {"name": "Silver Tempest", "code": "swsh12"},
        {"name": "Silver Tempest Trainer Gallery", "code": "swsh12tg"},
        {"name": "Crown Zenith", "code": "swsh12pt5"},
        {"name": "Crown Zenith Galarian Gallery", "code": "swsh12pt5gg"},
        {"name": "Scarlet & Violet", "code": "sv1"},
        {"name": "Scarlet & Violet Black Star Promos", "code": "svp"},
        {"name": "Paldea Evolved", "code": "sv2"},
        {"name": "Scarlet & Violet Energies", "code": "sve"},
        {"name": "Obsidian Flames", "code": "sv3"},
        {"name": "151", "code": "sv3pt5"},
        {"name": "Paradox Rift", "code": "sv4"},
        {"name": "Paldean Fates", "code": "sv4pt5"},
        {"name": "Temporal Forces", "code": "sv5"},
        {"name": "Twilight Masquerade", "code": "sv6"},
        {"name": "Shrouded Fable", "code": "sv6pt5"},
        {"name": "Stellar Crown", "code": "sv7"},
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

            if tcg_player_market > 60:
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
