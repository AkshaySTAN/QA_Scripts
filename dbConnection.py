import io
import sys

import aiomysql

import cardPackOperations
import conftest
import crateOperations
import tokenGeneration

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


async def run_operations():
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        token_value = await get_new_token()
        if not token_value:
            print("Failed to generate token")
            return

        # Capture output for the first function
        await cardPackOperations.run_card_pack_operations(token_value)
        output1 = new_stdout.getvalue()
        new_stdout.truncate(0)
        new_stdout.seek(0)

        # Capture output for the second function
        await crateOperations.run_crate_operations(token_value)
        output2 = new_stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    new_stdout.close()

    # Combine outputs
    cboutput = output1 + output2
    return cboutput



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
