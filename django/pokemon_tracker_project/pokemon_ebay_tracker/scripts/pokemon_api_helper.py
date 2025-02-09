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
                item_summary_response = requests.get(url, headers=headers, params=params)

                if item_summary_response.status_code == 200:
                    item_summary_response_dict = item_summary_response.json()
                    if item_summary_response_dict and 'itemSummaries' in item_summary_response_dict:
                        for item in item_summary_response_dict['itemSummaries']:
                            if item.get("seller").get("feedbackPercentage") < "95.0":
                                continue

                            end_time = datetime.datetime.strptime(item.get("itemEndDate"), '%Y-%m-%dT%H:%M:%S.%fZ')
                            end_time = end_time.replace(tzinfo=datetime.timezone.utc)
                            time_left = (end_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
                            minutes, seconds = divmod(time_left, 60)

                            cards_info.append({
                                "card_name": item.get("title"),
                                "tcg_player_card_link": card.get("card_link"),
                                "view_item_url": item.get("itemWebUrl"),
                                "time_left": f"{int(minutes)} minutes {int(seconds)} seconds",
                                "current_bid_price": item.get("currentBidPrice").get("value"),
                                "market_value": card.get("market"),
                                "image_url": item.get("image").get("imageUrl"),
                                "end_time": item.get("itemEndDate")
                            })
                else:
                    print(f"Error: {item_summary_response.status_code}")
                    print(item_summary_response.text)

            except requests.exceptions.RequestException as e:
                print(e)
    
    cards_info.sort(key=lambda x: x['end_time'])
    return cards_info