import json
import random
import requests
import time
import sys
from pokemontcgsdk import Card, RestClient
from bs4 import BeautifulSoup

# Configure RestClient with your API key
RestClient.configure('39270b46-5e88-40cd-baa3-b09d088bebcd')

# -------------------------------
# Helper: Retry requests with exponential backoff
# -------------------------------
def get_with_retry(url, retries=5, backoff_factor=2):
    for i in range(retries):
        try:
            response = requests.get(url, timeout=10)  # 10s timeout
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            wait_time = backoff_factor ** i + random.uniform(0, 1)
            print(f"[Retry {i + 1}/{retries}] Error fetching {url}: {e}. Retrying in {wait_time:.2f}s")
            time.sleep(wait_time)
    print(f"[FAILED] Max retries exceeded for {url}")
    return None

# -------------------------------
# Helper: Generate PriceCharting URL
# -------------------------------
def generate_pricecharting_url(card_name, card_number, set_name):
    full_set_name = f"pokemon-{set_name.lower().replace(' ', '-')}"
    if set_name == "151":
        full_set_name = "pokemon-scarlet-&-violet-151"

    base_url = f"https://pricecharting.com/game/{full_set_name}/{card_name.lower().replace(' ', '-')}-{card_number}"
    return base_url

# -------------------------------
# Helper: Scrape PriceCharting graded prices
# -------------------------------
def return_graded_prices(pricecharting_url):
    default_prices = {
        "ungraded": "N/A",
        "grade7": "N/A",
        "grade8": "N/A",
        "grade9": "N/A",
        "grade95": "N/A",
        "grade10": "N/A"
    }

    response = get_with_retry(pricecharting_url)
    if not response:
        return default_prices

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        prices = {
            'ungraded': soup.find('td', {'id': 'used_price'}),
            'grade7': soup.find('td', {'id': 'complete_price'}),
            'grade8': soup.find('td', {'id': 'new_price'}),
            'grade9': soup.find('td', {'id': 'graded_price'}),
            'grade95': soup.find('td', {'id': 'box_only_price'}),
            'grade10': soup.find('td', {'id': 'manual_only_price'})
        }

        extracted_prices = {}
        for grade, td in prices.items():
            extracted_prices[grade] = td.find('span', {'class': 'price'}).text.strip() if td and td.find('span', {'class': 'price'}) else "N/A"

        return extracted_prices
    except Exception as e:
        print(f"[Error] Failed to parse graded prices from {pricecharting_url}: {e}")
        return default_prices

# -------------------------------
# Main Card Fetching Logic
# -------------------------------
def generate_tcgplayer_json(set: dict):
    full_set_dicts = {
        set.get("name"): {
            "code": set.get("code"),
            "cards": []
        }
    }

    # Retry logic for fetching cards from TCG API
    max_retries = 5
    cards = []
    for attempt in range(max_retries):
        try:
            print(f"Fetching cards for set: {set.get('name')} (Attempt {attempt + 1}/{max_retries})")
            cards = Card.where(q=f'set.name:"{set.get("name")}" supertype:pokemon')
            break
        except Exception as e:
            err_str = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"[Retry {attempt + 1}] Failed to fetch cards: {err_str}")
            time.sleep(2 ** attempt + random.uniform(0, 1))  # exponential backoff
    else:
        print(f"[FATAL] Giving up on set: {set.get('name')} after {max_retries} attempts.")
        return full_set_dicts

    for card in cards:
        try:
            print(f"Processing: {card.name} - #{card.number} ({set.get('name')})")

            if not card.tcgplayer or not card.tcgplayer.prices:
                continue

            tcg_player_prices = card.tcgplayer.prices

            # Find first available price type
            tcg_player_market = None
            tcg_player_high = None
            for price_type in ['normal', 'holofoil', 'reverseHolofoil']:
                if getattr(tcg_player_prices, price_type):
                    tcg_player_market = getattr(tcg_player_prices, price_type).market
                    tcg_player_high = getattr(tcg_player_prices, price_type).high
                    break
            if tcg_player_market is None or tcg_player_market <= 80:
                continue

            # Fetch PriceCharting data
            pricecharting_url = generate_pricecharting_url(card.name, card.number, set.get("name"))
            extracted_prices = return_graded_prices(pricecharting_url)

            # Check if it's worth considering based on grade10 price
            grade10_str = extracted_prices.get("grade10", "N/A").replace("$", "").replace(",", "")
            if grade10_str == "N/A":
                continue
            try:
                grade10_value = float(grade10_str)
                if (grade10_value * 0.4) <= tcg_player_market:
                    continue
            except ValueError:
                continue

            card_image_url = card.images.large
            full_set_dicts[set.get("name")]["cards"].append({
                "name": card.name,
                "market": tcg_player_market,
                "price_high": tcg_player_high,
                "printed_total": card.set.printedTotal,
                "number": card.number,
                "card_link": card.tcgplayer.url,
                "pricecharting_url": pricecharting_url,
                "graded_prices": extracted_prices,
                "image_url": card_image_url
            })

            # Throttle to avoid hitting rate limits
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"[Error] Skipping card due to error: {e}")
            continue

    return full_set_dicts

# -------------------------------
# Runner
# -------------------------------
if __name__ == "__main__":
    set_name = sys.argv[0]

    sets = {
        "Sword & Shield": "swsh1",
        "Rebel Clash": "swsh2",
        "Darkness Ablaze": "swsh3",
        "Champion's Path": "swsh35",
        "Vivid Voltage": "swsh4",
        "Shining Fates": "swsh45",
        "Battle Styles": "swsh5",
        "Chilling Reign": "swsh6",
        "Evolving Skies": "swsh7",
        "Fusion Strike": "swsh8",
        "Brilliant Stars": "swsh9",
        "Astral Radiance": "swsh10",
        "Lost Origin": "swsh11",
        "Silver Tempest": "swsh12",
        "Paradox Rift": "sv4",
        "Paldean Fates": "sv4pt5",
        "Twilight Masquerade": "sv6",
        "Obsidian Flames": "sv3",
        "151": "sv3pt5",
        "Paldea Evolved": "sv2",
        "Crown Zenith Galarian Gallery": "swsh12pt5gg",
        "Crown Zenith": "swsh12pt5",
        "Surging Sparks": "sv8",
        "Prismatic Evolutions": "sv8pt5",
        "Journey Together": "sv9",
        "Destined Rivals": "sv10",
        "Black Bolt": "zsv10pt5",
        "White Flare": "rsv10pt5"
    }

    set = sets.get(set_name)
    set = {"name": set_name, "code": set}

    print(f"\n=== Processing Set: {set['name']} ===")
    cards_info = generate_tcgplayer_json(set=set)
    output_filename = f'psa_results/tcgplayer_cards_info_{set.get("name").replace(" ", "_").replace("&", "and")}.py'
    with open(output_filename, 'w') as f:
        f.write('cards_info = ' + json.dumps(cards_info, indent=4) + '\n')
    print(f"✅ Saved: {output_filename}")