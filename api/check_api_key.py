from api.get_user import get_user


def check_api_key(api_key):
    status_code, response = get_user(api_key, "me")
    return status_code == 200
