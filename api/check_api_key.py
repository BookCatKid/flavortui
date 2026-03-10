from api.constants import fetch_endpoint


def check_api_key(api_key):
    status_code, response = fetch_endpoint("users/me", api_key)
    if status_code == 200:
        return True
    else:
        return False
