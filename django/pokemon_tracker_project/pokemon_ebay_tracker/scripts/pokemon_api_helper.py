import datetime
import requests

def fetch_pokemon_cards(
        ebay_api_key: str,
        tcg_player_cards: dict,
        graded_check: str,
        set_to_check: str,
        minimum_bid_price: int,
        maximum_bid_percentage: float,
        time_left_hours: int
    ):
    query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=int(time_left_hours))).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

    if set_to_check != "All":
        sets_to_check = [set_to_check]
    else:
        sets_to_check = [
            "Prismatic Evolutions",
            "Surging Sparks",
            "Crown Zenith",
            "Crown Zenith Galarian Gallery",
            "Evolving Skies",
            "Paldea Evolved",
            "151",
            "Obsidian Flames",
            "Vivid Voltage",
            "Silver Tempest",
            "Astral Radiance",
            "Brilliant Stars",
            "Twilight Masquerade",
            "Paldean Fates",
            "Paradox Rift",
        ]

    if graded_check == "Graded":
        condition_ids = "{2750}"
    elif graded_check == "Ungraded":
        condition_ids = "{4000}"
    elif graded_check == "All":
        condition_ids = "{2750|4000}"

    cards_info = []

    for set in sets_to_check:
        cards = tcg_player_cards[set]["cards"]

        for card in cards:
            try:
                url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
                headers = {
                    "Authorization": "Bearer " + ebay_api_key,
                    "Content-Type": "application/json"
                }

                maximum_bid_price = int(float(card.get('market')) * float(maximum_bid_percentage))
                params = {
                    "q": f"{card.get('name')} {card.get('number')}/{card.get('printed_total')}",
                    "filter": [
                        "buyingOptions:{AUCTION}",
                        "priceCurrency:USD",
                        "deliveryCountry:US",
                        f"price:[{minimum_bid_price}..{maximum_bid_price}]", 
                        f"itemEndDate:[..{query_end_time}]",
                        f"conditionIds:{condition_ids}",
                    ]
                }
                response = requests.get(url, headers=headers, params=params)
                print(response.json())

                if response.status_code == 200:
                    response_dict = response.json()
                    if response_dict and 'itemSummaries' in response_dict:
                        for item in response_dict['itemSummaries']:
                            item_id = item['itemId']
                            
                            url = f"https://api.ebay.com/buy/browse/v1/item/{item_id}"
                            response = requests.get(url, headers=headers, params=params)
                            
                            if response.status_code == 200:
                                response = response.json()

                                if response.get("seller").get("feedbackPercentage") < "95.0":
                                    continue

                                end_time = datetime.datetime.strptime(response.get("itemEndDate"), '%Y-%m-%dT%H:%M:%S.%fZ')
                                end_time = end_time.replace(tzinfo=datetime.timezone.utc)
                                time_left = (end_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
                                minutes, seconds = divmod(time_left, 60)

                                cards_info.append({
                                    "card_name": response["title"],
                                    "tcg_player_card_link": card.get("card_link"),
                                    "view_item_url": response["itemWebUrl"],
                                    "time_left": f"{int(minutes)} minutes {int(seconds)} seconds",
                                    "current_bid_price": response["currentBidPrice"]["value"],
                                    "market_value": card.get("market"),
                                    "image_url": response.get("image").get("imageUrl"),
                                    "end_time": response.get("itemEndDate")
                                })
                else:
                    print(f"Error: {response.status_code}")
                    print(response.text)

            except requests.exceptions.RequestException as e:
                print(e)
    
    cards_info.sort(key=lambda x: x['end_time'])
    return cards_info