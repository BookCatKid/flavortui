import time
import json
import os
import requests
import hashlib
import threading
import urllib.parse

CACHE_DIR = ".cache"


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
            # In seconds, how long we should wait between requests. In general we go for double the "required" time.
            "projects": 24,
            "store": 24,
            "users_list": 24,
            "projects_id": 4,
            "store_id": 4,
            "default": 2,
        }

    def _ensure_cache_dir(self):
        os.makedirs(CACHE_DIR, exist_ok=True)

    def _get_cache_file(self, endpoint, format):
        hashed_key = hashlib.sha256(endpoint.encode()).hexdigest()
        return os.path.join(CACHE_DIR, f"{hashed_key}.{format}")

    def _save_to_cache(self, endpoint, response, status_code):
        self._ensure_cache_dir()
        file_name = self._get_cache_file(endpoint, "json")
        with open(file_name, "w") as file:
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
            with open(file_name, "r") as f:
                return json.load(f)
        return None

    def _get_endpoint_rate_limit(self, endpoint):
        parts = endpoint.split("/")
        base = parts[0]

        if base == "users":
            if len(parts) == 1:
                return self.rate_limits["users_list"]
            else:
                return self.rate_limits["default"]

        if base == "store":
            if len(parts) == 1:
                return self.rate_limits["store"]
            else:
                return self.rate_limits["store_id"]

        if base == "projects":
            if len(parts) == 1:
                return self.rate_limits["projects"]
            else:
                return self.rate_limits["projects_id"]

        # add other bases here later

        return self.rate_limits["default"]

    def _revalidate(self, endpoint):
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", headers=self.headers)
            self._save_to_cache(endpoint, response.json(), response.status_code)
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
            response = requests.get(url, headers=self.headers)
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
                response = requests.get(url)
                response.raise_for_status()
            except requests.ConnectionError:
                raise OfflineError("Could not connect to the Flavortown server.")
            with open(self._get_cache_file(url, ext), "wb") as f:
                f.write(response.content)
        return self._get_cache_file(url, ext)


_global_client = None


def get_client(api_key, settings=None):
    global _global_client
    if not _global_client or _global_client.api_key != api_key:
        _global_client = ApiClient(api_key, settings)
    elif settings is not None:
        _global_client.settings = settings
    return _global_client
