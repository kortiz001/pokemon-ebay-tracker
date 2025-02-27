import json
import random
import requests
import time
from japanese_sets.dict import TERESTAL_FESTIVAL
from pokemontcgsdk import Card, RestClient
from bs4 import BeautifulSoup

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')

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
    default_prices = {
        "ungraded": "N/A",
        "grade7": "N/A",
        "grade8": "N/A",
        "grade9": "N/A",
        "grade95": "N/A",
        "grade10": "N/A"
    }
    
    try:
        response = requests.get(pricecharting_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return default_prices

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        return default_prices

    ungraded_price_td = soup.find('td', {'id': 'used_price'})
    grade7_price_td = soup.find('td', {'id': 'complete_price'})
    grade8_price_td = soup.find('td', {'id': 'new_price'})
    grade9_price_td = soup.find('td', {'id': 'graded_price'})
    grade95_price_td = soup.find('td', {'id': 'box_only_price'})
    grade10_price_td = soup.find('td', {'id': 'manual_only_price'})

    try:
        prices = {
            'ungraded': ungraded_price_td,
            'grade7': grade7_price_td,
            'grade8': grade8_price_td,
            'grade9': grade9_price_td,
            'grade95': grade95_price_td,
            'grade10': grade10_price_td
        }

        extracted_prices = {}
        for grade, td in prices.items():
            extracted_prices[grade] = (td.find('span', {'class': 'price'}).text.strip() if td else "N/A")

        return extracted_prices
    except Exception as e:
        return default_prices

def generate_tcgplayer_json():
    sets = [
        {"name": "Base", "code": "base1"},
        {"name": "Jungle", "code": "base2"},
        {"name": "Wizards Black Star Promos", "code": "basep"},
        {"name": "Fossil", "code": "base3"},
        {"name": "Base Set 2", "code": "base4"},
        {"name": "Team Rocket", "code": "base5"},
        {"name": "Gym Heroes", "code": "gym1"},
        {"name": "Gym Challenge", "code": "gym2"},
        {"name": "Neo Genesis", "code": "neo1"},
        {"name": "Neo Discovery", "code": "neo2"},
        {"name": "Southern Islands", "code": "si1"},
        {"name": "Neo Revelation", "code": "neo3"},
        {"name": "Neo Destiny", "code": "neo4"},
        {"name": "Legendary Collection", "code": "base6"},
        {"name": "Expedition Base Set", "code": "ecard1"},
        {"name": "Aquapolis", "code": "ecard2"},
        {"name": "Skyridge", "code": "ecard3"},
        {"name": "Ruby & Sapphire", "code": "ex1"},
        {"name": "Sandstorm", "code": "ex2"},
        {"name": "Dragon", "code": "ex3"},
        {"name": "Paradox Rift", "code": "sv4"},
        {"name": "Paldean Fates", "code": "sv4pt5"},
        {"name": "Twilight Masquerade", "code": "sv6"},
        {"name": "Brilliant Stars", "code": "swsh9"},
        {"name": "Astral Radiance", "code": "swsh10"},
        {"name": "Silver Tempest", "code": "swsh12"},
        {"name": "Vivid Voltage", "code": "swsh4"},
        {"name": "Obsidian Flames", "code": "sv3"},
        {"name": "151", "code": "sv3pt5"},
        {"name": "Paldea Evolved", "code": "sv2"},
        {"name": "Crown Zenith Galarian Gallery", "code": "swsh12pt5gg"},
        {"name": "Evolving Skies", "code": "swsh7"},
        {"name": "Crown Zenith", "code": "swsh12pt5"},
        {"name": "Surging Sparks", "code": "sv8"},
        {"name": "Prismatic Evolutions", "code": "sv8pt5"}
    ]

    full_set_dicts = {}
    for set in sets:
        full_set_dicts[set.get("name")] = {
            "code": set.get("code"),
            "cards": []
        }
        cards = Card.where(q=f'set.name:"{set.get("name")}" supertype:pokemon')
        
        for card in cards:
            if card.tcgplayer is None:
                continue

            tcg_player = card.tcgplayer
            tcg_player_prices = tcg_player.prices
            if tcg_player_prices is None:
                continue

            for price_type in ['normal', 'holofoil', 'reverseHolofoil']:
                if getattr(tcg_player_prices, price_type):
                    tcg_player_market = getattr(tcg_player_prices, price_type).market
                    tcg_player_high = getattr(tcg_player_prices, price_type).high
                    break
            else:
                continue

            if tcg_player_market is not None and tcg_player_market > 20:
                pricecharting_url = generate_pricecharting_url(card.name, card.number, set.get("name"))
                extracted_prices = return_graded_prices(pricecharting_url)

                full_set_dicts[set.get("name")]["cards"].append({
                    "name": card.name,
                    "market": tcg_player_market,
                    "price_high": tcg_player_high,
                    "printed_total": card.set.printedTotal,
                    "number": card.number,
                    "card_link": tcg_player.url,
                    "pricecharting_url": pricecharting_url,
                    "graded_prices": extracted_prices,
                })
                time.sleep(random.randint(0, 3))
            else:
                continue

    return full_set_dicts

if __name__ == "__main__":
    cards_info = generate_tcgplayer_json()

    cards_info["Terestal Festival"] = TERESTAL_FESTIVAL
    for card in cards_info["Terestal Festival"]["cards"]:
        pricecharting_url = generate_pricecharting_url(card.get("name"), card.get("number"), "Terestal Festival")
        extracted_prices = return_graded_prices(pricecharting_url)
        card["pricecharting_url"] = pricecharting_url
        card["graded_prices"] = extracted_prices

    with open('tcgplayer_cards_info.py', 'w') as f:
        f.write('cards_info = ' + json.dumps(cards_info, indent=4) + '\n')