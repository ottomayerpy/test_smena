import base64
import json

import requests
from test_smena.settings import MEDIA_ROOT, WKHTMLTOPDF_URL

from .dataclasses import Order


def html_to_pdf(html: str, order: Order, type_check: str) -> str:
    """ Конвертирование html шаблона в pdf документ при помощи wkhtmltopdf воркера.

    Args:
        html (str): HTML шаблон
        order (DataOrder): Данные о заказе
        type_check (str): Тип чека (client/kitchen)

    Returns:
        path_file (str): Путь к pdf файлу
    """
    # Подготавливаем данные для wkhtmltopdf
    data = json.dumps({
        'contents': base64.b64encode(
            bytes(
                html,
                'utf-8',
            )
        ).decode('utf-8'),
    })

    # Отправляем в wkhtmltopdf шаблон
    response = requests.post(
        WKHTMLTOPDF_URL,
        data=data,
        headers={
            'Content-Type': 'application/json',
        },
    )

    # Сохраняем pdf в /media/pdf/
    path_file = f'{MEDIA_ROOT}pdf/{order.id}_{type_check}.pdf'
    with open(path_file, 'wb') as f:
        f.write(response.content)

    return path_file
