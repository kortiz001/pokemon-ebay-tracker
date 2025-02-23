import datetime
import requests
import urllib.parse
from bs4 import BeautifulSoup

def remove_duplicate_dicts(lst):
    unique_dicts = []
    unique_names = set()
    
    for d in lst:
        if d["card_name"] not in unique_names:
            unique_dicts.append(d)
            unique_names.add(d["card_name"])
    
    return unique_dicts

def generate_pricecharting_url(card_name, card_number, set_name):
    full_set_name = f"pokemon-{set_name.lower().replace(' ', '-')}"
    if set_name == "151":
        full_set_name = "pokemon-scarlet-&-violet-151"
    if set_name =="Terestal Festival":
        full_set_name = "pokemon-japanese-terastal-festival"
    if set_name == "Base":
        full_set_name = "pokemon-base-set"

    base_url = f"https://pricecharting.com/game/{full_set_name}/{card_name.lower().replace(' ', '-')}-{card_number}"
    return base_url

def return_graded_prices(pricecharting_url):
    try:
        response = requests.get(pricecharting_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        return(f"Error: {e}")

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        return(f"Error parsing HTML: {e}")

    ungraded_price_td = soup.find('td', {'id': 'used_price'})
    grade7_price_td = soup.find('td', {'id': 'complete_price'})
    grade8_price_td = soup.find('td', {'id': 'new_price'})
    grade9_price_td = soup.find('td', {'id': 'graded_price'})
    grade95_price_td = soup.find('td', {'id': 'box_only_price'})
    grade10_price_td = soup.find('td', {'id': 'manual_only_price'})

    try:
        if ungraded_price_td:
            ungraded_price = ungraded_price_td.find('span', {'class': 'price'}).text.strip() or "N/A"
        else:
            ungraded_price = "N/A"

        if grade7_price_td:
            grade7_price = grade7_price_td.find('span', {'class': 'price'}).text.strip() or "N/A"
        else:
            grade7_price = "N/A"

        if grade8_price_td:
            grade8_price = grade8_price_td.find('span', {'class': 'price'}).text.strip() or "N/A"
        else:
            grade8_price = "N/A"

        if grade9_price_td:
            grade9_price = grade9_price_td.find('span', {'class': 'price'}).text.strip() or "N/A"
        else:
            grade9_price = "N/A"

        if grade95_price_td:
            grade95_price = grade95_price_td.find('span', {'class': 'price'}).text.strip() or "N/A"
        else:
            grade95_price = "N/A"

        if grade10_price_td:
            grade10_price = grade10_price_td.find('span', {'class': 'price'}).text.strip() or "N/A"
        else:
            grade10_price = "N/A"

        return response, ungraded_price, grade7_price, grade8_price, grade9_price, grade95_price, grade10_price
    except Exception as e:
        return(f"Error extracting prices: {e}")

def fetch_pokemon_cards(
        ebay_api_key: str,
        listing_type: str,
        tcg_player_cards: dict,
        graded_check: str,
        set_to_check: str,
        minimum_bid_price: int,
        max_market_value: int,
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

    for item in sets_to_check:
        cards = tcg_player_cards[item]["cards"]
        set = item

        for card in cards:
            if card.get("price_high") < 50.00:
                continue
            if int(float(card.get("market"))) > int(max_market_value):
                continue

            try:
                url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
                headers = {
                    "Authorization": "Bearer " + ebay_api_key,
                    "Content-Type": "application/json"
                }

                maximum_bid_price = int(float(card.get('market')) * float(int(maximum_bid_percentage) * 0.01))
                
                filters_list = [
                    "buyingOptions:{AUCTION}",
                    "priceCurrency:USD",
                    "deliveryCountry:US",
                    "itemLocationCountry:US",
                    f"price:[{minimum_bid_price}..{maximum_bid_price}]", 
                    f"conditionIds:{condition_ids}",
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
                            feed_back_percentage = int(float(item.get("seller").get("feedbackPercentage")))
                            if feed_back_percentage < 95:
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

                            if graded_check == "Graded":
                                sold_link = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(item.get('title'))}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&Graded=Yes&_dcat=183454"
                            else:
                                sold_link = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(item.get('title'))}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1"
                            
                            cards_info["cards"].append({
                                "item_id": item.get("itemId"),
                                "card_name": item.get("title"),
                                "set": set,
                                "original_card_name": card.get("name"),
                                "card_number": card.get("number"),
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
                    print(f"card_name: {card.get('name')}, card_number: {card.get('number')}")
                    api_counter += 1
                else:
                    print(f"Error: {item_summary_response.status_code}")
                    print(item_summary_response.text)

            except requests.exceptions.RequestException as e:
                print(e)
    
    if listing_type == "Auction":
        cards_info["cards"].sort(key=lambda x: x['end_time'])

    seen = []
    for card in cards_info["cards"]:
        for item in seen:
            if card["card_name"] == item["card_name"]:
                continue
        seen.append(card)
    cards_info["cards"] = seen

    print(cards_info["cards"])

    # Add Graded Card Prices
    for card in cards_info["cards"]:
        price_charting_url = generate_pricecharting_url(card.get('original_card_name'), card.get('card_number'), card.get("set"))
        pricecharting_response, ungraded_price, grade7_price, grade8_price, grade9_price, grade95_price, grade10_price = return_graded_prices(price_charting_url)
        print(pricecharting_response)
        card["ungraded_price"] = ungraded_price
        card["grade7_price"] = grade7_price
        card["grade8_price"] = grade8_price
        card["grade9_price"] = grade9_price
        card["grade95_price"] = grade95_price
        card["grade10_price"] = grade10_price

    cards_info["api_counter"] = api_counter

    return cards_info