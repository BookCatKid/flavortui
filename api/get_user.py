from api.constants import fetch_endpoint


def get_user(api_key, user = "me"):
    status_code, response = fetch_endpoint(f"users/{user}", api_key)
    if status_code == 200:
        return response
    return None
