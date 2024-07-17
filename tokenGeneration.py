import json
import random
import logging

import aiomysql
import requests
import conftest

import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_token(phone):
    url = "https://stage-api.getstan.app/api/v4/verify/otp"
    headers = {
        "appversion": "112",
        "platform": "android",
        "Content-Type": "application/json"
    }
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
    try:
        response = requests.post(url, headers=headers, data=json_data)
        response.raise_for_status()
        result = response.json()
        return result.get('access_token')
    except requests.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return None


async def buy_coins(token):
    url_add_money = "https://stage-api.getstan.app/api/v1/users/add-money"
    headers_add_money = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "gaid": "",
        "AppVersion": "118",
        "Platform": "ios",
        "SID": "1716878004190-33976",
        "TS": "undefined",
        "Authorization": "Bearer " + token
    }
    data_5 = {
        "couponCode": "freestan",
        "amount": 4000
    }
    response_add_money = requests.post(url_add_money, headers=headers_add_money, data=json.dumps(data_5))
    logger.info(f"Response add_money status: {response_add_money.status_code}")



