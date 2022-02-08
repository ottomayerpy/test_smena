from django.template.loader import render_to_string
from django_rq import job

from .models import Check, DataOrder
from .wkhtmltopdf import html_to_pdf


@job
def create_checks(order: DataOrder) -> None:
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
