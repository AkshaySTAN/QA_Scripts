import json
import aiomysql as aiomysql
import pymongo
import requests
from bson import ObjectId
from quart import Quart, request, render_template, redirect, url_for
from Inventory_purchase import purchase_inventory


app = Quart(__name__)

# Mongo connection details
MONGO_DB_URL = "mongodb+srv://stage-stan:lqlFL2GvRItS3YFi@stan-stage-01.dfrdedi.mongodb.net/"
MONGO_DB_NAME = "stage"
COLLECTION_NAME = "communities"

# SQL connection
DB_HOST = 'nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com'
DB_PORT = 3306
DB_USER = 'admin'
DB_PASS = 'Stan.321'
DB_NAME = 'stage_stan'
token_storage = []
ws_conns_array = []
members = []

Community_BASE_URL = "https://stage-api.getstan.app/api/v4/communities/"
VERIFY_OTP_URL = "https://stage-api.getstan.app/api/v4/verify/otp"

ENDPOINTS = {
    "community_join": f"{Community_BASE_URL}join-community",
    "send_reaction": f"{Community_BASE_URL}message/react",
    "send_message": f"{Community_BASE_URL}message/send",
    "remove_member": f"{Community_BASE_URL}remove-member",
    "get_comments": f"{Community_BASE_URL}comments",
    "delete": f"{Community_BASE_URL}delete"
    # add other endpoints here
}

generic_headers = {
    "appversion": "112",
    "platform": "android",
    "Content-Type": "application/json"
}

data_mod = {
    "phone": "+919650195950",
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


@app.route('/join_community_result')
async def join_community_result():
    output = request.args.get('output')  # Get the output from the query parameter
    if output is None:
        output = "No output provided"
    return await render_template('join_community_result.html', output=output)


@app.route('/inventory')
async def inventory_operations_result():
    output = await purchase_inventory()
    return await render_template('inventory_operations_result.html', output=output)

@app.route('/', methods=['GET', 'POST'])
async def form():
    if request.method == 'POST':
        form_data = await request.form
        action = form_data.get('action')
        community_id = form_data.get('community_id')

        # Different actions might require different parameters and handling.
        if action == 'join_community':
            last_id = int(form_data.get('last_id', 0))  # Default to 0 if not provided
            rang = int(form_data.get('range', 0))  # Default to 0 if not provided
            output = await join_community(last_id, community_id, rang)
        elif action == 'remove_user':
            rang = int(form_data.get('range', 0))  # Default to 0 if not provided
            output = await remove_user(community_id, rang)
        elif action == 'delete_community':
            user_id = form_data.get('user_id')  # Specific to delete_community action
            output = await delete_community(community_id, user_id)
        elif action == 'inventory_operations':
            output = await purchase_inventory()
        else:
            return "Invalid action", 400  # Return a 400 Bad Request for undefined actions

        return redirect(url_for(f'{action}_result', output=output))

    # Show the form by default if it's a GET request or no action was taken.
    return await render_template('form.html')


async def handle_action(action, last_id, community_id, rang, user_id):
    if action == 'join_community':
        await join_community(last_id, community_id, rang)
    elif action == 'remove_user':
        await remove_user(community_id, rang)
    elif action == 'delete_community':
        await delete_community(community_id, user_id)
    elif action == 'inventory_operations':
        await purchase_inventory()
    else:
        raise ValueError("Invalid action")


async def join_community(last_id, community_id, rang):
    conn = await aiomysql.connect(host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com', port=3306,
                                  user='admin', password='Stan.321',
                                  db='stage_stan')

    print('Database connected....')

    try:
        for i in range(rang):
            token = await get_tokens(conn, last_id)
            last_id = last_id + 1
            if not token:
                continue
            await perform_connections(token)

    finally:
        conn.close()
    # Example function for joining a community
    # lastid = last_id
    JoinCommunity = {
        "communityId": community_id,
        "password": 'null',
        "channelId": "664f5ef984c1c19c42fc22ae"
    }

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
        # msgheader = {
        #     'Authorization': f'Bearer {admin_token}',
        #     'AppVersion': '118'
        # }
        join = requests.post(ENDPOINTS['community_join'], json=JoinCommunity, headers=headers)
        print(f"JOIN Status Code: {join.status_code}")
        print(f"Response: {join.json()}")
        if join.status_code == 200:
            print("Data retrieved:", join.json())
        else:
            print("Failed to retrieve data")
        # sendmsg = requests.post(ENDPOINTS['send_message'], json=SendMessage, headers=msgheader)
        # print(f" \n Send message Status Code: {sendmsg.status_code}")
        # print(f"Response: {sendmsg.text}")
    return "Joined community successfully"


async def remove_user(community_id, rang):
    url = "https://stage-api.getstan.app/api/v4/verify/otp"
    json_data_mod = json.dumps(data_mod)
    response_mod = requests.post(url, headers=generic_headers, data=json_data_mod)
    result_mod = response_mod.json()
    admin_token = result_mod.get('access_token')
    print("got the admin_token", admin_token)
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'AppVersion': '118'
    }
    client = pymongo.MongoClient(MONGO_DB_URL)
    db = client[MONGO_DB_NAME]
    # collection = db[collection_name]
    users = db.user_communities_joined.find({"communityId": ObjectId(community_id)}).limit(rang)
    print("\n")
    for doc in users:
        members.append(doc['userId'])
        print(doc['userId'])
        rem_user = {
            "communityId": community_id,
            "userId": doc['userId']
        }

        remove = requests.post(ENDPOINTS['remove_member'], json=rem_user, headers=headers)
        print(remove.json())


