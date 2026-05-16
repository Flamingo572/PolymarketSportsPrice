import requests
import json

def findIdsBySlug(slug):
    # Fetch markets from the CLOB (Central Limit Order Book)
    url = f"https://gamma-api.polymarket.com/markets/slug/{slug}"
    markets = requests.get(url).json()

    if(markets.get('type', "") != ""):
        return findEventsBySlug(slug)
        

    else:   
        # print(markets)
        # print(markets['clobTokenIds'])
        # print(markets['gameId'])
        # print(markets['outcomes'])
        return markets['gameId'], markets['clobTokenIds'], markets['outcomes']

def findSportByID():
    series = "10754"
    url = f"https://gamma-api.polymarket.com/events?series_id={series}&active=true&closed=false"
    markets = requests.get(url).json
    print(markets)

def findSportsTags():
    """Finds all active matches containing your keyword (e.g., 'Atletico')"""
    markets = requests.get("https://gamma-api.polymarket.com/markets?sports_market_types=moneyline&closed=false&active=true").json()
    for m in markets:
        print(f"Game: {m['question']}\nToken ID: {m["clobTokenIds"]}\nDate: {m['startDate']}")

def findEventsBySlug(slug):
    url = f"https://gamma-api.polymarket.com/events/slug/{slug}"
    markets = requests.get(url).json()
    allMarkets = markets.get('markets')

    return markets.get('gameId'), allMarkets[0].get('clobTokenIds'), allMarkets[0].get('outcomes')


