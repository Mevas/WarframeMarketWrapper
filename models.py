import json
import pandas as pd

from websocket import create_connection

import requests

import exceptions
import utility

logger = utility.create_logger()


class WarframeMarketCore:
    item_data = {}
    mod_data = []
    ducat_data = {}
    ducat_data_df = pd.DataFrame()

    def __init__(self, session=None):
        self._market_url = 'https://api.warframe.market/v1'
        self.secret = ''
        self.session = session if session is not None else self.new_session()

    def _request(self, method: str, *args, **kwargs) -> requests.Response:
        try:
            request_method = getattr(self.session, method)
            return request_method(*args, **kwargs)
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
        ) as exc:
            raise requests.exceptions.ConnectionError(exc)
        except requests.exceptions.RequestException as exc:
            raise requests.exceptions.Timeout(exc)

    def _delete(self, url: str, **kwargs) -> requests.Response:
        logger.debug("DELETE %s with %s", url, kwargs)
        return self._request("delete", url, **kwargs)

    def _get(self, url: str, **kwargs) -> requests.Response:
        logger.debug("GET %s with %s", url, kwargs)
        return self._request("get", url, **kwargs)

    def _patch(self, url: str, data=None, json_: bool = True, **kwargs) -> requests.Response:
        if json_:
            data = json.dumps(data) if data is not None else data
        logger.debug("PATCH %s with %s", url, kwargs)
        return self._request("patch", url, data, **kwargs)

    def _post(self, url: str, data=None, json_: bool = True, **kwargs) -> requests.Response:
        if json_:
            data = json.dumps(data) if data is not None else data
        logger.debug("POST %s with %s, %s", url, data, kwargs)
        return self._request("post", url, data, **kwargs)

    def _put(self, url: str, data=None, json_: bool = True, **kwargs) -> requests.Response:
        if json_:
            data = json.dumps(data) if data is not None else data
        logger.debug("PUT %s with %s", url, kwargs)
        return self._request("put", url, data, **kwargs)

    def _get_secret(self) -> str:
        if self.secret == '':
            try:
                with open(f'secret.txt') as secret_file:
                    self.secret = secret_file.read()
            except IOError:
                self.secret = input('Enter secret: ')
                with open(f'secret.txt', 'w+') as secret_file:
                    secret_file.write(self.secret)

        return self.secret

    def _build_url(self, *args, **kwargs):
        normalize = kwargs.get('normalize', False)
        parts = [kwargs.get('base_url', self._market_url)]
        parts.extend(args)
        parts = [str(p).lower().replace(' ', '_') if normalize else str(p) for p in parts]

        return '/'.join(parts)

    @staticmethod
    def _json(response: requests.Response, expected_status_code: int) -> dict:
        decoded_json = response.json()

        status_code = response.status_code

        if status_code != expected_status_code:
            if status_code >= 400:
                return None
                # raise exceptions.generate_error(response)

            logger.warning(f'Expected status code {expected_status_code} but got {status_code}')

        if 'error' in decoded_json:
            logger.error(f'Request returned an error: {decoded_json}')
            raise Exception(f'Request returned an error: {decoded_json}')

        if 'payload' in decoded_json:
            return decoded_json['payload']

        if 'profile' in decoded_json:
            return decoded_json['profile']

        logger.warning('Request returned an empty response')
        return {}

    def _open_ws(self, platform: str = 'pc'):
        logger.debug('Opening websocket connection')
        return create_connection(f'wss://warframe.market/socket?platform={platform}', timeout=30, header=[f'Authorization: JWT {self.secret}'])

    def _load_item_data(self) -> None:
        with open('item_data.json', 'r') as data:
            data_json = json.load(data)
            for item in data_json['items']['en']:
                self.item_data[item['id']] = item['url_name']
        logger.info('Loaded item data')

    def _load_mod_data(self) -> None:
        with open('Mods.json', 'r', encoding='utf8') as data:
            data_json = json.load(data)
            for item in data_json:
                self.mod_data.append(item['name'])
                # self.mod_data[item['name']] = item['rarity']
        logger.info('Loaded mod data')

    def _load_ducat_data(self) -> None:
        with open('ducat_data.json', 'r') as data:
            row_list = []
            self.ducat_data = json.load(data)
            for item in self.ducat_data['previous_hour']:
                row_list.append({'id': item['item'], 'ducats': item['ducats'], 'dpp': item['ducats_per_platinum_wa']})
            self.ducat_data_df = pd.DataFrame(row_list, columns=['id', 'ducats', 'dpp'])
            self.ducat_data_df.sort_values('dpp', ascending=False, inplace=True)
            self.ducat_data_df.reset_index(inplace=True, drop=True)
        logger.info('Loaded ducat data')

    def get_item_name_by_id(self, item_id: str) -> str:
        return self.item_data[item_id]

    def new_session(self, platform='pc', language='en', auth=True):
        session = requests.session()
        session.headers.update({
            'Platform': platform,
            'Language': language,
            'Content-Type': 'application/json'
        })

        if auth:
            session.headers.update({
                'Authorization': f'JWT {self._get_secret()}',
            })

        return session
