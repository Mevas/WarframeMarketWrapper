from models import WarframeMarketCore, logger


class Order(WarframeMarketCore):
    def __init__(self, user, order_id: str = ''):
        super(Order, self).__init__()
        self.user = user
        self.order_id = order_id
        self.order_json = self.user.get_order_by_id(self.order_id) if self.order_id != '' else {}
        if self.order_json:
            self.item_id = self.order_json['item']['id']
            self.order_type = self.order_json['order_type']
            self.platinum = self.order_json['platinum']
            self.quantity = self.order_json['quantity']
            self.visible = self.order_json['visible']
            self.item_name = self.order_json['item']['en']['item_name']
        else:
            self.item_id = ''
            self.order_type = ''
            self.platinum = 0
            self.quantity = 0
            self.visible = True
            self.item_name = ''

    def __str__(self):
        return f'Order with id {self.order_id}: {self.item_name} x{self.quantity} at {self.platinum}p each set on {"visible" if self.visible else "invisible"} for a total of {self.quantity * self.platinum}p'

    def new(self, item_id: str, order_type: str, platinum: int, quantity: int, visible: bool = True):
        if self.order_id != '':
            logger.warning('Tried to create a new order when it already exists')
            return self

        logger.info(f'Placing a new {order_type} order of {item_id} x{quantity} for {platinum}p each and visible {visible}')
        self.item_id = item_id
        self.order_type = order_type
        self.platinum = platinum
        self.quantity = quantity
        self.visible = visible
        self.item_name = self.get_item_name_by_id(item_id)

        url = self._build_url('profile', 'orders')
        payload = {
            'order_type': self.order_type,
            'item_id': self.item_id,
            'platinum': self.platinum,
            'quantity': self.quantity,
            'visible': self.visible
        }
        self._json(self._post(url, payload), 200)
        return self

    def change(self, item_id: str = None, platinum: int = None, quantity: int = None, visible: bool = None):
        if item_id is None:
            item_id = self.order_json['item']['id']
        if platinum is None:
            platinum = self.order_json['platinum']
        if quantity is None:
            quantity = self.order_json['quantity']
        if visible is None:
            visible = self.order_json['visible']

        logger.info(f'Changing {self.order_type} order {self.order_id} to {self.item_name} x{quantity} for {platinum}p each and visible {visible} for a total of {quantity * platinum}p')
        url = self._build_url('profile', 'orders', self.order_id)
        payload = {
            'item_id': item_id,
            'platinum': platinum,
            'quantity': quantity,
            'visible': visible
        }
        self._json(self._put(url, payload), 200)
        return self

    def delete(self) -> dict:
        logger.info(f'Deleting {self.order_type} order {self.order_id}: {self.item_name} x{self.quantity} for {self.platinum}p each and visible {self.visible}')
        url = self._build_url('profile', 'orders', self.order_id)
        return self._json(self._delete(url), 200)
