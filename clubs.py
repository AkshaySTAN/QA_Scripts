import asyncio
import json
import aiomysql
import requests
# from Communities_join_remove_user import UsrRange, last_id
from urls import SUPER_URL, ADMIN_URL, BASIC_ENDPOINTS

ws_conns_array = []
token_storage = []
user_ids = []
Last_id = int(input("Please enter the user id to start from"))


def generate_admin_token():
    AdminHeader = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Authorization": "Bearer null",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "User-Agent": "API test",
        "Content-Length": "*"
    }

    AdminData = {"email": "akshay@getstan.app",
                 "password": "TPiuOv"
                 }

    AdminUrl = 'https://stage-admin.getstan.app/admin-api/login'

    LoginToPanel = requests.post(url=AdminUrl, headers=AdminHeader, json=AdminData)
    response = LoginToPanel.json()

    #   Extract the 'secretToken' field
    secret_token = response['result']['data']['secretToken']
    return secret_token


async def main():
    conn = await aiomysql.connect(host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com', port=3306,
                                  user='admin', password='Stan.321',
                                  db='stage_stan')

    print('Database connected....')
    usr_range = int(input("PLease enter the no. of clubs u want to create"))
    try:
        for i in range(usr_range):
            token = await get_tokens(conn)
            if not token:
                continue
            await perform_connections(token)

    finally:
        conn.close()


async def get_tokens(connection):
    global Last_id
    async with connection.cursor() as cursor:
        query = f"SELECT phone FROM user WHERE id = {Last_id} AND deletedAt IS NULL"
        await cursor.execute(query)
        result = await cursor.fetchone()
        if result is None:
            return None
        else:
            user_ids.append(Last_id)
            Last_id += 1
            phone = result[0]
            token = await generate_token(phone)
            token_storage.append(token)
            return token


async def perform_connections(token):
    # Simulate some operation with token
    print(f"Fetching the tokens: {token}")


async def generate_token(phone):
    # Simulate token generation
    urlt = "https://stage-api.getstan.app/api/v4/verify/otp"

    # Headers
    headers = {
        "appversion": "112",
        "platform": "android",
        "Content-Type": "application/json"
    }

    # Data to be sent in the POST request
    data = {
        "phone": phone,
        "otp": "5555",
        "deviceInfo": {
            "APP_TYPE": "android",
            "DeviceData": {
                "deviceUID": "8b6bfb93fafc9w9d"
            }
        },
        "utmPayload": {},
        "campaignUrl": "",
        "sessionId": None,
        "referralCode": None,
        "provider": ""
    }

    json_data = json.dumps(data)

    # Making the POST request
    try:
        response = requests.post(url=urlt, headers=headers, data=json_data)
        response.raise_for_status()  # Raises HTTPError for bad requests (4XX or 5XX)
        result = response.json()
        return result.get('access_token')  # Return the access token
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def create_club():
    print("+++++ Starting clubs test ++++")
    secret_token = generate_admin_token()
    print(user_ids)
    for i in range(len(token_storage)):
        user_id = int(user_ids[i])
        print(user_id)
        payload = {
            "clubHosterType": "MUGC",
            "isClubHoster": True,
            "playerBanTimeInOnevone": "Invalid date",
            "gameId": "bgmi",
            "id": user_id
        }
        print(payload, "payload")

        assign_type_header = {
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'accept': 'application/json',
            'origin': 'https://stan-admin-7.web.app',
            'Authorization': f'Bearer {secret_token}'
        }
        assign_mod_category = requests.post(url=f"{ADMIN_URL}{BASIC_ENDPOINTS['assign_club_type']}",
                                            headers=assign_type_header,
                                            json=payload)
        print('Assigning PGC category to user => ' + str(user_ids[i]))
        print(assign_mod_category.text)

        files = {
            'thumbnail': ('collect.png', open('/Users/macbookprom1/PycharmProjects/collect.png', 'rb'), 'image/png'),
            'title': (None, f'{user_id}'),
            'tags': (None, 'Music'),
            'roomStatus': (None, 'Live'),
            'pinnedMessage': (None, '{"message":"","link":""}')
        }
        createClubHeaders = {
            # Remove Content-Type from headers; let requests handle it
            'Accept': '*/*',
            'GameId': 'freefire',
            'AppVersion': '118',
            'Platform': 'android',
            'SID': '1714035078106-20645',
            'Authorization': f'Bearer {token_storage[i]}'
        }
        create_a_club = requests.post(url=f"{SUPER_URL}{BASIC_ENDPOINTS['create_club']}", headers=createClubHeaders,
                                      files=files)
        print('Club created for user => ' + str(user_ids[i]))
        print(create_a_club.text)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
    create_club()
