from django.template.loader import render_to_string
from django_rq import job

from .dataclasses import Order
from .models import Check, Printer
from .wkhtmltopdf import html_to_pdf


@job
def create_checks(order: Order) -> None:
    """ Создать чеки. Функция для асинхронного обработчика django_rq

    Args:
        order (DataOrder): Данные о заказе
    """
    # Общий контекст для обоих типов чеков
    context = {
        'number': order.id,
        'address': order.address,
        'items': order.items,
        'price': order.price,
        'name': order.client.name,
        'phone': order.client.phone,
    }

    # Редер данных из контекста в шаблон
    rendered_template_client = render_to_string('client_check.html', context)

    # Конвертирование шаблона в pdf документ
    pdf_file_client = html_to_pdf(rendered_template_client, order, 'client')

    check_client = Check.get_check_by_order_id(order.id)
    check_client.pdf_file = pdf_file_client
    check_client.status = 'rendered'
    check_client.save()

    # Создаем чек для кухни
    rendered_template_kitchen = render_to_string('kitchen_check.html', context)
    pdf_file_kitchen = html_to_pdf(rendered_template_kitchen, order, 'kitchen')

    Check.objects.create(
        printer_id=check_client.printer_id,
        type='kitchen',
        order=check_client.order,
        status='rendered',
        pdf_file=pdf_file_kitchen,
    )


def get_ids() -> list:
    """ Возвращает список из ID всех заказов

    Returns:
        list: ID всех заказов
    """
    return [check.order['id'] for check in Check.objects.all()]


def get_new_ids(api_key: str) -> dict:
    """ Возвращает словарь со списком из ID всех новых заказов

    Args:
        api_key (str): API ключ принтера

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


def check_printer(point_id: int) -> bool:
    """ Проверяет существует ли принтер по ID точке

    Args:
        point_id (int): ID точка принтера

    Returns:
        bool: True значит существует
    """
    return Printer.objects.filter(point_id=point_id).count() > 0
