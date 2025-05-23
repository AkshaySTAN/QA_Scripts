import requests
import json
import asyncio
from token_generation import main as get_tokens_main # Assuming get_tokens_main is an async function
import io
import sys

# def get_tokens_sync():
# return asyncio.run(get_tokens_main())

async def check_raffles_and_notify(target_jackpot_ids=None, tickets_to_buy=1, winner_jackpot_offset=-5, num_users_for_tokens=None, starting_user_id_for_tokens=None):
    """
    Performs raffle checks: fetches live jackpots, makes users participate, and fetches winners.
    Args:
        target_jackpot_ids (list, optional): A list of specific jackpot IDs to target. 
                                            If None or empty, all live running jackpots are targeted.
        tickets_to_buy (int, optional): Number of tickets each user should buy. Defaults to 1.
        winner_jackpot_offset (int, optional): Offset used when fetching winners. 
                                                (e.g., if jackpot_id is 100 and offset is -5, it fetches for 95).
                                                Defaults to -5.
        num_users_for_tokens (int, optional): Number of users to generate tokens for. 
                                              If None, token_generation script might use its default or prompt.
        starting_user_id_for_tokens (int, optional): Starting user ID for token generation.
                                                   If None, token_generation script might use its default or prompt.
    Returns:
        str: A string containing the logs of participation and winner fetching.
    """
    # Directly await the async token generation function
    # Pass the new parameters to get_tokens_main
    tokens = await get_tokens_main(usr_range=num_users_for_tokens, start_id=starting_user_id_for_tokens) 
    if not tokens:
        # Instead of raising an exception, return an error message string
        return "Error: No tokens fetched!"

    output_log = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = output_log

    try:
        # 1. Get all live jackpots and store their IDs (using the first token)
        token = tokens[0]
        url = "https://stage-api.getstan.app/reward-service/api/v1/raffle"
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        # Extract jackpot IDs
        live_jackpot_ids = []
        print("extracting jackpot ids")
        if "ongoing" in data:
            for jackpot in data["ongoing"]:
                if jackpot.get("status") == "RUNNING":
                    live_jackpot_ids.append(jackpot.get("id"))
        
        # Use target_jackpot_ids if provided and not empty, otherwise use all live_jackpot_ids
        jackpot_ids_to_process = [jid for jid in target_jackpot_ids if jid in live_jackpot_ids] if target_jackpot_ids else live_jackpot_ids

        if not jackpot_ids_to_process:
            print("No matching live jackpots found for the provided target IDs, or no live jackpots available.")
            # return # Exit if no jackpots to process

        print("Processing Jackpot IDs:", jackpot_ids_to_process)

        # 2. Make each user (token) participate in each live jackpot and store responses
        # with open("participation_responses.txt", "w") as f: # Writing to string buffer instead
        for jackpot_id in jackpot_ids_to_process:
            for idx, user_token in enumerate(tokens):
                url_participate = "https://stage-api.getstan.app/reward-service/api/v1/raffle/participate"
                payload = json.dumps({
                    "jackpotId": jackpot_id,
                    "ticketsBought": tickets_to_buy
                })
                headers_participate = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {user_token}'
                }
                response = requests.post(url_participate, headers=headers_participate, data=payload)
                log_entry = {
                    "user_index": idx + 1,
                    "jackpot_id": jackpot_id,
                    "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text
                }
                # f.write(json.dumps(log_entry) + "\n")
                print(json.dumps(log_entry)) # Print to our string buffer
                # print(f"User {idx+1} participate response for Jackpot {jackpot_id}: {response.text}")

        # 3. Fetch winners for each jackpot and store in winners.txt
        # with open("winners.txt", "w") as wf: # Writing to string buffer instead
        for jackpot_id in jackpot_ids_to_process:
            # Apply the offset for fetching winners
            effective_jackpot_id_for_winners = jackpot_id + winner_jackpot_offset
            url_winners = f"https://stage-api.getstan.app/reward-service/api/v1/raffle/participants?listType=WINNERS&limit=100&offset=0&jackpotId={effective_jackpot_id_for_winners}"
            response = requests.get(url_winners, headers=headers)
            print(f"Fetching winners for effective jackpot ID {effective_jackpot_id_for_winners} (original: {jackpot_id}), status: {response.status_code}")
            try:
                data = response.json()
                print(f"API response for effective jackpot ID {effective_jackpot_id_for_winners}:", data)
                if isinstance(data, list):
                    winners = data
                else:
                    winners = data.get("participants", [])
                for winner in winners:
                    winner_entry = {
                        "jackpot_id": jackpot_id, # Log with original jackpot_id for clarity
                        "effective_jackpot_id_for_winners": effective_jackpot_id_for_winners,
                        "name": winner.get("name"),
                        "profilePic": winner.get("profilePic"),
                        "ticketsBought": winner.get("ticketsBought"),
                        "ticketsWon": winner.get("ticketsWon"),
                        "currencySpent": winner.get("currencySpent"),
                        "currencyWon": winner.get("currencyWon")
                    }
                    # wf.write(json.dumps(winner_entry) + "\n")
                    print(json.dumps(winner_entry)) # Print to our string buffer
            except Exception as e:
                # wf.write(json.dumps({"jackpot_id": jackpot_id, "effective_jackpot_id_for_winners": effective_jackpot_id_for_winners, "error": str(e)}) + "\n")
                print(json.dumps({"jackpot_id": jackpot_id, "effective_jackpot_id_for_winners": effective_jackpot_id_for_winners, "error": str(e)}))
    finally:
        sys.stdout = original_stdout # Restore stdout
        result_string = output_log.getvalue()
        output_log.close()

    return result_string


# Example of how to call it (optional, for testing)
if __name__ == '__main__':
    # Test with specific jackpot IDs
    # test_target_ids = [626, 627]
    # test_tickets = 2
    # test_offset = -1
    # result = asyncio.run(check_raffles_and_notify(target_jackpot_ids=test_target_ids, tickets_to_buy=test_tickets, winner_jackpot_offset=test_offset))
    
    # Test with default (all live jackpots)
    # Provide example values for the new parameters for standalone testing if needed
    result = asyncio.run(check_raffles_and_notify(num_users_for_tokens=2, starting_user_id_for_tokens=12444))
    print(result)
