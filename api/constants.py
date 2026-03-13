from api.client import get_client

BASE_URL = "https://flavortown.hackclub.com/api/v1"

def fetch_endpoint(endpoint, api_key):
    return get_client(api_key).fetch_endpoint(endpoint)
