import datetime
import requests
import urllib.parse

def fetch_pokemon_cards(
        ebay_api_key: str,
        listing_type: str,
        tcg_player_cards: dict,
        graded_check: str,
        set_to_check: str,
        minimum_bid_price: int,
        maximum_bid_percentage: float,
        time_left_hours: int
    ):
    query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=int(time_left_hours))).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

    if set_to_check == "All":
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
    elif set_to_check == "Old Sets":
        sets_to_check = [
            "Base",
            "Jungle",
            "Wizards Black Star Promos",
            "Fossil",
            "Base Set 2",
            "Team Rocket",
            "Gym Heroes",
            "Gym Challenge",
            "Neo Genesis",
            "Neo Discovery",
            "Southern Islands",
            "Neo Revelation",
            "Neo Destiny",
            "Legendary Collection", 
            "Expedition Base Set",
            "Aquapolis",
            "Skyridge",
            "Ruby & Sapphire",
            "Sandstorm",
            "Dragon"
        ]
    else:
        sets_to_check = [set_to_check]


    if graded_check == "Graded":
        condition_ids = "{2750}"
    elif graded_check == "Ungraded":
        condition_ids = "{4000}"
    elif graded_check == "All":
        condition_ids = "{2750|4000}"

    cards_info = {}
    cards_info["cards"] = []
    api_counter = 0

    for set in sets_to_check:
        cards = tcg_player_cards[set]["cards"]

        for card in cards:
            if card.get("price_high") < 50.00:
                continue

            try:
                url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
                headers = {
                    "Authorization": "Bearer " + ebay_api_key,
                    "Content-Type": "application/json"
                }

                maximum_bid_price = int(float(card.get('market')) * float(maximum_bid_percentage))
                
                filters_list = [
                    "buyingOptions:{AUCTION}",
                    "priceCurrency:USD",
                    "deliveryCountry:US",
                    f"price:[{minimum_bid_price}..{maximum_bid_price}]", 
                    f"conditionIds:{condition_ids}",
                    "listingMarketplaceId': 'EBAY_US'",
                ]
                if listing_type == "Buy It Now":
                    filters_list.append("buyingOptions:{FIXED_PRICE}")
                else:
                    filters_list.append("buyingOptions:{AUCTION}")
                    filters_list.append(f"itemEndDate:[..{query_end_time}]",)

                params = {
                    "q": f"{card.get('name')} {card.get('number')}/{card.get('printed_total')}",
                    "filter": filters_list,
                }
                item_summary_response = requests.get(url, headers=headers, params=params)

                if item_summary_response.status_code == 200:
                    item_summary_response_dict = item_summary_response.json()

                    if item_summary_response_dict and 'itemSummaries' in item_summary_response_dict:
                        for item in item_summary_response_dict['itemSummaries']:
                            if item.get("seller").get("feedbackPercentage") < "95.0":
                                continue

                            if listing_type == "Auction":
                                end_time = datetime.datetime.strptime(item.get("itemEndDate"), '%Y-%m-%dT%H:%M:%S.%fZ')
                                end_time = end_time.replace(tzinfo=datetime.timezone.utc)
                                time_left = (end_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
                                hours = None
                                minutes, seconds = divmod(time_left, 60)
                                if minutes > 60:
                                    hours, minutes = divmod(minutes, 60)

                                if hours:
                                    time_left_message = f"{int(hours)} hours {int(minutes)} minutes"
                                else:
                                    time_left_message = f"{int(minutes)} minutes {int(seconds)} seconds"

                                current_bid_price = item.get("currentBidPrice").get("value")
                            elif listing_type == "Buy It Now":
                                time_left_message = None
                                current_bid_price = item.get("price").get("value")

                            shipping_cost = None
                            shipping_cost_type = None
                            if item.get("shippingOptions"):
                                shipping_cost_type = item.get("shippingOptions")[0].get("shippingCostType")
                                if shipping_cost_type == "FIXED":
                                    shipping_cost = item.get("shippingOptions")[0].get("shippingCost").get("value")

                            sold_link = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(item.get('title'))}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1"

                            cards_info["cards"].append({
                                "item_id": item.get("itemId"),
                                "card_name": item.get("title"),
                                "tcg_player_card_link": card.get("card_link"),
                                "view_item_url": item.get("itemWebUrl"),
                                "time_left": time_left_message,
                                "current_bid_price": current_bid_price,
                                "market_value": card.get("market"),
                                "image_url": item.get("image").get("imageUrl").replace("l225.jpg", "l1600.jpg"),
                                "end_time": item.get("itemEndDate"),
                                "shipping_cost": shipping_cost,
                                "shipping_cost_type": shipping_cost_type,
                                "sold_link": sold_link
                            })

                    api_counter += 1
                else:
                    print(f"Error: {item_summary_response.status_code}")
                    print(item_summary_response.text)

            except requests.exceptions.RequestException as e:
                print(e)
    
    if listing_type == "Auction":
        cards_info["cards"].sort(key=lambda x: x['end_time'])
    cards_info["cards"] = [dict(t) for i, t in enumerate(cards_info["cards"]) if t not in cards_info["cards"][:i]]
    cards_info["api_counter"] = api_counter

    return cards_info