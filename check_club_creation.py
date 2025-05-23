import requests

url = "https://stage-api.getstan.app/api/v5/club"

payload = {
    'title': 'Kohli_15',
    'tags': 'Ludo',
    'roomStatus': 'Live',
    'autoJoinStage': 'true',
    'pinnedMessage': '{"message":"","link":""}'
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'AppVersion': '180',
    'Platform': 'android',
    'SID': '1736166992009-27857',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiZ21pUHJvZmlsZUlkIjozMTk1LCJleHAiOjE3NDM4NDE2ODAsImZyZWVmaXJlUHJvZmlsZUlkIjozMjMxLCJpYXQiOjE3NDM3NTUyODAsImlkIjoxOTQzfQ.Jd74gcUgmZfrTm0gHz28EM8KGozBn9y_-XtLfCaGtOA'
}

# Convert payload items to tuples for multipart encoding
files = [(key, (None, value)) for key, value in payload.items()]

response = requests.post(url, headers=headers, files=files)

print(response.status_code)
print(response.text)