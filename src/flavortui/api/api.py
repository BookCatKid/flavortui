from urllib.parse import urlencode

from flavortui.api.client import get_client

# This file is surprisingly simple!

# simple helper func


def fetch_endpoint(endpoint, api_key):
    return get_client(api_key).fetch_endpoint(endpoint)


# User stuff


def get_user(api_key, user_id="me"):
    status_code, response = fetch_endpoint(f"users/{user_id}", api_key)
    return status_code, response


def get_users(api_key, query="", page=1):
    params = urlencode({"page": page, "query": query})
    return fetch_endpoint(f"users?{params}", api_key)


# Store stuff


def get_store(api_key):
    return fetch_endpoint("store", api_key)


# don't think I'll ever use this but ok?
def get_store_item(api_key, item_id):
    return fetch_endpoint(f"store/{item_id}", api_key)


# Projects


def get_project(api_key, project_id):
    return fetch_endpoint(f"projects/{project_id}", api_key)


def get_projects_for_user(api_key, user_id="me"):
    user = get_user(api_key, user_id)
    projects = []
    for project_id in user[1]["project_ids"]:
        projects.append(get_project(api_key, project_id))
    return projects


def get_projects(api_key, page=1, query=""):
    params = urlencode({"page": page, "query": query})
    return fetch_endpoint(f"projects?{params}", api_key)


# Devlogs


def get_project_devlogs(api_key, project_id):
    return fetch_endpoint(f"projects/{project_id}/devlogs", api_key)


def get_devlogs(api_key, page=1):
    params = urlencode({"page": page})
    return fetch_endpoint(f"devlogs?{params}", api_key)


# Check api key


def check_api_key(api_key):
    return get_user(api_key, "me")[0] == 200
