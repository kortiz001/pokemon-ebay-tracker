import datetime
import requests
from pokemontcgsdk import Card, Set, RestClient

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')
API_TOKEN = "v^1.1#i^1#I^3#f^0#r^0#p^1#t^H4sIAAAAAAAAAOVYbWwURRi+a3tFUkoxfrRixXNBNODeze597N3KHbneUXpybQ+uVKh8OLc71257u3vuztIeitRCCAUDKgkiSCQQ5YeRaFRITNCkfkRBQvyBEeMHAU0M/NBEsRRCdHd7lGslgPQSL/H+XOadd955nmfed2Z2QG/5xFkbGjYMVlonlOzpBb0lVitVASaW22ZPLi2ZarOAPAfrnt4ZvWV9pb/MUaGYzrCLkJqRJRXZe8S0pLKmMUBoisTKUBVUVoIiUlnMsYlQY4ylHYDNKDKWOTlN2KORAOGnGeTjaYQ46IZcktet0pWYLXKAoBHNQBdEtIdJuv2MT+9XVQ1FJRVDCev9gPaQgCYB0wIAS1MscDm8PqqNsLciRRVkSXdxACJowmXNsUoe1utDhaqKFKwHIYLRUH2iORSNzGtqmePMixXM6ZDAEGvq6FZY5pG9FaY1dP1pVNObTWgch1SVcAaHZxgdlA1dAXML8E2p3V4fR3so6PNQfjcNCiNlvayIEF8fh2EReDJlurJIwgLO3khRXY1kJ+JwrtWkh4hG7MbfQg2mhZSAlAAxry60NBSPE8EFaJUgNSuYzMhdSJQlMr4oQlI87aeSgKdIrxch2sf4cvMMB8upPGaisCzxgqGZam+ScR3SQaOx0lB50uhOzfrMoRQ2AOX70VckZFxtxpoOL6KGOyRjWZGo62A3mzdegJHRGCtCUsNoJMLYDlOhAAEzGYEnxnaaqZjLnh41QHRgnGGdzu7ubke3yyEr7U4aAMq5pDGW4DqQCAnD16h101+48QBSMKlwSB+pCizOZnQsPXqq6gCkdiLoodwM48/pPhpWcKz1H4Y8zs7RBVG4AuFonuH5pJuHNEqBQhRIMJejTgMHSsIsKUKlC+FMGnKI5PQ800SkCDzr8qRoly+FSN7rT5FufypFJj28l6RSCAGEkknO7/sf1cnNZnoCcQrChUn1QqV5tqs+EY4tEFFkcViMKGIExBIxsTXtdDbBTii2duIlQh2M+VPxxsDNFsM1yYfTgq5Miz5/8dV6g6xixI+LXoKTMygupwUuW1wL7FL4OFRwNoHSad0wLpKhTCZaoK26UPT+3S5xa7QLeEL9N6fTNVmpRsYWFytjvKoHgBnBYZw/Dk4WnTLUjFrHHYZ5pYl6XLwF/dpaVKx1ksNsBX74vunQKeMOh7qKcyhIlTVFv2o7mo37V4ue5JJ+nGFFTqeR0kqNu5xFUcMwmUbFVtcFSHABFtlZSzEun8/HeL2ucfHizJN0ZbFtSQXaicvCt3Cndo7+wA9azB/VZx0AfdYPS6xWMAc8SE0HD5SXLi4rnTRVFTByCDDlUIV2Sf9uVZCjC2UzUFBK7rAcnxzjn2uIne9Naoce/2Ouz1KZ976wZzmoGXlhmFhKVeQ9N4Daqz02qqq6kvYAGjAA0BRwtYHpV3vLqLvL7lw789MhbVfkx9rORsIWuffSyh0zXwaVI05Wq81S1me1tPe/+NnUoUXLvlgNvTuIneXZt5969FeOqzs1MFhzX/ixk+ILb9Dx7W8O9WysWHv7lCc/vlQ92H+g/+SsvTtOzz+/++y6d4/Btz4/eKahr3/wJe+FUyeOnNl/8cvXTjLLm+8ffGV+1YFtx7TdQ5sfSc5bMKmRXXe8qrr2z637an5f+EH1Xw99d2pp1f7TP9yVLf9k7bdH31NaN+2OntvQvOto4tkBvH5v1+XXw0dXL5TZtm1Pl9oufNX128Etu+Z+c/byzE3B5wfnfq38tPGZaQ1nZmTrK7Y+8fPs96kVa3be9vDmQ5Z9y149NhDrODztsH/dfObyhHMfaS0nyuXQlr6L97zz/Yo1tXzb4UmBI1NqbNtDw2v5NyMmYZn5EQAA"

def fetch_pokemon_cards():
    query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

    sets = [
        {"name": "151", "code": "sv3pt5"},
        {"name": "Temporal Forces", "code": "sv5"},
        {"name": "Paldea Evolved", "code": "sv2"},
        {"name": "Crown Zenith Galarian Gallery", "code": "swsh12pt5gg"},
        {"name": "Evolving Skies", "code": "swsh7"},
        {"name": "Crown Zenith", "code": "swsh12pt5"},
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

            if tcg_player_market > 20:
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
                            f"price:[0..{tcg_player_market * 0.85:.2f}]",
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
