from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import service
from .dataclasses import Order
from .serializers import CheckSerializer
from .service import check_printer, get_check_by_order_id, get_ids, get_new_ids


class CheckViews(APIView):
    def get(self, request):
        check_id = request.GET.get('check_id', None)
        api_key = request.GET.get('api_key', None)

        if check_id:
            check = get_check_by_order_id(int(check_id))
            if check is None:
                return Response({'error': 'Данного чека не существует'}, status=status.HTTP_400_BAD_REQUEST)
            if check.printer_id.api_key == api_key:
                if check.status == 'new':
                    return HttpResponse(check.pdf_file, content_type='application/pdf')
                return Response({'error': 'Для данного чека не сгенерирован PDF-файл'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'error': 'Ошибка авторизации'}, status=status.HTTP_401_UNAUTHORIZED)


class NewChecksViews(APIView):
    def get(self, request):
        api_key = request.GET.get('api_key', None)

        checks = get_new_ids(api_key)
        if checks is None:
            return Response({'error': 'Ошибка авторизации'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'ok': checks}, status=status.HTTP_200_OK)


class CreateChecksViews(APIView):
    def post(self, request):
        order = Order.create(request.data)

        serializer = CheckSerializer(data={
            'printer_id': order.point_id,
            'order': request.data,
            'type': 'client',
            'status': 'new',
        })

        if serializer.is_valid():
            if order.id in get_ids():
                return Response({'error': 'Для данного заказа уже созданы чеки'}, status=status.HTTP_400_BAD_REQUEST)
            if not check_printer(order.point_id):
                return Response({'error': 'Для данной точки не настроено ни одного принтера'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            service.create_checks.delay(order)
            return Response({'ok': 'Чеки успешно созданы'}, status=status.HTTP_200_OK)

        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
