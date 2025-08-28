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

def generate_tcgplayer_json(set: dict):
    full_set_dicts = {}
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

        if tcg_player_market is not None and tcg_player_market > 80:
            pricecharting_url = generate_pricecharting_url(card.name, card.number, set.get("name"))
            extracted_prices = return_graded_prices(pricecharting_url)

            if not (float(extracted_prices.get("grade10").replace("$", "").replace(",", "")) * 0.4) > tcg_player_market:
                continue

            card_image_object = card.images
            card_image_url = card_image_object.large
            full_set_dicts[set.get("name")]["cards"].append({
                "name": card.name,
                "market": tcg_player_market,
                "price_high": tcg_player_high,
                "printed_total": card.set.printedTotal,
                "number": card.number,
                "card_link": tcg_player.url,
                "pricecharting_url": pricecharting_url,
                "graded_prices": extracted_prices,
                "image_url": card_image_url
            })
            time.sleep(random.randint(0, 3))
        else:
            continue

    return full_set_dicts

if __name__ == "__main__":
    sets = [
        {"name": "Sun & Moon", "code": "sm1"},
        {"name": "Guardians Rising", "code": "sm2"},
        {"name": "Burning Shadows", "code": "sm3"},
        {"name": "Crimson Invasion", "code": "sm4"},
        {"name": "Ultra Prism", "code": "sm5"},
        {"name": "Forbidden Light", "code": "sm6"},
        {"name": "Celestial Storm", "code": "sm7"},
        {"name": "Lost Thunder", "code": "sm8"},
        {"name": "Team Up", "code": "sm9"},
        {"name": "Unbroken Bonds", "code": "sm10"},
        {"name": "Unified Minds", "code": "sm11"},
        {"name": "Cosmic Eclipse", "code": "sm12"},
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
        {"name": "Prismatic Evolutions", "code": "sv8pt5"},
        {"name": "Journey Together", "code": "sv9"},
        {"name": "Destined Rivals", "code": "sv10"},
        {"name": "Black Bolt", "code": "zsv10pt5"},
        {"name": "White Flare", "code": "rsv10pt5"}
    ]

    full_set_dict = {}
    for set in sets:
        # cards_info = generate_tcgplayer_json(set=set)
        # full_set_dict[set.get("name")] = cards_info
        # with open(f'tcgplayer_cards_info_{set.get("name")}.py', 'w') as f:
        #     f.write('cards_info = ' + json.dumps(cards_info, indent=4) + '\n')
        with open(f'tcgplayer_cards_info_{set.get("name")}.py', 'r') as f:
            set_dict = json.loads(f.read().split("cards_info = ")[1])
            full_set_dict[set.get("name")] = set_dict.get(set.get("name"))

    with open(f'tcgplayer_cards_info_psa_check.py', 'w') as f:
        f.write('cards_info = ' + json.dumps(full_set_dict, indent=4) + '\n')