import json
import random
import aiomysql
import requests
import conftest
import cardPackOperations
import crateOperations
import tokenGeneration
import io
import sys

# Configuration constants
API_BASE_URL = "https://stage-api.getstan.app/api"
APP_VERSION = "118"
PLATFORM = "ios"
SID = "1716878004190-33976"
TS = "undefined"

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

async def run_operations(token_value, operation):
    if not token_value:
        print("Token value is invalid or missing.")
        return

    if operation == "card-pack":
        await cardPackOperations.run_card_pack_operations(token_value)
    elif operation == "crate":
        await crateOperations.run_crate_operations(token_value)
    else:
        print("Invalid operation type specified.")

async def coin_purchases():
    # Capture print statements

    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        print(f"+++++++++++here0000============")
        token_value = await get_new_token()

        if not token_value:
            print(f"+++++++++++here022200============")
            print("Token value is invalid or missing.")
            return
        else:
            print(f"+++++++++++here1============")
            await run_operations(token_value, "card-pack")
            await run_operations(token_value, "crate")
            print(f"+++++++++++here2============")
    finally:
        # Restore standard output
     sys.stdout = old_stdout

    # Get the captured output
    output = new_stdout.getvalue()
    new_stdout.close()
    return output

        # Uncomment below lines if you want to prompt the user for operations
        # choice = input("Enter '1' to run card-pack operations or '2' to run crate operations: ").strip()
        #
        # if choice == '1':
        #     await run_operations(token_value, "card-pack")
        # elif choice == '2':
        #     await run_operations(token_value, "crate")
        # else:
        #     print("Invalid choice. Please enter '1' for card-pack operations or '2' for crate operations.")



# # Example usage of the function
# if __name__ == "__main__":
#     import asyncio
#     result = asyncio.run(coin_purchases())
#     print(result)
