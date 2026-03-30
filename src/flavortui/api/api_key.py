import keyring

SERVICE = "flavortui"
ACCOUNT = "default"


def get_api_key():
    return keyring.get_password(SERVICE, ACCOUNT)


def save_api_key(key: str):
    keyring.set_password(SERVICE, ACCOUNT, key)


def delete_api_key():
    keyring.delete_password(SERVICE, ACCOUNT)
