from api.client import get_client


def fetch_endpoint(endpoint, api_key):
    return get_client(api_key).fetch_endpoint(endpoint)


def get_user(api_key, user_id="me"):
    status_code, response = fetch_endpoint(f"users/{user_id}", api_key)
    return status_code, response


def check_api_key(api_key):
    status_code, response = get_user(api_key, "me")
    return status_code == 200
