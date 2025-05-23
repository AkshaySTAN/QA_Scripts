import requests
import json
import asyncio
import aiomysql

# Globals for tracking
Last_id = 1
user_ids = []
token_storage = []

async def generate_token(phone):
    url = "https://stage-api.getstan.app/api/v4/verify/otp"
    data = {
        "phone": phone,
        "otp": "5555",
        "integrityToken": None,
        "sessionId": None,
        "deviceInfo": {
            "APP_TYPE": "android",
            "DeviceData": {
                "deviceUID": "8b6bfb93fafc9w9d"
            }
        },
        "utmPayload": {},
        "campaignUrl": ""
    }
    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip"
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Response Headers: {response.headers}")
    if response.status_code == 200:
        try:
            response_body = response.json()
            return response_body.get("access_token")
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            raise
    else:
        print(f"Response Body: {response.text}")
        raise Exception(f"Failed to generate token. Status code: {response.status_code}")

async def get_tokens(connection, count, start_id_param):
    global Last_id # Still uses global Last_id for iteration, but initialized by param
    tokens = []
    
    # Use the passed start_id_param instead of input()
    current_user_id = start_id_param 

    async with connection.cursor() as cursor:
        # Last_id = input("Please enter the starting user ID: ") # Removed input
        # Last_id = int(Last_id)
        while len(tokens) < count:
            query = f"SELECT phone FROM user WHERE id = {current_user_id} AND deletedAt IS NULL"
            await cursor.execute(query)
            result = await cursor.fetchone()
            if result is None:
                current_user_id += 1
                continue
            phone = result[0]
            token = await generate_token(phone)
            if token:
                tokens.append(token)
                user_ids.append(current_user_id) # Use current_user_id which is being iterated
            current_user_id += 1
            Last_id = current_user_id # Update global Last_id if it's still needed elsewhere, though ideally avoid globals
    return tokens

async def main(usr_range=None, start_id=None):
    # Use usr_range from parameter, or prompt if not provided (fallback)
    if usr_range is None:
        usr_range = int(input("Please enter the no. of users you want to extract tokens for: "))
    # Add prompting for start_id if it's not provided
    if start_id is None:
        start_id = int(input("Please enter the starting user ID: "))

    conn = await aiomysql.connect(
        host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com',
        port=3306,
        user='admin',
        password='Stan.321',
        db='stage_stan'
    )
    print('Database connected....')
    try:
        # Pass start_id to get_tokens
        tokens = await get_tokens(conn, usr_range, start_id)
        print(f"\nExtracted tokens: {tokens}")
        return tokens
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())

