import json


class RequestBodyFactory:
    @staticmethod
    def create_request_body1():
        return {
            "cardPackId": 6,
            "quantity": 1,
            "isComboOffer": False,
            "gameId": "freefire"
        }

    @staticmethod
    def create_request_body2():
        return {
            "crateId": 4,
            "count": 1,
            "crateName": "Basic Crate",
            "gameId": "freefire"
        }

    @staticmethod
    def create_request_body3(first_user_card_id):
        return {
            "userCardId": first_user_card_id,
            "type": "SINGLE",
            "gameId": "freefire",
            "count": 1
        }

    @staticmethod
    def create_request_body4(latest_user_card_id):
        return {
            "minPrice": 10,
            "maxPrice": 10,
            "userCardId": latest_user_card_id,
            "autoSellAllowed": True,
            "biddingAllowed": False,
            "expiryTime": 24,
            "listingName": "Auto Trade",
            "cashoutType": "MONEY"
        }

    @staticmethod
    def create_request_body5(last_second_user_card_id):
        return {
            "userCardId": last_second_user_card_id,
            "type": "APPLY"
        }
