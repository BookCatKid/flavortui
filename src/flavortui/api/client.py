import hashlib
import json
import os
import threading
import time
import urllib.parse
from pathlib import Path

import requests
from platformdirs import user_cache_dir

CACHE_DIR = Path(user_cache_dir("flavortui"))
API_TIMEOUT = (3.05, 10)
IMAGE_TIMEOUT = (3.05, 20)


class OfflineError(Exception):
    pass


class ApiClient:
    def __init__(self, api_key, settings=None):
        self.api_key = api_key
        self.settings = settings or {}
        self.base_url = "https://flavortown.hackclub.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Flavortown-Ext-16596": "true",
        }
        self.is_offline = False

        self._ensure_cache_dir()

        self.rate_limits = {
            # In seconds, how long we should wait between requests.
            # In general we go for double the "required" time.
            "projects": 24,
            "store": 24,
            "users_list": 24,
            "projects_id": 4,
            "store_id": 4,
            "default": 2,
        }

    def _ensure_cache_dir(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cache_file(self, endpoint, file_format):
        hashed_key = hashlib.sha256(endpoint.encode()).hexdigest()
        return CACHE_DIR / f"{hashed_key}.{file_format}"

    def _save_to_cache(self, endpoint, response, status_code):
        self._ensure_cache_dir()
        file_name = self._get_cache_file(endpoint, "json")
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "timestamp": time.time(),
                    "data": response,
                    "status_code": status_code,
                },
                file,
            )

    def _load_from_cache(self, endpoint):
        file_name = self._get_cache_file(endpoint, "json")
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _get_endpoint_rate_limit(self, endpoint):
        parts = endpoint.split("/")
        base = parts[0]

        if base == "users":
            if len(parts) == 1:
                return self.rate_limits["users_list"]
            return self.rate_limits["default"]

        if base == "store":
            if len(parts) == 1:
                return self.rate_limits["store"]
            return self.rate_limits["store_id"]

        if base == "projects":
            if len(parts) == 1:
                return self.rate_limits["projects"]
            return self.rate_limits["projects_id"]

        # add other bases here later

        return self.rate_limits["default"]

    def _revalidate(self, endpoint):
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                timeout=API_TIMEOUT,
            )
            self._save_to_cache(endpoint, response.json(), response.status_code)
            self.is_offline = False
        except requests.ConnectionError:
            self.is_offline = True
        except Exception:
            pass

    def fetch_endpoint(self, endpoint):
        cached_file = self._load_from_cache(endpoint)
        caching_strategy = self.settings.get("caching_strategy", "timed")
        if cached_file:
            # default caching
            if (
                time.time() - cached_file["timestamp"]
                < self._get_endpoint_rate_limit(endpoint)
                and caching_strategy == "timed"
            ):
                return cached_file["status_code"], cached_file["data"]
            # extended caching
            if (
                time.time() - cached_file["timestamp"]
                < self._get_endpoint_rate_limit(endpoint) * 15
                and caching_strategy == "extended"
            ):
                return cached_file["status_code"], cached_file["data"]
            # swr caching
            if caching_strategy == "swr":
                if time.time() - cached_file[
                    "timestamp"
                ] >= self._get_endpoint_rate_limit(endpoint):
                    threading.Thread(
                        target=self._revalidate, args=(endpoint,), daemon=True
                    ).start()
                return cached_file["status_code"], cached_file["data"]

        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, timeout=API_TIMEOUT)
        except requests.ConnectionError as e:
            self.is_offline = True
            if cached_file:
                return cached_file["status_code"], cached_file["data"]
            raise OfflineError("Could not connect to the Flavortown server.") from e
        self.is_offline = False
        data = response.json()
        self._save_to_cache(endpoint, data, response.status_code)
        return response.status_code, data

    def fetch_image(self, url):
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lstrip(".") or "png"
        if not os.path.exists(self._get_cache_file(url, ext)):
            try:
                response = requests.get(url, timeout=IMAGE_TIMEOUT)
                response.raise_for_status()
            except requests.ConnectionError:
                raise OfflineError("Could not connect to the Flavortown server.")
            with open(self._get_cache_file(url, ext), "wb") as f:
                f.write(response.content)
        return self._get_cache_file(url, ext)


_GLOBAL_CLIENT = None


def get_client(api_key, settings=None):
    global _GLOBAL_CLIENT
    if not _GLOBAL_CLIENT or _GLOBAL_CLIENT.api_key != api_key:
        _GLOBAL_CLIENT = ApiClient(api_key, settings)
    elif settings is not None:
        _GLOBAL_CLIENT.settings = settings
    return _GLOBAL_CLIENT
