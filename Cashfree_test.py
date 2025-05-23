# import pymysql as pymysql
import asyncio
# import json
import aiomysql
# import requests
# from aiomysql import connection
# from bson import ObjectId
from pymongo import MongoClient
# from endpoints import ENDPOINTS, VERIFY_OTP
# from test_data import JoinCommunity, SendMessage, SendReaction, RemoveUser, data_mod, generic_headers

ws_conns_array = []
token_storage = []
members = []

# Mongo connection details
MONGO_DB_URL = "mongodb+srv://stage-stan:lqlFL2GvRItS3YFi@stan-stage-01.dfrdedi.mongodb.net/"
MONGO_DB_NAME = "stage"
COLLECTION_NAME = "user_creator_dashboard_data"

def get_db():
    client = MongoClient(MONGO_DB_URL)
    db = client[MONGO_DB_NAME]
    return db

def update_lifetime_earnings_in_mongo(user_id, new_earnings):
    db = get_db()
    collection = db[COLLECTION_NAME]
    result = collection.update_one(
        {"userId": user_id},
        {"$set": {"lifetimeEarnings": new_earnings}}
    )
    print(f"[MongoDB] Modified {result.modified_count} document(s).")
    return result.modified_count

async def update_referral_cash_in_sql(user_id, referral_cash):
    async with aiomysql.connect(
        host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com',
        port=3306,
        user='admin',
        password='Stan.321',
        db='stage_stan'
    ) as conn:
        print('[MySQL] Database connected')
        async with conn.cursor() as cursor:
            query = f"UPDATE stage_stan.user_currency SET referral_cash = {referral_cash} WHERE userId = {user_id}"
            await cursor.execute(query)
            await conn.commit()
            print(f"[MySQL] Updated referral_cash for userId {user_id}.")

def get_user_inputs():
    user_id = int(input("Please enter the userId: "))
    referral_cash = float(input("Please enter the new referral_cash value: "))
    lifetime_earnings = float(input("Please enter the new lifetimeEarnings value: "))
    return user_id, referral_cash, lifetime_earnings

async def main():
    user_id, referral_cash, lifetime_earnings = get_user_inputs()
    update_lifetime_earnings_in_mongo(user_id, lifetime_earnings)
    await update_referral_cash_in_sql(user_id, referral_cash)
    print("All updates completed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

