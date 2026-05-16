import requests
import json

def get_active_sports_ids():
    id = "0x438e385073ec0110f6d632814a22ffec4b235dbab7467b8057e9ce82110284fc"
    url = f"https://gamma-api.polymarket.com/events/{id}"
    
    # THESE ARE THE CRITICAL FILTERS
    params = {
        "active": "true",        # Must be currently active
        "closed": "false",       # Must not be finished
        "tag_id": "100639",      # 100639 is the Tag ID for 'Sports'
        "limit": 100             # Just get the top 10 for now
    }

    response = requests.get(url).json()
    print(response)
    if not response:
        print("No active sports markets found. Check your VPN/Proxy.")
        return

    for market in response:
        question = market.get('question')
        # Remember: clobTokenIds is a string that looks like a list
        token_ids = json.loads(market.get('clobTokenIds', '[]'))
        outcomes = json.loads(market.get('outcomes', '[]'))

        print(f"MATCH: {question}")
        if token_ids and outcomes:
            print(f"  -> {outcomes[0]} ID: {token_ids[0]}")
            print(f"  -> {outcomes[1]} ID: {token_ids[1]}")
        print("-" * 30)

if __name__ == "__main__":
    get_active_sports_ids()