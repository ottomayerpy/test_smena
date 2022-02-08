from django.contrib import admin

from .models import Check, Printer


class PrinterAdmin(admin.ModelAdmin):
    list_display = ['name', 'check_type', 'point_id',]
    list_filter = [
        'name',
        'check_type',
        'point_id',
    ]
    class Meta:
        model = Printer


class CheckAdmin(admin.ModelAdmin):
    list_display = ['printer_id', 'type', 'status',]
    list_filter = [
        'printer_id',
        'type',
        'status',
    ]
    class Meta:
        model = Check


admin.site.register(Printer, PrinterAdmin)
admin.site.register(Check, CheckAdmin)
