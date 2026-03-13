from api.constants import fetch_endpoint


def get_user(api_key, user_id="me"):
    status_code, response = fetch_endpoint(f"users/{user_id}", api_key)
    return status_code, response
