import json
import pprint
import os
import random
import requests
import time
import sys
from bs4 import BeautifulSoup

TCGDEX_BASE = "https://api.tcgdex.net/v2/en"
POKEWALLET_BASE = "https://api.pokewallet.io"
POKEWALLET_API_KEY = os.environ.get(
    "POKEWALLET_API_KEY", "pk_live_409d09208df8d373418919fae0b9060c9169082da88cca22"
)

# Mapping from our set names to PokeWallet set codes
POKEWALLET_SET_CODES = {
    "Sword & Shield": "SWSH01",
    "Rebel Clash": "SWSH02",
    "Darkness Ablaze": "SWSH03",
    "Champion's Path": "CHP",
    "Vivid Voltage": "SWSH04",
    "Shining Fates": "SHF",
    "Battle Styles": "SWSH05",
    "Chilling Reign": "SWSH06",
    "Evolving Skies": "SWSH07",
    "Fusion Strike": "SWSH08",
    "Brilliant Stars": "SWSH09",
    "Astral Radiance": "SWSH10",
    "Lost Origin": "SWSH11",
    "Silver Tempest": "SWSH12",
    "Crown Zenith": "CRZ",
    "Paradox Rift": "PAR",
    "Paldean Fates": "PAF",
    "Twilight Masquerade": "TWM",
    "Obsidian Flames": "OBF",
    "151": "MEW",
    "Paldea Evolved": "PAL",
    "Surging Sparks": "SSP",
    "Prismatic Evolutions": "PRE",
    "Journey Together": "JTG",
    "Destined Rivals": "DRI",
    "Black Bolt": "BLK",
    "White Flare": "WHT",
    "Mega Evolution": "MEG",
    "Phantasmal Flames": "PFL",
    "Sun & Moon": "SM01",
    "Guardians Rising": "SM02",
    "Burning Shadows": "SM03",
    "Shining Legends": "SHL",
    "Crimson Invasion": "SM04",
    "Ultra Prism": "SM05",
    "Forbidden Light": "SM06",
    "Celestial Storm": "CES",
    "Dragon Majesty": "DRM",
    "Lost Thunder": "SM8",
    "Team Up": "SM9",
    "Unbroken Bonds": "SM10",
    "Unified Minds": "SM11",
    "Hidden Fates": "HIF",
    "Cosmic Eclipse": "SM12",
}

# Fetch live EUR to USD conversion rate
def get_eur_to_usd():
    try:
        resp = requests.get("https://api.exchangerate-api.com/v4/latest/EUR", timeout=10)
        rate = resp.json()["rates"]["USD"]
        print(f"EUR to USD rate: {rate}")
        return rate
    except Exception as e:
        print(f"[Warning] Failed to fetch EUR/USD rate, using fallback 1.04: {e}")
        return 1.04

EUR_TO_USD = get_eur_to_usd()

# -------------------------------
# Helper: Retry requests with exponential backoff
# -------------------------------
def get_with_retry(url, retries=5, wait_time=30, headers=None):
    for i in range(retries):
        try:
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"[Retry {i + 1}/{retries}] Error fetching {url}: {e}. Retrying in {wait_time}s")
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
        print(f"[PriceCharting] No response from {pricecharting_url}")
        return default_prices

    try:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Detect Cloudflare challenge or blocked response
        title = soup.find('title')
        title_text = title.text.strip() if title else ""
        if "just a moment" in title_text.lower() or "attention required" in title_text.lower():
            print(f"[PriceCharting] BLOCKED by Cloudflare for {pricecharting_url}")
            return default_prices

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

        if all(v == "N/A" for v in extracted_prices.values()):
            print(f"[PriceCharting] All prices returned N/A for {pricecharting_url}")

        return extracted_prices
    except Exception as e:
        print(f"[Error] Failed to parse graded prices from {pricecharting_url}: {e}")
        return default_prices

# -------------------------------
# Helper: Fetch all cards in a set from TCGdex
# -------------------------------
def fetch_set_cards(set_code):
    url = f"{TCGDEX_BASE}/sets/{set_code}"
    response = get_with_retry(url)
    if not response:
        return [], 0

    data = response.json()
    cards = data.get("cards", [])
    printed_total = data.get("cardCount", {}).get("official", 0)
    return cards, printed_total

# -------------------------------
# Helper: Fetch single card details from TCGdex
# -------------------------------
def fetch_card_details(card_id):
    url = f"{TCGDEX_BASE}/cards/{card_id}"
    response = get_with_retry(url, retries=3, wait_time=5)
    if not response:
        return None
    return response.json()

