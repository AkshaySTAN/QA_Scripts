import json

import pytest
import pytest
import random
import requests
import logging
import colorlog

from app_testing.Shashi.projectNewShashi.conftests import send_otp, BASE_URL, GAID, APP_VERSION, PLATFORM, SID, REFERRAL_CODE, \
    NAME

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


def test_send_otp(phone_number):
    response = send_otp(phone_number)
    assert response.status_code == 200


def test_verify_otp(phone_number, authorization_token):
    assert authorization_token is not None


def test_get_avatar(authorization_token):
    url = f"{BASE_URL}/v4/home/avatar"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "gaid": GAID,
        "AppVersion": APP_VERSION,
        "Platform": PLATFORM,
        "SID": SID,
        "TS": "undefined",
        "Authorization": f"Bearer {authorization_token}"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    logger.info("Avatar information retrieved")


def test_apply_referral_code(authorization_token):
    url = f"{BASE_URL}/v4/user/apply/referral/code"
    payload = {"code": REFERRAL_CODE}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "gaid": GAID,
        "AppVersion": APP_VERSION,
        "Platform": PLATFORM,
        "SID": SID,
        "TS": "undefined",
        "Authorization": f"Bearer {authorization_token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200
    logger.info("Referral code applied successfully")


def test_user_profile_update(authorization_token):
    url = f"{BASE_URL}/v1/users/update-profile-v2"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "gaid": GAID,
        "AppVersion": "122",
        "Platform": "ios",
        "SID": SID,
        "TS": "undefined",
        "Authorization": f"Bearer {authorization_token}"
    }
    payload = {
        "profilePic": "https://stage-bucket.sgp1.cdn.digitaloceanspaces.com/CMS/avtar3.png?1715174778418",
        "name": NAME
    }
    response = requests.put(url, data=json.dumps(payload), headers=headers)
    assert response.status_code == 200
    logger.info("Profile updated successfully")


def test_user_referral_history(authorization_token):
    url = f"{BASE_URL}/v4/user/referral/history?limit=10&offset=0"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "gaid": GAID,
        "AppVersion": APP_VERSION,
        "Platform": PLATFORM,
        "SID": SID,
        "TS": "undefined",
        "Authorization": f"Bearer {authorization_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch referral history. Status code: {response.status_code}")
        logger.error(f"Response text: {response.text}")
        return
    response_data = response.json()
    logger.debug(f"Referral history response data: {response_data}")
    if not response_data:
        logger.info("Referral history is empty")
        return
    for referral_cash in response_data:
        if isinstance(referral_cash, dict):
            referral_cash_received = referral_cash.get("credited")
            if referral_cash_received == 1:
                logger.info("Referral credited successfully")
            else:
                logger.info("Not credited")
        else:
            logger.error(f"Unexpected data format: {referral_cash}")


def test_process_user(phone_number, authorization_token):
    test_send_otp(phone_number)
    test_verify_otp(phone_number, authorization_token)
    test_get_avatar(authorization_token)
    test_apply_referral_code(authorization_token)
    test_user_profile_update(authorization_token)
    test_user_referral_history(authorization_token)
    logger.info(f"Processed user with phone number {phone_number}")


@pytest.mark.parametrize("user_number", range(1, 2))
def test_users(user_number, phone_number, authorization_token):
    test_process_user(phone_number, authorization_token)
