import json
from pokemontcgsdk import Card, Set, RestClient

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')

def generate_tcgplayer_json():
    sets = [
        {"name": "Base Set", "code": "base1"},
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
            for price_type in ['normal', 'holofoil', 'reverse_holofoil']:
                if getattr(tcg_player_prices, price_type):
                    tcg_player_market = getattr(tcg_player_prices, price_type).market
                    tcg_player_high = getattr(tcg_player_prices, price_type).high
                    break
            else:
                continue

            if tcg_player_market > 20:
                full_set_dicts[set.get("name")]["cards"].append({
                    "name": card.name,
                    "market": tcg_player_market,
                    "price_high": tcg_player_high,
                    "printed_total": card.set.printedTotal,
                    "number": card.number,
                    "card_link": tcg_player.url
                })

    return full_set_dicts

if __name__ == "__main__":
    cards_info = generate_tcgplayer_json()

    with open('tcgplayer_cards_info.py', 'w') as f:
        f.write('cards_info = ' + json.dumps(cards_info) + '\n')