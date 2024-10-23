import asyncio
import json
import aiomysql
import pymongo
import requests
from pymongo import MongoClient
from bson import ObjectId

from endpoints import ENDPOINTS
from test_data import JoinCommunity, SendMessage, SendReaction

last_id = 10040  # from where the code will start picking up userids
ws_conns_array = []
token_storage = []
members = []
admin_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiZ21pUHJvZmlsZUlkIjozMTk1LCJleHAiOjE3MTc2NjY2MjksImZyZWVmaXJlUHJvZmlsZUlkIjozMjMxLCJpYXQiOjE3MTc1ODAyMjksImlkIjoxOTQzfQ.2iJg3SIJUleKdQSmJpM8LYNNC0tBdsQfQyyAleZulws'

# Mongo connection details
MONGO_DB_URL = "mongodb+srv://stage-stan:lqlFL2GvRItS3YFi@stan-stage-01.dfrdedi.mongodb.net/"
MONGO_DB_NAME = "stage"


async def main():
    try:
        conn = await aiomysql.connect(
            host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com',
            port=3306,
            user='admin',
            password='Stan.321',
            db='stage_stan'
        )

        print('Database connected....')

        try:
            for i in range(100):
                token = await get_tokens(conn)
                if not token:
                    continue
                await perform_connections(token)
        finally:
            conn.close()

    except aiomysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")


async def get_tokens(connection):
    global last_id
    async with connection.cursor() as cursor:
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
    url = "https://stage-api.getstan.app/api/v4/verify/otp"

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

    # Convert the data dictionary to JSON format
    json_data = json.dumps(data)

    # Making the POST request
    try:
        response = requests.post(url, headers=headers, data=json_data)
        response.raise_for_status()  # Raises HTTPError for bad requests (4XX or 5XX)
        result = response.json()
        return result.get('access_token')  # Return the access token
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def test_communities():
    print("+++++ Starting communities test ++++")
    print(token_storage)
    for i in range(len(token_storage)):
        headers = {
            'Authorization': f'Bearer {token_storage[i]}',
            'AppVersion': '118'
        }
        # joining community with Stage users
        join = requests.post(ENDPOINTS['community_join'], json=JoinCommunity, headers=headers)
        # sending messages to community with Stage users
        react = requests.post(ENDPOINTS['send_reaction'], json=SendReaction, headers=headers)
        # Print the status code and response data
        sendmsg = requests.post(ENDPOINTS['send_message'], json=SendMessage, headers=headers)
        print(f"Status Code: {join.status_code}")
        print(f"Response: {join.text}")
        print(f"Status Code: {react.status_code}")
        print(f"Response: {react.text}")
        print(f"Status Code: {sendmsg.status_code}")
        print(f"Response: {sendmsg.text}")
        if join.status_code == 200:
            print("Data retrieved:", join.json())
        else:
            print("Failed to retrieve data")


def get_db():
    client = MongoClient(MONGO_DB_URL)
    db = client[MONGO_DB_NAME]
    return db


def test_remove_user():
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'AppVersion': '118'
    }
    client = pymongo.MongoClient(MONGO_DB_URL)
    db = client[MONGO_DB_NAME]
    users = db.user_communities_joined.find({"communityId": ObjectId('664f5ef884c1c19c42fc22ab')}).limit(2)
    print("\n")
    for doc in users:
        members.append(doc['userId'])
        print(doc['userId'])
        rem_user = {
            "communityId": "664f5ef884c1c19c42fc22ab",
            "userId": doc['userId']
        }

        remove = requests.post(ENDPOINTS['remove_member'], json=rem_user, headers=headers)
        print(remove.json())


if __name__ == '__main__':
    choice = input("Enter the test to run (test_communities, test_remove_user): ")
    if choice == 'test_communities':
        asyncio.run(main())  # Initialize tokens first
        test_communities()
    elif choice == 'test_remove_user':
        test_remove_user()
    else:
        print("Invalid choice. Please choose either 'test_communities' or 'test_remove_user'.")
