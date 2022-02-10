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
    point_id = models.IntegerField('Точка к которой привязан принтер')

    def __str__(self):
        return self.name

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

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'
        ordering = ['-id',]
