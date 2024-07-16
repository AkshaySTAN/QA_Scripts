import requests

AdminHeader = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Authorization": "Bearer null",
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "User-Agent": "API test",
    "Content-Length": "*"
}

AdminData = {"email": "akshay@getstan.app",
             "password": "TPiuOv"
             }


AdminUrl = 'https://stage-admin.getstan.app/admin-api/login'

LoginToPanel = requests.post(url=AdminUrl, headers=AdminHeader, json=AdminData)
response = LoginToPanel.json()

# Extract the 'secretToken' field
secret_token = response['result']['data']['secretToken']
print(secret_token)