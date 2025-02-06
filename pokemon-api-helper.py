import datetime
import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import RestClient

RestClient.configure('102d86ed-ff3b-44ce-8278-7d0c72c037a4')
API_TOKEN = "v^1.1#i^1#I^3#f^0#r^0#p^1#t^H4sIAAAAAAAAAOVYW2wUVRjutluQSwGjEa0lWQcQUGfmzOzOXkZ2YelyWdheYNsFGgvM5Uw7dG7MOUvZELWtKSRcAgmoD0asMV5CAviAMWqCyi0aSUAwGC8hog/wgheEqNEEZ7albCsBpJu4ifuyOf/5z3++7zv/f86ZA7pGjXls06JNv1V5Rpf3dYGuco+HGQfGjKp8fEJFeXVlGShw8PR1Tevy9lRcnI0EXbP4ZRBZpoGgb4OuGYjPG6NE1jZ4U0Aq4g1Bh4jHEp+O16V4lgK8ZZvYlEyN8CUTUSIkilCU/IoMQ2wgFAk6VuN6zCYzSoh+ISTLrKgIoVAgIDJOP0JZmDQQFgwcJVjAciRgSRBsAhzvj/AMR7FspIXwZaCNVNNwXChAxPJw+fxYuwDrraEKCEEbO0GIWDK+IN0QTybm1zfNpgtixQZ0SGMBZ9HQVq0pQ19G0LLw1tOgvDefzkoSRIigY/0zDA3Kx6+DuQv4eakVMcT6gxxQpAgMMiJXFCkXmLYu4FvjcC2qTCp5Vx4aWMW52ynqqCGuhRIeaNU7IZIJn/u3NCtoqqJCO0rMnxdfGW9sJGJL4HrVaLAxaZkdUDcNsnFZgmRkNsKIQGbIYBBCNhwKD8zTH2xA5WET1ZqGrLqaIV+9iedBBzQcLg1bII3j1ODMHFewC6jQL3RdQsC1uGvav4hZ3G64ywp1Rwdfvnn7BRgcjbGtilkMByMM78grFCUEy1JlYnhnPhUHsmcDihLtGFs8TXd2dlKdfsq022gWAIZeUZdKS+1QFwjX1631vL96+wGkmqciQWckUnmcsxwsG5xUdQAYbUSMYwKhUGRA96GwYsOt/zAUcKaHFkSxCiQgsqyfDQelCKeAgL8oe01sIEdpFwcUhRypC3YHxJYmSJCUnDzL6tBWZd7PKaw/rEBSDkYUMhBRFFLk5CDJKBACCEVRioT/R3Vyp5mehpINcXFSvVhpnutYkK5NLdFhorlWT9h6AqTSKT2j0XS9sFbQM2vxCnWekIoojXXROy2Gm5Kv1VRHmSZn/tKr9UUmwlAeEb20ZFqw0dRUKVdaC+y35UbBxrk01DTHMCKScctKFmmrLha9f7dL3B3tIp5Q/83pdFNWyM3Y0mLljkdOAMFSKff8oSRTp00h69Y6bnfNq/OoR8Rbda6tJcXaIdnPVpX775uUQxm3U2i9RNkQmVnbuWpTDe79q8lJcsM5zrBtahq0M8yIy1nXs1gQNVhqdV2EBFeFEjtrmZA/HGaBn+NGxEvKn6SrS21LKtJO7K29izs1PfQDP1aW/zE9nsOgx3Oo3OMBs8F0Zip4ZFRFs7difDVSMaRUQaGQ2mY43602pDpgzhJUu/y+spMTUnL3otTVLjH77vIrc8JlVQXvC32t4MHBF4YxFcy4gucGUHOjp5KZOLmK5QALgoDzRxiuBUy90etlHvDer/rPXdsfPdrcO/1EzYzJh1uXXkRzQNWgk8dTWebt8ZRVb1zXzELfStCCtn3XbYq7zCeOKq/3jL28NPzrB1d3HbwyWVv4pfXUmYWvVf7V+nDPO+eT63qe2b4v+tHFI9+MXd4+aa+n07fz61WLL1+L7uO2nVy4bvOUT3o/+3BG94rWjeb0s4vb6JpZz7fN1Y7/Lp/b0nTg+O466pfR1ld7j+Xs6Fm4/96XXm47/2ndmu3HTx/7IVDd/Wzi6se1O7a+dyGMfzqwmd//xo9bd6cDc6xLb+488WTd6blPq++/OGlmnPyz6duKe/Z8saf30W3BDu/3r6T61vx8fpVwiJry6qm3Xzj4x7nejmkPZZ4L0mNrjoiLN546kml+axamTm22guqk8fTMSxNTzJns5xe29K/l392WGNv5EQAA"

query_end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

sets = [
    {"name": "Obsidian Flames", "code": "sv3"},
    {"name": "151", "code": "sv3pt5"},
    {"name": "Temporal Forces", "code": "sv5"},
    {"name": "Paldea Evolved", "code": "sv2"},
    {"name": "Crown Zenith Galarian Gallery", "code": "swsh12pt5gg"},
    {"name": "Evolving Skies", "code": "swsh7"},
    {"name": "Crown Zenith", "code": "swsh12pt5"},
    {"name": "Surging Sparks", "code": "sv8"},
    {"name": "Prismatic Evolutions", "code": "sv8pt5"}
]

for set in sets:
    set_object = Set.find(set.get("code"))
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
                        f"price:[0..{tcg_player_market * 0.8:.2f}]",
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
                            headers = {
                                "Authorization": "Bearer " + API_TOKEN,
                                "Content-Type": "application/json"
                            }
                            response = requests.get(url, headers=headers, params=params)
                            if response.status_code == 200:
                                response = response.json()

                                if response.get("seller").get("feedbackPercentage") == "0.0":
                                    continue

                                end_time = datetime.datetime.strptime(response.get("itemEndDate"), '%Y-%m-%dT%H:%M:%S.%fZ')
                                end_time = end_time.replace(tzinfo=datetime.timezone.utc)
                                time_left = (end_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
                                minutes, seconds = divmod(time_left, 60)

                                print(f"Card Name: {card.name}, View Item URL: {response['itemWebUrl']}, Time Left: {int(minutes)} minutes {int(seconds)} seconds")
                                print(f"Current Bid Price: ${response["currentBidPrice"]["value"]}, Market Value: ${tcg_player_market}\n")
                else:
                    print(f"Error: {response.status_code}")
                    print(response.text)

            except requests.exceptions.RequestException as e:
                print(e)