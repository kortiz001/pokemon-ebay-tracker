import datetime
import requests
from pokemontcgsdk import Card, Set, RestClient

# Configure RestClient with your API key
RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')
API_TOKEN = "v^1.1#i^1#f^0#I^3#p^1#r^0#t^H4sIAAAAAAAAAOVYW2wUVRju9ipCMUSDSECXARItmdkzs5fZHdvFbdfalaUt3bZiI+DZmTPtsHPLnLO0642VcIkPGmJJCYmBptIHEXghCmokqQ8KidEYNRUJhCAxNT54iYSQADqzXcq2Em7dxCbuy2b+/z//+b7v/P85ZwZkK2fVbG/afqnaVVU6mAXZUpeLnQ1mVVasmFtWurCiBBQEuAazy7LlW8rGajHUVFNoQ9g0dIzcfZqqYyFnrKPSli4YECtY0KGGsEBEIRFZHRc4BgimZRBDNFTKHYvWUVwwyHkDfp8sAhkE/bZRv56y3bDdoj/IIREEOOgNsUne9mOcRjEdE6gT2w84Pw04GvDtgBM4XvDxDAsCXZS7E1lYMXQ7hAFUOIdWyI21CqDeGinEGFnETkKFY5HGREskFn26ub3WU5ArnJchQSBJ48lPDYaE3J1QTaNbT4Nz0UIiLYoIY8oTHp9hclIhch3MPcDPKe3jQsGA6JOgTwzyLPQWRcpGw9IguTUOx6JItJwLFZBOFJK5naK2GsmNSCT5p2Y7RSzqdv7WpKGqyAqy6qin6yPPR1pbqfAqtEnRWyxCm0YKaYZOt7ZFaVbi7IoBEksHAghxQT6Yn2c8WV7lKRM1GLqkOJphd7NB6pENGk2Vhi2Qxg5qsWeOyMQBVBjny0sIQqEuZ03HFzFNenRnWZFm6+DOPd5+ASZGE2IpyTRBExmmOnIK1VHQNBWJmurMlWK+evpwHdVDiCl4PL29vUyvlzGsbg8HAOtZuzqeEHuQBqlcrNPrTrxy+wG0kqMiInskVgSSMW0sfXap2gD0birsZ308H8rrPhlWeKr1X4YCzp7JDVGsBoGQ42QuZP8FOT4ZKMpeE87XqMfBgZIwQ2vQSiFiqlBEtGjXWVpDliIJXr/MeYMyoqVASKZ9IVmmk34pQLMyQgChZFIMBf9HfXKnlZ5AooVIkUq9SGWeSTUmGuKrNBTtaNCilhYF8URc61Q9nma4EWqdG8lapR7GQ3Lr6ro7bYabkm9QFVuZdnv+mdfrTQYmSJoWvYRomKjVUBUxM7MW2GtJrdAimQRSVdswLZIR04wVa6suEr272yXujXYxT6j/5HS6KSvsVOzMYuWMx3YCaCqMc/4woqF5DJgmTq/3OOYNOdTT4q3Y19YZxdomOc5Wkcbvm4xDuYfBm0TGQthIW/ZVm2lx7l/tdpHr9nFGLENVkdXJTrudNS1NYFJFM62vi1DgCpxhZy3Le4PBkJ8L8NPiJeZO0g0zbUsq1k5cXn/3d2rP5Pf7cEnux25xfQa2uI6XulygFixnl4IllWUd5WVzFmKFIEaBMoOVbt1+b7UQk0IZEypW6YMlX8+NS683xS9mk+mjz/21MlhSXfB5YXAdWDDxgWFWGTu74GsDWHTDU8E+8HA15wcc4AHH8T6+Cyy94S1n55c/lOq/7+x7rz6RHfrhtROXO0a3fmBm5oLqiSCXq6KkfIurpOZkVM4K7uH43if5vvWRZWeOumHX+vKtg1dPeg/vP3uBPip984lmrXlm26Id+j78bjT07blz95vfrTnyQmTk0aGX+6tiv51quuL9g5n31uILO2sWXepeG519/sBIYsW2Z09UjnZ8utdaLysH36kl3w+N/di/5+Ohg759py+jM5L80pIdb5/+vX7elYGRU0d+Oj5wuHGg3dN/sW3O+1WPtG3G12D/sHvYTP098FHkFR+1bNeBHWNV+xZvW/d464Vdx748dP7q7qf2x7qax06u+3XPV/OzlTWpQz0d2s43tT2jbyz/fEGH+vNI5MVU9Bj+cPNjVxrrSprOl/4pjo5+Ed81AiO7Vx7/Zf+14fG1/Ac36IH0+BEAAA=="

def fetch_pokemon_cards():
    query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=20)).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

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
