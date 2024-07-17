import requests
import json


async def buy_coins(token):
    url_add_money = "https://stage-api.getstan.app/api/v1/users/add-money"
    data = {
        "couponCode": "freestan",
        "amount": 8000
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "gaid": "",
        "AppVersion": "118",
        "Platform": "android",
        "SID": "1716878004190-33976",
        "TS": "undefined",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(url_add_money, headers=headers, json=data)

    print(f"Response add_money status: {response.status_code}")

    # Treat 201 as a successful status code
    if response.status_code != 200 and response.status_code != 201:
        raise Exception(f"Failed to add money. Status code: {response.status_code}")
