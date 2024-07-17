import json
import random
import aiomysql
import requests
import conftest
import tokenGeneration
import io
import sys

# Configuration constants
API_BASE_URL = "https://stage-api.getstan.app/api"
APP_VERSION = "120"
PLATFORM = "ios"
SID = "1719492998451-90623"
TS = "undefined"
GAID = "60fe72c8-b35f-4c99-9f2f-8ac8624acf81"

# Gift keys arrays
GIFT_KEYS_LEADERBOARD = ["headphones", "controller", "speaker", "wristWatch", "sneakers", "superBike"]
GIFT_KEYS_LEADERBOARD_PASS = ["bagpack", "pizza", "camera", "heart", "energyDrink", "shades", "skateboard"]

def get_headers(token, content_type="application/json", game_id=None):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": content_type,
        "gaid": GAID,
        "AppVersion": APP_VERSION,
        "Platform": PLATFORM,
        "SID": SID,
        "TS": TS,
        "Authorization": "Bearer " + token
    }
    if game_id:
        headers["gameId"] = game_id
    return headers

async def send_club_gift(token, data):
    try:
        url_club_gift_send = f"{API_BASE_URL}/v4/club-gift/send"
        headers = get_headers(token)

        print(f"Sending request to {url_club_gift_send} with headers {headers} and data {data}")
        response = requests.post(url_club_gift_send, headers=headers, json=data)
        print(f"Response club_gift_send status: {response.status_code}")
        print(f"Response club_gift_send body: {response.text}")
        response.raise_for_status()

    except requests.RequestException as e:
        print(f"An error occurred during API requests: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def club_leaderboard_gift(token, channel_id):
    await tokenGeneration.buy_coins(token)
    data_leaderboard = {
        "channelId": channel_id,
        "giftKey": random.choice(GIFT_KEYS_LEADERBOARD)
    }
    await send_club_gift(token, data_leaderboard)

async def club_leaderboard_gift_pass(token, channel_id):
    await tokenGeneration.buy_coins(token)
    data_leaderboard_pass = {
        "channelId": channel_id,
        "giftKey": random.choice(GIFT_KEYS_LEADERBOARD_PASS)
    }
    await send_club_gift(token, data_leaderboard_pass)

async def get_new_token():
    async with aiomysql.connect(host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com', port=3306,
                                user='admin', password='Stan.321',
                                db='stage_stan') as conn:
        print('Database connected')
        async with conn.cursor() as cursor:
            query = f"SELECT phone FROM user WHERE id = {conftest.last_id} AND deletedAt IS NULL"
            await cursor.execute(query)
            result = await cursor.fetchone()
            if result is None:
                return None
            conftest.last_id += 1
            phone = result[0]
            token = await tokenGeneration.generate_token(phone)
            print(f"Generated token: {token}")
            return token

def fetch_live_clubs(token):
    url = f"{API_BASE_URL}/v5/get/live-clubs?status=live&limit=10&offset=0&category=All"
    headers = get_headers(token)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Returns the entire JSON response
    else:
        print(f"Failed to fetch live clubs: {response.status_code} {response.text}")
        return []

async def club_leaderboard_operations():
    # Capture print statements
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        initial_token_value = await get_new_token()
        if not initial_token_value:
            print("Failed to generate an initial token.")
            return

        clubs_response = fetch_live_clubs(initial_token_value)
        if not clubs_response:
            print("No live clubs available.")
            return

        clubs = clubs_response.get('clubs', []) if isinstance(clubs_response, dict) else clubs_response

        if not clubs:
            print("No clubs found in the response.")
            return

        for _ in range(2):  # Running the operation for 4 random clubs
            club = random.choice(clubs)
            channel_id = club.get('channelId')
            if not channel_id:
                continue
            print(f"Starting club_leaderboard_gift operation for club {channel_id}")
            token_value = await get_new_token()  # Get a new token for each club operation
            if not token_value:
                print(f"Token value is invalid or missing for club {channel_id}.")
                continue
            await club_leaderboard_gift(token_value, channel_id)
            print(f"Completed club_leaderboard_gift operation for club {channel_id}")

            print(f"Starting club_leaderboard_gift_pass operation for club {channel_id}")
            token_value = await get_new_token()  # Get a new token for each club operation
            if not token_value:
                print(f"Token value is invalid or missing for club {channel_id}.")
                continue
            await club_leaderboard_gift_pass(token_value, channel_id)
            print(f"Completed club_leaderboard_gift_pass operation for club {channel_id}")

    finally:
        # Restore standard output
        sys.stdout = old_stdout

    # Get the captured output
    output = new_stdout.getvalue()
    new_stdout.close()
    return output

# Example usage of the function
# if __name__ == "__main__":
#     import asyncio
#     result = asyncio.run(club_leaderboard_operations())
#     print(result)
