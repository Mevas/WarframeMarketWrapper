import ast
import json

import utility
from Order import Order
from User import User
from models import WarframeMarketCore, logger


class SearchConstraints:
    def __init__(self, min_ducat_data_ratio: float, max_price_to_start_search: int, min_ratio_per_item: float, min_stock: int, min_ducats: int, max_ducats: int):
        self.min_ratio_per_item = min_ratio_per_item
        self.min_stock = min_stock
        self.min_ducats = min_ducats
        self.max_ducats = max_ducats
        self.max_price_to_start_search = max_price_to_start_search
        self.min_ducat_data_ratio = min_ducat_data_ratio


class Market(WarframeMarketCore):
    def __init__(self, user: User):
        super(Market, self).__init__()
        self.logger = utility.validate_logger(logger)
        self.user = user

        self._load_item_data()
        self._load_mod_data()
        self.update_ducat_data()

        self.logger.debug('Market instance initialized')

    def get_item_data(self, item: str) -> dict:
        self.logger.info(f'Getting data for item: {item}')
        url = self._build_url('items', item, normalize=True)
        return self._json(self._get(url), 200)

    def get_item_orders(self, item: str) -> dict:
        self.logger.info(f'Getting orders for item: {item}')
        url = self._build_url('items', item, 'orders', normalize=True)
        return self._json(self._get(url), 200)

    def get_item_statistics(self, item: str) -> dict:
        self.logger.info(f'Getting statistics for item: {item}')
        url = self._build_url('items', item, 'statistics', normalize=True)
        return self._json(self._get(url), 200)

    def get_all_items_data(self) -> dict:
        self.logger.info(f'Getting data for all items')
        url = self._build_url('items')
        return self._json(self._get(url), 200)

    def get_all_ducat_data(self) -> dict:
        self.logger.info(f'Getting ducat data for all items')
        url = self._build_url('tools', 'ducats')
        return self._json(self._get(url), 200)

    def get_market_statistics(self) -> dict:
        self.logger.info(f'Getting global market statistics')
        url = self._build_url('statistics')
        return self._json(self._get(url), 200)

    def get_most_recent_orders(self) -> dict:
        """Get the 500 most recent orders. Updates every 3 minutes."""
        self.logger.info(f'Getting the most recent orders')
        url = self._build_url('most_recent')
        return self._json(self._get(url), 200)

    def get_site_user_statistics(self) -> dict:
        websocket = self._open_ws(platform=self.user.platform)
        return ast.literal_eval(websocket.recv())['payload']

    def place_new_order(self, item_id: str, order_type: str, platinum: int, quantity: int, visible: bool = True) -> Order:
        """Place a new order and return the JSON of placed order."""
        return Order(self.user.username).new(item_id, order_type, platinum, quantity, visible)

    def get_order_by_id(self, order_id: str, username: str = None) -> dict:
        if username is None:
            username = self.user.username
        return User(username).get_order_by_id(order_id)

    def update_ducat_data(self) -> None:
        with open('ducat_data.json', 'w+') as file:
            json.dump(self.get_all_ducat_data(), file)
        self.logger.info(f'Updated ducat data')
        self._load_ducat_data()

    def update_item_data(self) -> None:
        with open('item_data.json', 'w+') as file:
            json.dump(self.get_all_items_data(), file)
        self.logger.info(f'Updated item data')
        self._load_item_data()

    def get_ducat_data_by_id(self, item_id: str) -> int:
        self.logger.debug(f'Getting ducat price for item with id {item_id}')
        return self.ducat_data_df[self.ducat_data_df.id == item_id]['ducats'].values[0]

