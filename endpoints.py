# urls.py

BASE_URL = "https://stage-api.getstan.app/api/v4/communities/"
ENDPOINTS = {
    "community_join": f"{BASE_URL}join-community",
    "send_reaction": f"{BASE_URL}message/react",
    "send_message": f"{BASE_URL}message/send",
    "remove_member": f"{BASE_URL}remove-member",
    "get_comments": f"{BASE_URL}comments",
    "delete": f"{BASE_URL}delete"
    # add other endpoints here
}

VERIFY_OTP = "https://stage-api.getstan.app/api/v4/verify/otp"