async def delete_community(community_id, user_id):
    conn = await aiomysql.connect(host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com', port=3306,
                                  user='admin', password='Stan.321',
                                  db='stage_stan')

    print('Database connected....')
    async with conn.cursor() as cursor:
        query = f"SELECT phone FROM user WHERE id = {user_id} AND deletedAt IS NULL"
        await cursor.execute(query)
        phon = await cursor.fetchone()
        data_MOD = {
            "phone": phon,
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

    url = "https://stage-api.getstan.app/api/v4/verify/otp"
    json_data_mod = json.dumps(data_MOD)
    response_mod = requests.post(url, headers=generic_headers, data=json_data_mod)
    result_mod = response_mod.json()
    admin_token = result_mod.get('access_token')
    print("got the admin_token", admin_token)
    header = {
        'Authorization': f'Bearer {admin_token}',
        'AppVersion': '118'
    }
    data = {
        "communityId": community_id,
    }
    delete_com = requests.post(url=ENDPOINTS['delete'], headers=header, data=data)
    print(delete_com.json())


async def get_tokens(connection1, last_id):
    async with connection1.cursor() as cursor:
        query = f"SELECT phone FROM user WHERE id = {last_id} AND deletedAt IS NULL"
        await cursor.execute(query)
        result = await cursor.fetchone()
        if result is None:
            return None
        else:
            phone = result[0]
            token = await generate_token(phone)
            token_storage.append(token)
            print("token generated successfully")
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
    # Making the POST request
    try:
        response = requests.post(verify_otp_url, headers=headers1, data=json_data)
        response.raise_for_status()  # Raises HTTPError for bad requests (4XX or 5XX)
        result = response.json()
        return result.get('access_token')  # Return the access token
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)

#####################################################################################################################


