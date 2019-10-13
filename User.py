from models import WarframeMarketCore, logger


class User(WarframeMarketCore):
    def __init__(self, username: str, platform: str = 'pc', region: str = 'en'):
        super(User, self).__init__()
        self.username = username
        self.platform = platform
        self.region = region
        self.orders_json = {}

    def get_profile(self) -> dict:
        logger.info(f'Getting info for profile: {self.username}')
        url = self._build_url('profile', self.username)
        return self._json(self._get(url), 200)

    def get_orders(self, force=False):
        if self.orders_json and not force:
            return self.orders_json
        logger.info(f'Getting orders for profile: {self.username}')
        url = self._build_url('profile', self.username, 'orders')
        self.orders_json = self._json(self._get(url), 200)
        return self.orders_json

    def get_statistics(self) -> dict:
        logger.info(f'Getting statistics for profile: {self.username}')
        url = self._build_url('profile', self.username, 'statistics')
        return self._json(self._get(url), 200)

    def get_achievements(self) -> dict:
        logger.info(f'Getting achievements for profile: {self.username}')
        url = self._build_url('profile', self.username, 'achievements')
        return self._json(self._get(url), 200)

    def get_reviews(self) -> dict:
        logger.info(f'Getting reviews for profile: {self.username}')
        url = self._build_url('profile', self.username, 'reviews')
        return self._json(self._get(url), 200)

    def change_bio(self, message: str) -> dict:
        """Change the current user's profile bio and return JSON of the new bio: "{'about': '<p>Hello World</p>', 'about_raw': 'Hello World'}"."""
        logger.info(f'Changing profile bio for user {self.username}')
        url = self._build_url('profile', 'customization', 'about')
        payload = {
            'about': message
        }
        return self._json(self._post(url, payload), 200)

    def get_settings(self) -> dict:
        """
        Get the user's settings.
        Returns error for now.
        """
        logger.info(f'Getting settings for user {self.username}')
        url = self._build_url('settings')
        return self._json(self._get(url), 200)

    def change_settings(self, platform: str, region: str) -> dict:
        logger.info(f'Changing settings for user {self.username} ({self.platform} -> {platform}, {self.region} -> {region})')
        url = self._build_url('settings', 'verification')
        payload = {
            'platform': platform,
            'region': region
        }
        return self._json(self._patch(url, payload), 200)

    def remove_patreon(self):
        url = self._build_url('settings', 'account', 'patreon')
        return self._json(self._delete(url), 200)

    def _set_status(self, status: str) -> None:
        logger.info(f'Setting status of user {self.username} to {status}')
        websocket = self._open_ws(platform=self.platform)
        websocket.send(f'{{"type":"@WS/USER/SET_STATUS","payload":"{status}"}}')
        websocket.close()
        logger.info(f'Status of user {self.username} successfully changed to {status}')

    def set_ingame(self) -> None:
        self._set_status('ingame')

    def set_online(self) -> None:
        self._set_status('online')

    def set_offline(self) -> None:
        self._set_status('offline')

    def change_review_visibility(self, review_id: str, visible: bool) -> dict:
        logger.info(f'Changing review {review_id} to {"visible" if visible else "invisible"}')
        url = self._build_url('profile', self.username, 'review', review_id)
        payload = {
            'hidden': not visible
        }
        return self._json(self._put(url, payload), 200)

    def change_review_on_user(self, username: str, review_id: str, text: str) -> dict:
        """
        Change the text of a review that you wrote for a user.
        There's no endpoint to find the ids of reviews that you wrote, so it's UNTESTED and I'm not sure the endpoint works
        """
        logger.info(f'Changing review {review_id} of user {username} to "{text}"')
        url = self._build_url('profile', username, 'review', review_id)
        payload = {
            'text': text
        }
        return self._json(self._put(url, payload), 200)

    def delete_review_on_user(self, username: str, review_id: str) -> dict:
        """
        Delete the review with the given id that you wrote for a user.
        There's no endpoint to find the ids of reviews that you wrote.
        """
        logger.info(f'Deleting review {review_id} of user {username}')
        url = self._build_url('profile', username, 'review', review_id)
        return self._json(self._delete(url), 200)

    def get_order_by_id(self, order_id: str) -> dict:
        self.get_orders()
        for order_type, orders in self.orders_json.items():
            for order in orders:
                if order['id'] == order_id:
                    return order
