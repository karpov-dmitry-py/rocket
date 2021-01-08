import os.path
import json
import requests

from .helpers import _log
from .helpers import _err

API_KEY = '85b11ee4b684d93c8f99044a3a4015aa'
API_BASE_URL = 'https://proxymania.ru/api'
PROXY_SOURCE = 'proxies.json'


class ProxyManager:

    def __init__(self, get_from_api=True, save_to_fs=False):
        self._key = API_KEY
        self._api_base_url = API_BASE_URL
        self._proxies = None
        self._save_to_fs = save_to_fs
        self._set_session()

        if get_from_api:
            self._get_proxies_from_api()
        else:
            self._get_proxies_from_fs()

    def _set_session(self):
        self._session = requests.Session()

    def _get_proxies_from_api(self):
        url = f'{self._api_base_url}/get_proxies/{self._key}/?extended=1'
        response = self._session.get(url)
        if response.status_code != 200:
            err_msg = f'Non-200 response received from proxy provider. ' \
                      f'Provider API: {url}' \
                      f'Response text: {response.text}'
            _err(err_msg)
            return

        proxies_from_api = response.json()
        if not proxies_from_api:
            _err(f'No available proxies retrieved from provider API: {url}')
            return
        proxies = []
        for _dict in proxies_from_api:
            user = _dict.get('username')
            pswd = _dict.get('password')
            address = _dict.get('http')
            full_url = f'http://{user}:{pswd}@{address}'
            proxy = {
                'http': full_url,
                'https': full_url,
            }
            proxies.append(proxy)
        self._proxies = proxies
        if self._save_to_fs:
            self._save_proxies_to_fs()

    @staticmethod
    def _get_proxies_full_path():
        return os.path.join(os.path.dirname(__file__), PROXY_SOURCE)

    def _get_proxies_from_fs(self):
        file_path = self._get_proxies_full_path()
        try:
            with open(file_path, 'r') as source:
                self._proxies = json.load(source)
                _log(f'Read proxies from file: {file_path}')
        except (FileExistsError, FileNotFoundError, OSError, Exception) as err:
            _err(f'Failed to read proxies from file: {file_path}. Error: {str(err)}')

    def _save_proxies_to_fs(self):
        file_path = self._get_proxies_full_path()
        try:
            with open(file_path, 'w') as f:
                json.dump(self._proxies, f)
                _log(f'Saved proxies to file: {file_path}')
        except (FileExistsError, FileNotFoundError, OSError, Exception) as err:
            _err(f'Failed to save proxies to file: {file_path}. Error: {str(err)}')

    def get_proxies(self):
        return self._proxies


def main():
    # manager = ProxyManager(get_from_api=False)
    # proxies = manager.get_proxies()
    pass


if __name__ == '__main__':
    main()
