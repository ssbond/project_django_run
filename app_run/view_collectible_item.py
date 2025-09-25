from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CollectibleItem
from .serializers import CollectibleItemSerializer
from rest_framework.decorators import api_view
from openpyxl import load_workbook

class CollectibleItemApiViewSet(viewsets.ModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer
    pass

class UploadFileApiView(APIView):
    pass

@api_view(['POST'])
def upload_collectible_items_xls(request):
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file provided."}, status=400)

    workbook = load_workbook(file)
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)
    header = next(rows)  # Получаем заголовки столбцов
    header_data = []
    for h in header:
        header_data.append(h.lower())
        if h=='URL':
            header_data[-1]='picture'
    filedata = []
    for row in rows:
        filedata.append(dict(zip(header_data, row)))
    message = []
    for i, row in enumerate(filedata, start=2):  # start=2, т.к. 1 строка - заголовок
        serializer = CollectibleItemSerializer(data=row)
        if serializer.is_valid():
            serializer.save()
        else:
            errors = serializer.errors
            error_details = []
            for field_name, error_list in errors.items():
                # Ищем индекс поля в header_data
                try:
                    field_index = header_data.index(field_name) + 1  # +1 для Excel-стиля (столбец A=1)
                except ValueError:
                    field_index = "N/A"
                # error_details.append(f"Строка {i}, Столбец {field_index} ('{field_name}'): {', '.join(error_list)}")
                error_details.append(f"row_{i}[{field_index}]")
            message.append(error_details)
    if message:  # Если в списке message есть ошибки (он не пустой)
        return Response(message, status=400)  # Возвращаем ошибку
    else:
        return Response({"message": "Файл успешно загружен."}, status=200)  # Возвращаем успех