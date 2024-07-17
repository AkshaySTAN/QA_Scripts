from request_body_factory import RequestBodyFactory
from token_generation import generate_token
from buy_coins import buy_coins
import io
import sys
import asyncio
import aiohttp  # Use aiohttp for async HTTP requests
from database_connection import DatabaseConnection

BASE_URL = "https://stage-api.getstan.app"
APP_VERSION = "122"
GAME_ID = "freefire"
PATHS = [
    "/api/v1/card-packs/buy",
    "/api/v1/crates/buy",
    "/api/v1/cards/upgrade",
    "/api/v1/community-market/list",
    "/api/v1/cards/dismantle"
]


async def get_random_profile_id(db):
    query = "SELECT p.id, p.userId FROM profile p JOIN user u ON p.userId = u.id WHERE p.id>26564 and p.gameId ='freefire' and p.deletedAt IS NULL AND u.phone IS NOT NULL ORDER BY RAND() LIMIT 1"
    results = await db.fetch_data(query)  # Use await here to get the actual result
    print(f"Results from DB: {results}")
    if results:
        return {
            "userId": results[0]['userId'],  # Now results is an actual list, not a coroutine
            "profileId": results[0]['id']
        }
    else:
        print("Failed to fetch random profile ID from the database.")
        return None


async def fetch_latest_user_card_id(db, profile_id):
    query = f"SELECT id FROM user_card WHERE profileId = {profile_id} AND deletedAt IS NULL ORDER BY id DESC LIMIT 1"
    results = await db.fetch_data(query)
    print(f"Results from latest user card ID query: {results}")
    cards = len(results)
    if cards == 0:
        print('---------->This user do not have any cards<-------------------------')
        return

    if results:
        return results[0]['id']
    else:
        print("ResultSet is null or empty.")
        return -1


async def fetch_last_second_user_card_id(db, profile_id):
    query = f"SELECT id FROM user_card WHERE profileId = {profile_id} AND deletedAt IS NULL ORDER BY id DESC LIMIT 1 OFFSET 1"
    results = await db.fetch_data(query)
    print(f"Results from last second user card ID query: {results}")
    if results:
        return results[0]['id']
    else:
        print("ResultSet is null or empty.")
        return -1


async def fetch_first_user_card_id(db, profile_id):
    query = f"SELECT id FROM user_card WHERE profileId = {profile_id} AND deletedAt IS NULL LIMIT 1"
    results = await db.fetch_data(query)
    print(f"Results from first user card ID query: {results}")
    if results:
        return results[0]['id']
    else:
        print("ResultSet is null or empty.")
        return -1


async def fetch_phone_number(db, user_id):
    phone_number_query = f"SELECT phone FROM user WHERE id = {user_id}"
    print(f"Executing query: {phone_number_query}")
    phone_number_results = await db.fetch_data(phone_number_query)
    print(f"Results from phone number query: {phone_number_results}")
    if phone_number_results:
        return phone_number_results[0]['phone']
    else:
        print("Failed to fetch phone number for profile ID.")
        return None


async def purchase_inventory():
    # Create a StringIO object to capture output
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        db = DatabaseConnection(loop=asyncio.get_running_loop())
        connection = await db.get_connection()
        if not connection:
            print("Failed to establish database connection.")
            return

        user_details = await get_random_profile_id(db)
        if user_details:
            phone_number = await fetch_phone_number(db, user_details["userId"])
            token = generate_token(phone_number)
            if not token:
                print("Token generation failed")
                return

            await buy_coins(token)
            print("Coins added successfully.")

            latest_user_card_id = await fetch_latest_user_card_id(db, user_details["profileId"])
            first_user_card_id = await fetch_first_user_card_id(db, user_details["profileId"])
            last_second_user_card_id = await fetch_last_second_user_card_id(db, user_details["profileId"])

            request_body_map = {
                PATHS[0]: RequestBodyFactory.create_request_body1(),
                PATHS[1]: RequestBodyFactory.create_request_body2(),
                PATHS[2]: RequestBodyFactory.create_request_body3(first_user_card_id),
                PATHS[3]: RequestBodyFactory.create_request_body4(latest_user_card_id),
                PATHS[4]: RequestBodyFactory.create_request_body5(last_second_user_card_id)
            }

            async with aiohttp.ClientSession() as session:
                for path in PATHS:
                    request_body = request_body_map.get(path)
                    if not request_body:
                        print(f"Request body for path {path} is null.")
                        continue

                    headers = {
                        "Content-Type": "application/json",
                        "AppVersion": APP_VERSION,
                        "Authorization": f"Bearer {token}",
                    }
                    if path != "/api/v1/community-market/list":
                        headers["gameid"] = GAME_ID

                    async with session.post(BASE_URL + path, headers=headers, json=request_body) as response:
                        response_text = await response.text()
                        print(f"Path: {path}")
                        print(f"Status Code: {response.status}")
                        print(f"Response: {response_text}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        await db.close_connection()
        print("Database connection closed.")

    # Restore standard output
    sys.stdout = sys.__stdout__

    # Get the content of captured output and return it
    output = captured_output.getvalue()
    captured_output.close()
    return output


if __name__ == "__main__":
    asyncio.run(purchase_inventory())
