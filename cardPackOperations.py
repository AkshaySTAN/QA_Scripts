import json
import random
import requests
import tokenGeneration

# Configuration constants
API_BASE_URL = "https://stage-api.getstan.app/api"
APP_VERSION = "118"
PLATFORM = "ios"
SID = "1716878004190-33976"
TS = "undefined"


def get_headers(token, content_type="application/json"):
    return {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": content_type,
        "gaid": "",
        "AppVersion": APP_VERSION,
        "Platform": PLATFORM,
        "SID": SID,
        "TS": TS,
        "Authorization": "Bearer " + token
    }


async def run_card_pack_operations(token):
    try:
        # Get card pack details
        url_get_card_pack = f"{API_BASE_URL}/v4/store/card/packs?"
        headers = get_headers(token)
        response_get_card_pack = requests.get(url_get_card_pack, headers=headers)
        print(f"Response get_card_pack status: {response_get_card_pack.status_code}")

        await tokenGeneration.buy_coins(token)

        # Get user coins before buying card pack
        url_user_coins = f"{API_BASE_URL}/v3/user/coins"
        response_user_coins = requests.get(url_user_coins, headers=headers)
        print(f"Response user_coins status: {response_user_coins.status_code}")
        print(f"Response user_coins body: {response_user_coins.text}")

        fan_coins = response_user_coins.json()
        before_coins = fan_coins.get('money', 0)

        # Buy card pack
        url_card_packs_buy = f"{API_BASE_URL}/v1/card-packs/buy"
        card_pack_ids = [3, 2, 7]
        random_card_pack_id = random.choice(card_pack_ids)
        data_buy = {
            "cardPackId": random_card_pack_id,
            "quantity": 1,
            "isComboOffer": False,
            "gameId": "bgmi"
        }
        response_card_packs_buy = requests.post(url_card_packs_buy, headers=headers, data=json.dumps(data_buy))
        print(f"Response card_packs_buy status: {response_card_packs_buy.status_code}")
        print(f"Response card_packs_buy body: {response_card_packs_buy.text}")

        user_card_pack_ids = []
        try:
            user_card_pack_ids = response_card_packs_buy.json()
            if not isinstance(user_card_pack_ids, list):
                raise ValueError("Expected a list of user card pack IDs")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Failed to process response: {e}")

        # Open card pack
        url_pack_open = f"{API_BASE_URL}/v1/card-packs/open"
        data_open = {
            "userCardPackIds": user_card_pack_ids,
            "gameId": "bgmi"
        }
        response_pack_open = requests.post(url_pack_open, headers=headers, data=json.dumps(data_open))
        print(f"Response pack_open status: {response_pack_open.status_code}")

        # Get user coins after buying card pack
        response_user_coins = requests.get(url_user_coins, headers=headers)
        print(f"Response user_coins status: {response_user_coins.status_code}")
        print(f"Response user_coins body: {response_user_coins.text}")

        fan_coins1 = response_user_coins.json()
        after_coins = fan_coins1.get('money', 0)

        if after_coins < before_coins:
            print(f'After coins {after_coins} is less than {before_coins}')
            print('...........FanCoin got deducted..................')
        else:
            print('FanCoins not deducted???????')

        assert after_coins < before_coins
        print('.............Test case passed........')

    except requests.RequestException as e:
        print(f"An error occurred during API requests: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

