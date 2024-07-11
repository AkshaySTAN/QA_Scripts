# import pymysql as pymysql
import asyncio
import json
import aiomysql
import requests
from aiomysql import connection
from bson import ObjectId
import pymongo
from pymongo import MongoClient
from Admin_panel_autologin import LoginToPanel, AdminUrl, response
from endpoints import ENDPOINTS, VERIFY_OTP
from test_data import JoinCommunity, SendMessage, SendReaction, RemoveUser, data_mod, generic_headers

ws_conns_array = []
token_storage = []
members = []

# Mongo connection details
MONGO_DB_URL = "mongodb+srv://stage-stan:lqlFL2GvRItS3YFi@stan-stage-01.dfrdedi.mongodb.net/"
MONGO_DB_NAME = "stage"
COLLECTION_NAME = "communities"

last_id = int(input("please enter LasId"))  # from where the code will start picking up userids


def communities():
    pass


def remove_user():
    pass


async def main():
    conn = await aiomysql.connect(host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com', port=3306,
                                  user='admin', password='Stan.321',
                                  db='stage_stan')

    print('Database connected....')
    lent = int(input("Please enter the no. of users that you want to add to a community"))

    try:
        for i in range(lent):
            token = await get_tokens(conn)
            if not token:
                continue
            await perform_connections(token)

    finally:
        conn.close()


async def get_tokens(connection1):
    global last_id
    async with connection1.cursor() as cursor:
        query = f"SELECT phone FROM user WHERE id = {last_id} AND deletedAt IS NULL"
        await cursor.execute(query)
        result = await cursor.fetchone()
        if result is None:
            return None
        else:
            last_id += 1
            phone = result[0]
            token = await generate_token(phone)
            token_storage.append(token)
            return token


async def perform_connections(token):
    # Simulate some operation with token
    print(f"Fetching the tokens: {token}")


async def generate_token(phone):
    # Simulate token generation
    verify_otp_url = "https://stage-api.getstan.app/api/v4/verify/otp"

    # Headers
    headers1 = {
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

    # Convert the data dictionary to JSON format
    json_data = json.dumps(data)
    json_data_mod = json.dumps(data_mod)
    # Making the POST request
    try:
        response = requests.post(verify_otp_url, headers=headers1, data=json_data)
        response.raise_for_status()  # Raises HTTPError for bad requests (4XX or 5XX)
        result = response.json()
        return result.get('access_token')  # Return the access token
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def communities():
    url1 = "https://stage-api.getstan.app/api/v4/verify/otp"
    json_data_mod = json.dumps(data_mod)
    response_mod = requests.post(url=url1, headers=generic_headers, data=json_data_mod)
    result_mod = response_mod.json()
    admin_token = result_mod.get('access_token')

    print("+++++ Starting communities test ++++")
    print("got the admin token =>", admin_token)
    # print(token_storage)
    for i in range(len(token_storage)):
        headers = {
            'Authorization': f'Bearer {token_storage[i]}',
            'AppVersion': '118'
        }
        msgheader = {
            'Authorization': f'Bearer {admin_token}',
            'AppVersion': '118'
        }
        join = requests.post(ENDPOINTS['community_join'], json=JoinCommunity, headers=headers)
        print(f"JOIN Status Code: {join.status_code}")
        print(f"Response: {join.json()}")
        if join.status_code == 200:
            print("Data retrieved:", join.json())
        else:
            print("Failed to retrieve data")
        sendmsg = requests.post(ENDPOINTS['send_message'], json=SendMessage, headers=msgheader)
        print(f" \n Send message Status Code: {sendmsg.status_code}")
        print(f"Response: {sendmsg.text}")
        #
        # react = requests.post(ENDPOINTS['send_reaction'], json=SendReaction, headers=headers)
        # print(f" \nSend reaction Status Code: {react.status_code}")
        # print(f"Response: {react.text}")


def get_db():
    client = MongoClient(MONGO_DB_URL)
    db = client[MONGO_DB_NAME]
    return db


def remove_user():
    url = "https://stage-api.getstan.app/api/v4/verify/otp"
    json_data_mod = json.dumps(data_mod)
    response_mod = requests.post(url, headers=generic_headers, data=json_data_mod)
    result_mod = response_mod.json()
    admin_token = result_mod.get('access_token')
    print("admin_token", admin_token)
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'AppVersion': '118'
    }
    com_id = input("Enter the community id to remove the users from")
    num = int(input("Enter the no.of users you want to remove"))
    client = pymongo.MongoClient(MONGO_DB_URL)
    db = client[MONGO_DB_NAME]
    # collection = db[collection_name]
    users = db.user_communities_joined.find({"communityId": ObjectId(com_id)}).limit(num)
    print("\n")
    for doc in users:
        members.append(doc['userId'])
        print(doc['userId'])
        rem_user = {
            "communityId": com_id,
            "userId": doc['userId']
        }

        remove = requests.post(ENDPOINTS['remove_member'], json=rem_user, headers=headers)
        print(remove.json())


def delete_community():
    header = {
            'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiZ21pUHJvZmlsZUlkIjozMTk1LCJleHAiOjE3MTg4NjkzOTcsImZyZWVmaXJlUHJvZmlsZUlkIjozMjMxLCJpYXQiOjE3MTg3ODI5OTcsImlkIjoxOTQzfQ.QGkP0u8ZuMDcU-4FoUJ2Yf8EEcPLLvpobOHqY0r-VtE',
            'AppVersion': '118'
        }
    commit = input("Enter the community id =>")
    data = {
        "communityId": commit,
    }
    delete_com = requests.post(url=ENDPOINTS['delete'], headers=header, data=data)
    print(delete_com.json())


if __name__ == '__main__':
    asyncio.run(main())

while True:
    print("\nSelect an action:")
    print("1. Join user in Communities")
    print("2. Remove User")
    print("3. Delete Community")
    print("4. Exit =>")
    choice = input("Enter your choice (1/2/3/4): ")

    if choice == '1':
        communities()
    elif choice == '2':
        remove_user()
    elif choice == '3':
        delete_community()
    elif choice == '4':
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please enter 1, 2,3 or 4.")