# -------------------------------
# Helper: Extract market and high prices from TCGdex card data
# Uses TCGplayer (USD) if available, falls back to Cardmarket (EUR -> USD)
# -------------------------------
def extract_market_prices(card_data):
    pricing = card_data.get("pricing", {})

    # Try TCGplayer first (USD)
    tcgplayer = pricing.get("tcgplayer")
    if tcgplayer:
        for variant in ["normal", "holofoil", "reverse-holofoil"]:
            variant_data = tcgplayer.get(variant)
            if variant_data and variant_data.get("marketPrice") is not None:
                return (
                    variant_data["marketPrice"],
                    variant_data.get("productId"),
                )

    # Fall back to Cardmarket (EUR -> USD)
    cardmarket = pricing.get("cardmarket")
    if cardmarket and cardmarket.get("avg") is not None:
        avg_eur = cardmarket["avg"]
        market_usd = round(avg_eur * EUR_TO_USD, 2)
        print(f"  Using Cardmarket avg: {avg_eur} EUR -> ${market_usd} USD")
        return market_usd, None

    return None, None

# -------------------------------
# Helper: Fetch price from PokeWallet API (fallback)
# Returns (market_price, tcgplayer_url) or (None, None)
# -------------------------------
def fetch_pokewallet_price(card_name, card_number, set_name):
    pw_set_code = POKEWALLET_SET_CODES.get(set_name)
    if not pw_set_code:
        print(f"  [PokeWallet] No set code mapping for {set_name}")
        return None, None

    headers = {"X-API-Key": POKEWALLET_API_KEY}

    # Search by card name + number to find the right card
    query = f"{card_name} {card_number}"
    url = f"{POKEWALLET_BASE}/search?q={requests.utils.quote(query)}&limit=10"

    try:
        response = get_with_retry(url, retries=3, wait_time=5, headers=headers)
        if not response:
            return None, None

        data = response.json()
        results = data.get("results", [])

        for result in results:
            card_info = result.get("card_info", {})
            result_set_code = card_info.get("set_code", "")
            result_number = card_info.get("card_number", "")

            # Match by pokewallet set code (set_code field is the set_id number as string)
            # Also match by card number
            # The card_number format from pokewallet is like "161/131"
            # Our card_number from TCGdex is like "161"
            number_match = (
                result_number == card_number
                or result_number.startswith(f"{card_number}/")
            )

            if not number_match:
                continue

            # Check TCGplayer prices
            tcg = result.get("tcgplayer", {})
            tcg_prices = tcg.get("prices", {})
            if isinstance(tcg_prices, dict):
                market_price = tcg_prices.get("market_price")
                tcg_url = tcg.get("url", "")
                if market_price is not None:
                    print(f"  [PokeWallet] Found TCGplayer price: ${market_price}")
                    return market_price, tcg_url

            # Check Cardmarket prices as fallback
            cm = result.get("cardmarket", {})
            if cm:
                cm_prices = cm.get("prices", [])
                for variant in cm_prices:
                    if variant.get("variant_type") == "normal" and variant.get("avg") is not None:
                        avg_eur = variant["avg"]
                        market_usd = round(avg_eur * EUR_TO_USD, 2)
                        print(f"  [PokeWallet] Using Cardmarket avg: {avg_eur} EUR -> ${market_usd} USD")
                        cm_url = cm.get("product_url", "")
                        return market_usd, cm_url

        print(f"  [PokeWallet] No matching card found for {card_name} #{card_number} in {set_name}")
        return None, None

    except Exception as e:
        print(f"  [PokeWallet] Error fetching price: {e}")
        return None, None

