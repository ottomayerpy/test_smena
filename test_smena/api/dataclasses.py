from dataclasses import dataclass
from typing import List

@dataclass
class Client:
    """  """
    name: str
    phone: str


@dataclass
class Item:
    """  """
    name: str
    quantity: int
    unit_price: int


@dataclass
class Order:
    """ Класс для отслеживания заказа. """
    id: int
    price: int
    address: str
    client: Client
    items: List[Item]
    point_id: int

    def create(data):
        return Order(
            id=int(data['id']),
            price=int(data['price']),
            address=data['address'],
            client = Client(
                name=data['client']['name'],
                phone=data['client']['phone'],
            ),
            items=[Item(
                name=item['name'],
                quantity=int(item['quantity']),
                unit_price=int(item['unit_price']),
            ) for item in data['items']],
            point_id=int(data['point_id']),
        )
