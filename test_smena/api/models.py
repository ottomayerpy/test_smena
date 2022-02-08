from dataclasses import dataclass
from typing import List

from django.db import models

CHECK_TYPES_CHOICES = (
    ('kitchen', 'kitchen'),
    ('client', 'client'),
)

STATUSES_CHOICES = (
    ('new', 'new'),
    ('rendered', 'rendered'),
    ('printed', 'printed'),
)


class Printer(models.Model):
    """ Принтер (Printer). Каждый принтер печатает только свой тип чеков.
    Поле api_key принимает уникальные значения, по нему однозначно определяется принтер.
    Для этой модели должны быть fixtures (принтеры для обоих типов чеков для нескольких точек). """
    name = models.CharField('Название принтера', max_length=255)
    api_key = models.CharField('Ключ доступа к API', max_length=1024, unique=True)
    check_type = models.CharField('Тип чека которые печатает принтер', choices=CHECK_TYPES_CHOICES, max_length=10)
    point_id = models.IntegerField('Точка к которой привязан принтер', unique=True)

    def __str__(self):
        return self.name

    def check_printer(point_id: int) -> bool:
        """ Проверяет существует ли принтер по ID точке

        Args:
            point_id (int): ID точка принтера

        Returns:
            bool: True значит существует
        """
        return Printer.objects.filter(point_id=point_id).count() > 0

    class Meta:
        verbose_name = 'Принтер'
        verbose_name_plural = 'Принтеры'
        ordering = ['-point_id',]


class Check(models.Model):
    """ Информация о заказе для каждого чека хранится в
    JSON, нет необходимости делать отдельные модели. """
    printer_id = models.ForeignKey(Printer, verbose_name='Принтер', on_delete=models.CASCADE)
    type = models.CharField('Тип чека', choices=CHECK_TYPES_CHOICES, max_length=10)
    order = models.JSONField('Информация о заказе')
    status = models.CharField('Статус чека', choices=STATUSES_CHOICES, default='new', max_length=10)
    pdf_file = models.FileField('Ссылка на созданный PDF-файл')

    def __str__(self):
        return str(self.printer_id)
    
    def get_ids() -> list:
        """ Возвращает список из ID всех заказов

        Returns:
            list: ID всех заказов
        """
        return [check.order['id'] for check in Check.objects.all()]

    def get_new_ids(api_key: str) -> dict:
        """ Возвращает словарь со списком из ID всех новых заказов

        Returns:
            dict: ID новых заказов
        """
        printer = Printer.objects.get(api_key=api_key)
        return {
            "checks": [{"id": check.order['id']} for check in Check.objects.filter(type='client', status='rendered', printer_id=printer)]
        }

    def get_check_by_order_id(order_id: int):
        """ Возвращает заказ по ID заказа

        Args:
            order_id (int): ID заказа

        Returns:
            object (Check): Объект из QuerySet
            None: Если нет совпадений
        """
        for check in Check.objects.filter(type='client'):
            if check.order['id'] == order_id:
                return check

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'
        ordering = ['-id',]


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
class DataOrder:
    """ Класс для отслеживания заказа. """
    id: int
    price: int
    address: str
    client: Client
    items: List[Item]
    point_id: int

    def create(data):
        return DataOrder(
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