#
# app = Quart(__name__)
#
# last_id = 0  # Ensure last_id is initialized
#
#
# @app.before_serving
# async def initialize_last_id():
#     global last_id
#     # Initialize last_id to the first valid ID in the database
#     conn = await aiomysql.connect(host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com', port=3306,
#                                   user='admin', password='Stan.321',
#                                   db='stage_stan')
#     async with conn.cursor() as cursor:
#         query = "SELECT id FROM user WHERE deletedAt IS NULL ORDER BY id ASC LIMIT 1"
#         await cursor.execute(query)
#         result = await cursor.fetchone()
#         if result:
#             last_id = result[0]
#             print(f"Initialized last_id to {last_id}")
#         else:
#             print("No valid entries found in the user table.")
#     conn.close()
#
#
# @app.route('/', methods=['GET', 'POST'])
# async def form():
#     if request.method == 'POST':
#         form_data = await request.form
#         action = form_data.get('action')
#         last_id = int(form_data.get('last_id'))  # Convert to integer as it comes as a string from form
#         community_id = form_data.get('community_id')
#         rang = int(form_data.get('range'))
#
#         # Pass last_id to handle_action
#         output = await handle_action(action, last_id, community_id, rang)
#
#         # Redirect to the appropriate result page based on the action
#         return redirect(url_for(f'{action}_result', output=output))
#
#     return await render_template('form.html')
#
#
# @app.route('/join_community_result')
# async def join_community_result():
#     output = request.args.get('output')  # Get the output from the query parameter
#     if output is None:
#         output = "No output provided"
#     return await render_template('join_community_result.html', output=output)
#
#
# @app.route('/remove_user_result')
# async def remove_user_result():
#     output = request.args.get('output')  # Get the output from the query parameter
#     if output is None:
#         output = "No output provided"
#     return await render_template('remove_user_result.html', output=output)
#
#
# @app.route('/delete_community_result')
# async def delete_community_result():
#     output = request.args.get('output')  # Get the output from the query parameter
#     if output is None:
#         output = "No output provided"
#     return await render_template('delete_community_result.html', output=output)
#
#
# async def handle_action(action, last_id, community_id, rang):
#     if action == 'join_community':
#         await mane(rang)  # Pass last_id to mane
#         return await communities(last_id, community_id, rang)
#     elif action == 'remove_user':
#         await mane(rang)  # Pass last_id to mane
#         return await remove_user(community_id, rang)  # Pass last_id to remove_user
#     elif action == 'delete_community':
#         return await delete_community(community_id)
#     else:
#         return "Invalid action"
#
#
#
# ws_conns_array = []
# token_storage = []
# members = []
#
# # Mongo connection details
# MONGO_DB_URL = "mongodb+srv://stage-stan:lqlFL2GvRItS3YFi@stan-stage-01.dfrdedi.mongodb.net/"
# MONGO_DB_NAME = "stage"
# COLLECTION_NAME = "communities"
#
#
# async def mane(rang):
#     conn = await aiomysql.connect(host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com', port=3306,
#                                   user='admin', password='Stan.321',
#                                   db='stage_stan')
#
#     print('Database connected....')
#
#     try:
#         for i in range(rang):
#             token = await get_tokens(conn)
#             if not token:
#                 continue
#             await perform_connections(token)
#
#     finally:
#         conn.close()
#
#
# async def get_tokens(connection1,last_id):
#
#     async with connection1.cursor() as cursor:
#         query = f"SELECT phone FROM user WHERE id = {last_id} AND deletedAt IS NULL"
#         print(f"Executing query: {query}")
#         await cursor.execute(query)
#         result = await cursor.fetchone()
#         if result is None:
#             print(f"No phone found for id {last_id}")
#             return None
#         else:
#             phone = result[0]
#             print(f"Found phone: {phone} for id {last_id}")
#             token = await generate_token(phone)
#             if token:
#                 print(f"Generated token: {token} for phone: {phone}")
#                 token_storage.append(token)
#                 print(f"Updated token_storage: {token_storage}")
#             last_id += 1  # Move to the next ID
#             return token
#
#
# async def perform_connections(token):
#     # Simulate some operation with token
#     print(f"Fetching the tokens: {token}")
#
#
# async def generate_token(phone):
#     verify_otp_url = "https://stage-api.getstan.app/api/v4/verify/otp"
#
#     headers1 = {
#         "appversion": "112",
#         "platform": "android",
#         "Content-Type": "application/json"
#     }
#
#     data = {
#         "phone": phone,
#         "otp": "5555",
#         "deviceInfo": {
#             "APP_TYPE": "android",
#             "DeviceData": {
#                 "deviceUID": "8b6bfb93fafc9w9d"
#             }
#         },
#         "utmPayload": {},
#         "campaignUrl": "",
#         "sessionId": None,
#         "referralCode": None,
#         "provider": ""
#     }
#
#     json_data = json.dumps(data)
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(verify_otp_url, headers=headers1, data=json_data) as response:
#                 response.raise_for_status()
#                 result = await response.json()
#                 print(f"Response from OTP verification: {result}")
#                 return result.get('access_token')
#     except aiohttp.ClientError as e:
#         print(f"An error occurred: {e}")
#         return None
#
#
# async def communities(last_id, community_id, rang):
#     url1 = "https://stage-api.getstan.app/api/v4/verify/otp"
#     data_mod = {
#         "phone": "+919650195950",
#         "otp": "5555",
#         "deviceInfo": {
#             "APP_TYPE": "android",
#             "DeviceData": {
#                 "deviceUID": "8b6bfb93fafc9w9d"
#             }
#         },
#         "utmPayload": {},
#         "campaignUrl": "",
#         "sessionId": None,
#         "referralCode": None,
#         "provider": ""
#     }
#     json_data_mod = json.dumps(data_mod)
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url1, headers=generic_headers, data=json_data_mod) as response_mod:
#             response_mod.raise_for_status()
#             result_mod = await response_mod.json()
#             admin_token = result_mod.get('access_token')
#
#             JoinCommunity = {
#                 "communityId": community_id,
#                 "password": 'null',
#                 "channelId": "664f5ef984c1c19c42fc22ae"
#             }
#
#             print("+++++ Starting communities test ++++")
#             print("got the admin token =>", admin_token)
#
#             for token in token_storage:
#                 headers = {
#                     'Authorization': f'Bearer {token}',
#                     'AppVersion': '118'
#                 }
#                 msgheader = {
#                     'Authorization': f'Bearer {admin_token}',
#                     'AppVersion': '118'
#                 }
#                 async with session.post(ENDPOINTS['community_join'], json=JoinCommunity, headers=headers) as join:
#                     join.raise_for_status()
#                     print(f"JOIN Status Code: {join.status}")
#                     response_join = await join.json()
#                     print(f"Response: {response_join}")
#                     if join.status == 200:
#                         print("Data retrieved:", response_join)
#                     else:
#                         print("Failed to retrieve data")
#                 async with session.post(ENDPOINTS['send_message'], json=SendMessage, headers=msgheader) as sendmsg:
#                     sendmsg.raise_for_status()
#                     response_sendmsg = await sendmsg.text()
#                     print(f" \n Send message Status Code: {sendmsg.status}")
#                     print(f"Response: {response_sendmsg}")
#
#     return "Community actions completed"  # Add a return statement
#
#
# async def get_db():
#     client = MongoClient(MONGO_DB_URL)
#     db = client[MONGO_DB_NAME]
#     return db
#
#
# async def remove_user(community_id, rang):
#     url = "https://stage-api.getstan.app/api/v4/verify/otp"
#     json_data_mod = json.dumps(data_mod)
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=generic_headers, data=json_data_mod) as response_mod:
#             response_mod.raise_for_status()
#             result_mod = await response_mod.json()
#             admin_token = result_mod.get('access_token')
#             print("admin_token", admin_token)
#             headers = {
#                 'Authorization': f'Bearer {admin_token}',
#                 'AppVersion': '118'
#             }
#
#             client = MongoClient(MONGO_DB_URL)
#             db = client[MONGO_DB_NAME]
#             users = db.user_communities_joined.find({"communityId": ObjectId(community_id)}).limit(rang)
#             print("\n")
#             for doc in users:
#                 members.append(doc['userId'])
#                 print(doc['userId'])
#                 rem_user = {
#                     "communityId": community_id,
#                     "userId": doc['userId']
#                 }
#
#                 async with session.post(ENDPOINTS['remove_member'], json=rem_user, headers=headers) as remove:
#                     remove.raise_for_status()
#                     response_remove = await remove.json()
#                     print(response_remove)
#
#     return "Users removed successfully"  # Add a return statement
#
#
# async def delete_community(community_id):
#     header = {
#         'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiZ21pUHJvZmlsZUlkIjozMTk1LCJleHAiOjE3MTg4NjkzOTcsImZyZWVmaXJlUHJvZmlsZUlkIjozMjMxLCJpYXQiOjE3MTg3ODI5OTcsImlkIjoxOTQzfQ.QGkP0u8ZuMDcU-4FoUJ2Yf8EEcPLLvpobOHqY0r-VtE',
#         'AppVersion': '118'
#     }
#     data = {
#         "communityId": community_id,
#     }
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url=ENDPOINTS['delete'], headers=header, data=data) as delete_com:
#             delete_com.raise_for_status()
#             response_delete = await delete_com.json()
#             print(response_delete)
#
#     return "Community deleted successfully"  # Add a return statement
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