# -------------------------------
# Main Card Fetching Logic
# -------------------------------
def generate_tcgplayer_json(set_info: dict):
    set_name = set_info.get("name")
    set_code = set_info.get("code")

    full_set_dicts = {
        set_name: {
            "code": set_code,
            "cards": []
        }
    }

    # Fetch all card IDs in the set
    max_retries = 5
    card_list = []
    printed_total = 0
    for attempt in range(max_retries):
        try:
            print(f"Fetching cards for set: {set_name} (Attempt {attempt + 1}/{max_retries})")
            card_list, printed_total = fetch_set_cards(set_code)
            if card_list:
                break
        except Exception as e:
            print(f"[Retry {attempt + 1}] Failed to fetch set: {e}")
            time.sleep(2 ** attempt + random.uniform(0, 1))
    else:
        print(f"[FATAL] Giving up on set: {set_name} after {max_retries} attempts.")
        return full_set_dicts

    print(f"Found {len(card_list)} cards in {set_name}")

    for card_stub in card_list:
        card_id = card_stub.get("id")
        card_name_stub = card_stub.get("name", "Unknown")

        try:
            print(f"Processing: {card_name_stub} - #{card_stub.get('localId')} ({set_name})")

            card_data = fetch_card_details(card_id)
            if not card_data:
                continue

            # Skip non-Pokemon cards
            if card_data.get("category") != "Pokemon":
                continue

            card_number = card_data.get("localId", "")
            card_name = card_data.get("name", card_name_stub)

            # Extract market prices from TCGdex (TCGplayer or Cardmarket)
            market_price, product_id = extract_market_prices(card_data)

            # If TCGdex has no price, fall back to PokeWallet
            tcg_url_from_pokewallet = None
            if market_price is None:
                print(f"  [TCGdex] No price available, trying PokeWallet...")
                market_price, tcg_url_from_pokewallet = fetch_pokewallet_price(
                    card_name, card_number, set_name
                )
                time.sleep(random.uniform(0.5, 1.5))  # Rate limit pokewallet

            if market_price is None or market_price <= 80:
                continue

            # Fetch PriceCharting data for graded prices
            pricecharting_url = generate_pricecharting_url(card_name, card_number, set_name)
            extracted_prices = return_graded_prices(pricecharting_url)

            # Check if it's worth considering based on grade10 price
            grade10_str = extracted_prices.get("grade10", "N/A").replace("$", "").replace(",", "")
            if grade10_str != "N/A":
                try:
                    grade10_value = float(grade10_str)
                    if (grade10_value * 0.36) <= market_price:
                        print(f"  [Skip] Grade10 profit too low: ${grade10_value} * 0.36 = ${grade10_value * 0.36:.2f} <= ${market_price}")
                        continue
                except ValueError:
                    print(f"  [Skip] Could not parse grade10 price: {grade10_str}")

            # Build card link: TCGplayer productId > PokeWallet URL > PriceCharting
            if product_id:
                card_link = f"https://www.tcgplayer.com/product/{product_id}"
            elif tcg_url_from_pokewallet:
                card_link = tcg_url_from_pokewallet
            else:
                card_link = pricecharting_url

            # Image URL from TCGdex
            card_image_url = card_data.get("image", "")
            if card_image_url:
                card_image_url += "/high.png"

            full_set_dicts[set_name]["cards"].append({
                "name": card_name,
                "market": market_price,
                "printed_total": printed_total,
                "number": card_number,
                "card_link": card_link,
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
    set_name = sys.argv[1]

    sets = {
        "Sword & Shield": "swsh1",
        "Rebel Clash": "swsh2",
        "Darkness Ablaze": "swsh3",
        "Champion's Path": "swsh3.5",
        "Vivid Voltage": "swsh4",
        "Shining Fates": "swsh4.5",
        "Battle Styles": "swsh5",
        "Chilling Reign": "swsh6",
        "Evolving Skies": "swsh7",
        "Fusion Strike": "swsh8",
        "Brilliant Stars": "swsh9",
        "Astral Radiance": "swsh10",
        "Lost Origin": "swsh11",
        "Silver Tempest": "swsh12",
        "Crown Zenith": "swsh12.5",
        "Paradox Rift": "sv04",
        "Paldean Fates": "sv04.5",
        "Twilight Masquerade": "sv06",
        "Obsidian Flames": "sv03",
        "151": "sv03.5",
        "Paldea Evolved": "sv02",
        "Surging Sparks": "sv08",
        "Prismatic Evolutions": "sv08.5",
        "Journey Together": "sv09",
        "Destined Rivals": "sv10",
        "Black Bolt": "sv10.5b",
        "White Flare": "sv10.5w",
        "Mega Evolution": "me01",
        "Phantasmal Flames": "me02",
        "Sun & Moon": "sm1",
        "Guardians Rising": "sm2",
        "Burning Shadows": "sm3",
        "Shining Legends": "sm3.5",
        "Crimson Invasion": "sm4",
        "Ultra Prism": "sm5",
        "Forbidden Light": "sm6",
        "Celestial Storm": "sm7",
        "Dragon Majesty": "sm7.5",
        "Lost Thunder": "sm8",
        "Team Up": "sm9",
        "Unbroken Bonds": "sm10",
        "Unified Minds": "sm11",
        "Hidden Fates": "sm115",
        "Cosmic Eclipse": "sm12",
    }

    set_code = sets.get(set_name)
    if not set_code:
        print(f"Unknown set: {set_name}")
        sys.exit(1)

    set_info = {"name": set_name, "code": set_code}

    print(f"\n=== Processing Set: {set_info['name']} ===")
    cards_info = generate_tcgplayer_json(set_info=set_info)

    output_dir = 'psa_results'
    os.makedirs(output_dir, exist_ok=True)

    filename_safe = set_name.replace(" ", "_").replace("&", "and")
    output_filename = f'{output_dir}/tcgplayer_cards_info_{filename_safe}.py'

    with open(output_filename, 'w') as f:
        f.write('cards_info = ' + pprint.pformat(cards_info, indent=4, width=120) + '\n')

    print(f"Saved: {output_filename}")
