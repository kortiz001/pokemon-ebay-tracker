import datetime
import requests
from pokemontcgsdk import Card, Set, RestClient

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')
API_TOKEN = "v^1.1#i^1#p^1#f^0#I^3#r^0#t^H4sIAAAAAAAAAOVYC2wURRi+uz6wgSsEEbGCXLfiA9292Xvf0ju89lp79Nqe3FFpI8I+ZunS20d251pqIpQjQaIxGGOi8UFQoqAhkhijYoIkCIFAgoFIjDEqQREM+ADkEeXh7PUo10oA6SU2cXPJZf7555/v++b/Z2YX9JdXzFzVtOqc3TrGtq4f9NusVnosqCgve6iyxFZVZgEFDtZ1/ff2l2ZLjtUarJzWmLnQ0FTFgI6lcloxmJwxRGR0hVFZQzIYhZWhwSCeSUZa4oyLAoymq0jl1TThiEVDhB9C2uv2eL0+P6QDPoitypWYKTVE+EQvzwbcbjrg9kOPEMT9hpGBMcVArIJChAu4vCRwkcCfomkG/zw+KugOdhKOdqgbkqpgFwoQ4RxcJjdWL8B6faisYUAd4SBEOBZpTLZFYtGG1lStsyBWOK9DErEoYwxt1asCdLSz6Qy8/jRGzptJZngeGgbhDA/MMDQoE7kC5hbg56T2cRzrgSznFQKc1+cFRZGyUdVlFl0fh2mRBFLMuTJQQRLqu5GiWA1uCeRRvtWKQ8SiDvPvsQyblkQJ6iGioS7SEUkkiHAz7JGUNh2RmtoNZVUhE3OjJC24gjQHBJr0+SB0BfyB/DwDwfIqD5uoXlUEydTMcLSqqA5i0HC4NKBAGuzUhmeOiMgEVOjnHpTQ3Wmu6cAiZlCXYi4rlLEOjlzzxgswOBohXeIyCA5GGN6RUyhEsJomCcTwzlwq5rNnqREiuhDSGKezt7eX6nVTqr7Y6QKAds5viSf5LiizhOlr1nrOX7rxAFLKUeFxFWN/BvVpGMtSnKoYgLKYCHtpj98fzOs+FFZ4uPUfhgLOzqEFUawCcQXYIEcHaLdLACIUYDEKJJzPUaeJA3JsHymzejdEWprlIcnjPMvIUJcExu0VXe6ACEnBFxRJT1AUSVypPpIWIQQQchwfDPyP6uRmMz0JeR2i4qR6sdK8r7sxWR9vlmF0Xr0c1eUoiCfjcnva6Wxll7By+xI0X6pj40Ex0RK62WK4Jvn6tISVSeH5R1+tN6kGgsKI6CV5VYMJNS3xfaNrgd26kGB11JeE6TQ2jIhkRNNiRdqqi0Xv3+0St0a7iCfUf3M6XZOVYWbs6GJljjdwAFaTKPP8oXhVdqpsxqx11GWaF+ZQj4i3hK+to4o1JjnAVhIG7psUpoy6KKOHp3RoqBkdX7WpNvP+lcJJruDjDOlqOg31dnrE5SzLGcRyaTja6roICS6xo+yspf3uQNDl8wPfiHjxuZN04Wjbkoq0E5fW38Kd2jn0BT9syT101rodZK2f2axWUAtm0DWgurxkXmnJuCpDQpCSWJEypMUKfm/VIdUN+zRW0m23W76ojAsrmuJn+rnMx4//MTtgsRd8X1i3AEwZ/MJQUUKPLfjcAKZe7Smjx99pd3mBC/hp/Hh8naDmam8pPbl00sxNP9zduyOYWDn7Tdv64962hj0v1gD7oJPVWmYpzVotyy+vvmff/L3chqMvrYmAjuysXW0vTxMnf7Jz4rbkuTlVYxJBMdmw8eKzVOTs3q0bHt18fDd/6ceSX05s+/Su9e29jTH7qXGWCbe9esC+p3JZy8qthyqzn49NPbL68KTqCe+Uf7BC+7B2wevTfju97MhbE95/b0vnMxXJ30/WJGKt3zXu+qnijp4p+/+8fFo6uOPgU/dR9cs3eHafOPPrjGwjuW86b+GOXtj+/BbLc+O/meIrecA+fdOB/UbPa7PPbTz8pda0/9LTuzqeVOoeji46duTiya92fDTRf+H+tdVTO16ZRa9ZtOjtJzKbv21uDp6veeGSf2Xq3Ulf78yeP8vUvTGPr5pz6Hvbgz+Ta0/9NbNqYC3/BvexTbf5EQAA"

def fetch_pokemon_cards():
    query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

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
                            f"price:[0..{tcg_player_market * 0.80:.2f}]",
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
