import requests

BASE_URL = "https://flavortown.hackclub.com/api/v1"

def fetch_endpoint(endpoint, api_key):
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    return response.status_code, response.json()
