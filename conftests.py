import pytest
import random
import requests
import logging
import colorlog

# Configure colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

BASE_URL = "https://stage-api.getstan.app/api"
APP_TYPE = "android"
DEVICE_UID = "23a178b4e8dff03a"
GAID = "c93d19fa-f0d4-44d4-817a-23229d92c90e"
APP_VERSION = "121"
PLATFORM = "android"
SID = "1720432325593-31579"
OTP = "2425"
REFERRAL_CODE = "7KZ96POP"
NAME = "Shashi"


def generate_random_phone_number():
    return "+91" + str(random.randint(1000000000, 9999999999))


@pytest.fixture
def phone_number():
    phone_number = generate_random_phone_number()
    logger.info(f"Generated Random Phone Number: {phone_number}")
    return phone_number


@pytest.fixture
def authorization_token(phone_number):
    otp_send_response = send_otp(phone_number)
    assert otp_send_response.status_code == 200

    url = f"{BASE_URL}/v4/verify/otp"
    payload = {
        "phone": phone_number,
        "otp": OTP,
        "integrityToken": None,
        "sessionId": None,
        "deviceInfo": {
            "APP_TYPE": APP_TYPE,
            "DeviceData": {
                "deviceUID": DEVICE_UID
            }
        },
        "utmPayload": {},
        "campaignUrl": ""
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "gaid": GAID,
        "AppVersion": APP_VERSION,
        "Platform": PLATFORM,
        "SID": SID,
        "TS": "undefined"
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    access_token = data.get("access_token")
    assert access_token is not None
    logger.info("OTP verified and access token received")
    return access_token


def send_otp(phone_number):
    url = f"{BASE_URL}/v1/auth/otp/send"
    payload = {"phone": phone_number}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    logger.info(f"OTP sent to {phone_number}")
    return response
