import json
import logging
import requests
import pytest
import tokenGeneration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
API_BASE_URL = "https://stage-api.getstan.app/api"
APP_VERSION = "121"
PLATFORM = "ios"
SID = "1716878004190-33976"
TS = "undefined"


def get_headers(token, content_type="application/json", game_id=None):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": content_type,
        "gaid": "",
        "AppVersion": APP_VERSION,
        "Platform": PLATFORM,
        "SID": SID,
        "TS": TS,
        "Authorization": "Bearer " + token
    }
    if game_id:
        headers["gameId"] = game_id
    return headers


async def run_crate_operations(token):
    try:
        headers = get_headers(token)

        # Fetch club_pass balance before operations
        url_pass = f"{API_BASE_URL}/v4/club-pass/balance"
        response_pass_before = requests.get(url_pass, headers=headers)
        logger.info(f"Response club-pass/balance before status: {response_pass_before.status_code}")
        response_pass_before.raise_for_status()

        before_response_pass = response_pass_before.json()
        club_pass_before = before_response_pass.get('club_pass')

        logger.info(f"Club pass balance before: {before_response_pass}")

        # Get crate details
        url_crates = f"{API_BASE_URL}/v4/store/crates?"
        response_crates = requests.get(url_crates, headers=headers)
        logger.info(f"Response crates status: {response_crates.status_code}")
        response_crates.raise_for_status()

        # Buy crate
        url_crate_buy = f"{API_BASE_URL}/v1/crates/buy"
        data_buy = {
            "crateId": 5,
            "count": 1,
            "crateName": "Gold Crate",
            "gameId": "freefire"
        }
        response_crate_buy = requests.post(url_crate_buy, headers=headers, json=data_buy)
        logger.info(f"Response crate_buy status: {response_crate_buy.status_code}")
        logger.info(f"Response crate_buy body: {response_crate_buy.text}")
        response_crate_buy.raise_for_status()

        response_data = response_crate_buy.json()
        user_card_id = response_data.get('id')
        if user_card_id is None:
            raise ValueError("ID not found in the response")

        # Get upgrades before opening the crate
        url_crate_upgrades = f"{API_BASE_URL}/v3/user/upgrades"
        headers_upgrades = get_headers(token, game_id="freefire")
        response_crate_upgrades_before = requests.get(url_crate_upgrades, headers=headers_upgrades)
        logger.info(f"Response before crate_upgrades status: {response_crate_upgrades_before.status_code}")
        logger.info(f"Response before crate_upgrades body: {response_crate_upgrades_before.text}")
        response_crate_upgrades_before.raise_for_status()

        previous_upgrades = response_crate_upgrades_before.json()

        # Open crate
        url_crates_open = f"{API_BASE_URL}/v1/crates/open"
        data_open = {
            "crateId": user_card_id,
            "gameId": "freefire",
            "count": 1
        }
        response_crate_open = requests.post(url_crates_open, headers=headers, json=data_open)
        logger.info(f"Response crate_open status: {response_crate_open.status_code}")
        logger.info(f"Response crate_open body: {response_crate_open.text}")
        response_crate_open.raise_for_status()

        upgrades_open = response_crate_open.json().get('upgrades', 0)

        response_pass_after = requests.get(url_pass, headers=headers)
        logger.info(f"Response club-pass/balance after status: {response_pass_after.status_code}")
        response_pass_after.raise_for_status()

        after_response_pass = response_pass_after.json()
        club_pass_after = after_response_pass.get('club_pass')

        logger.info(f"Club pass balance after: {club_pass_after}")

        # Get upgrades after opening the crate
        response_crate_upgrades_after = requests.get(url_crate_upgrades, headers=headers_upgrades)
        logger.info(f"Response after crate_upgrades status: {response_crate_upgrades_after.status_code}")
        logger.info(f"Response after crate_upgrades body: {response_crate_upgrades_after.text}")
        response_crate_upgrades_after.raise_for_status()

        current_upgrades = response_crate_upgrades_after.json()

        # Validate club pass balance
        if club_pass_after < club_pass_before:
            logger.info(f'Club pass balance after ({club_pass_after}) is less than  ({club_pass_before}).')
        else:
            logger.error('Club pass balance did not decrease as expected.')

        # Validate upgrades count
        if current_upgrades == previous_upgrades + upgrades_open:
            logger.info(f'Current upgrades {current_upgrades} is equal to {previous_upgrades} + {upgrades_open}')
            logger.info('...........Upgrades count is correct..................')
        else:
            logger.error('Incorrect count got added???????????')

        assert current_upgrades == previous_upgrades + upgrades_open
        logger.info(".............Test case passed.........")

    except requests.RequestException as e:
        logger.error(f"An error occurred during API requests: {e}")
    except ValueError as e:
        logger.error(f"Value error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
