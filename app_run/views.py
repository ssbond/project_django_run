from pyexpat.errors import messages

from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django.conf import settings
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from django.db import IntegrityError

from app_run.models import Run, AthleteInfo, Challenge
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
def company_details(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    }
    return Response(details)
class RunsPagination(PageNumberPagination):
    page_size_query_param = 'size'  # Разрешаем изменять количество объектов через query параметр size в url
    max_page_size = 50  # Ограничиваем максимальное количество объектов на странице

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    ordering = ('-created_at',)
    pagination_class = RunsPagination



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
            # if run.status == 'finished':
                run.status = 'finished'
                run.save()
                data = {"message": "Забег окончил"}
                # print('Забег окончен')
                athlete = self.request.user  # текущий пользователь
                if athlete == None or athlete.is_anonymous:
                    data = {"message": "Анонимный пользователь не может участвовать в челленджах"}
                    return Response(data, status=status.HTTP_401_UNAUTHORIZED)
                try:
                    total_runs = Run.objects.filter(athlete=athlete, status='finished').count()
                except Run.DoesNotExist:
                    total_runs = 0
                if total_runs >= 10:
                    challenge10, created = Challenge.objects.get_or_create(
                        athlete=athlete,
                        full_name='Сделай 10 Забегов!'
                    )
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {"message": "Невозможно закончить не начатый забег"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Run.DoesNotExist:
            data = {"message": "Забег не найден"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

class AthletsPagination(PageNumberPagination):
    page_size_query_param = 'size'  # Разрешаем изменять количество объектов через query параметр size в url
    max_page_size = 50  # Ограничиваем максимальное количество объектов на странице

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False).annotate(
        runs_finished_count=Count('runs', filter=Q(runs__status='finished'))
    )

    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['first_name', 'last_name']  # Указываем поля по которым будет вестись поиск
    search_fields = ['first_name', 'last_name']  # Для поиска по части строки
    ordering_fields = ['date_joined'] # Поля по которым будет возможна сортировка
    ordering = ['-date_joined']  # Сортировка по умолчанию (новые first)
    pagination_class = AthletsPagination
    def get_queryset(self):
        qs = super().get_queryset()
        user_role = self.request.query_params.get('type')
        if user_role == 'athlete':
            qs = qs.filter(is_staff=False)
        elif user_role == 'coach':
            qs = qs.filter(is_staff=True)
        return qs

class AthleteInfoApiView(APIView):
    def get(self, request, *args, **kwargs):
        athlete_id = self.kwargs.get('athlete_id')
        try:
            user = User.objects.get(id=athlete_id)
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)
        athlete_info, created = AthleteInfo.objects.get_or_create(user_id=user)
        athlete_info_serializer = AthleteInfoSerializer(athlete_info)
        return Response(athlete_info_serializer.data)

    def put(self, request, *args, **kwargs):
        athlete_id = self.kwargs.get('athlete_id')
        try:
            user = User.objects.get(id=athlete_id)
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)
        athlete_info, created = AthleteInfo.objects.get_or_create(user_id=user)
        weight = request.data.get('weight')
        goals = request.data.get('goals')
        athlete_info.weight = weight
        athlete_info.goals = goals
        try:
            athlete_info.full_clean()
            athlete_info.save()
        except ValidationError as e:
            erros = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            return Response(erros, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'weight': ['Недопустимое значение веса']}, status=status.HTTP_400_BAD_REQUEST)
        athlete_info_serializer = AthleteInfoSerializer(athlete_info)
        return Response(athlete_info_serializer.data, status=status.HTTP_201_CREATED)


class ChallengeInfoApiViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.all().select_related('athlete')
    serializer_class = ChallengeSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['athlete']
    ordering_fields = ['full_name']
    ordering = ('full_name',)
    pagination_class = RunsPagination
    def list(self, request, *args, **kwargs):
        user = self.request.user  # текущий пользователь
        # ... ваш код ...
        print(user)
        return super().list(request, *args, **kwargs)