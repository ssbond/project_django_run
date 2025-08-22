from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer
from django.contrib.auth.models import User


@api_view(['GET'])
def company_details(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    }
    return Response(details)

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer






class RunStartApiView(APIView):
    def post(self, request, *args, **kwargs):
        run_id = self.kwargs.get('run_id')
        try:
            run = Run.objects.get(id=run_id)
            if run.status == 'init':
                run.status = 'in_progress'
                run.save()
                data = {"message": "Забег начал"}
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {"message": "Невозможно запустить запущенный или законченный забег"}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)
        except Run.DoesNotExist:
            data = {"message": "Забег не найден"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class RunStopApiView(APIView):
    def post(self, request, *args, **kwargs):
        run_id = self.kwargs.get('run_id')
        try:
            run = Run.objects.get(id=run_id)
            if run.status == 'in_progress':
                run.status = 'finished'
                run.save()
                data = {"message": "Забег окончил"}
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {"message": "Невозможно закончить не начатый забег"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Run.DoesNotExist:
            data = {"message": "Забег не найден"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]  # Подключаем SearchFilter здесь
    search_fields = ['first_name', 'last_name']  # Указываем поля по которым будет вестись поиск
    def get_queryset(self):
        qs = super().get_queryset()
        user_role = self.request.query_params.get('type')
        if user_role == 'athlete':
            qs = qs.filter(is_staff=False)
        elif user_role == 'coach':
            qs = qs.filter(is_staff=True)
        return qs