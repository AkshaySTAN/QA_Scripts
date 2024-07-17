import requests
import json


def generate_token(phone):
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

    # Print the response headers for debugging
    print(f"Response Headers: {response.headers}")

    if response.status_code == 200:
        # Decompress the GZIP response
        try:
            response_body = response.json()
            return response_body.get("access_token")
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            raise
    else:
        print(f"Response Body: {response.text}")
        raise Exception(f"Failed to generate token. Status code: {response.status_code}")
