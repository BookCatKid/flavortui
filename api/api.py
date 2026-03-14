from api.client import get_client

# This file is suprisingly simple for now!

# simple helper func

def fetch_endpoint(endpoint, api_key):
    return get_client(api_key).fetch_endpoint(endpoint)

# User stuff

def get_user(api_key, user_id="me"):
    status_code, response = fetch_endpoint(f"users/{user_id}", api_key)
    return status_code, response

# Store stuff

def get_store(api_key):
    return fetch_endpoint("store", api_key)

# don't think I'll ever use this but ok?
def get_store_item(api_key, item_id):
    return fetch_endpoint(f"store/{item_id}", api_key)

# Check api key

def check_api_key(api_key):
    status_code, response = get_user(api_key, "me")
    return status_code == 200
