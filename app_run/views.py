from pyexpat.errors import messages

from django.db.models import Count, Q, Sum

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django.conf import settings
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from django.db import IntegrityError

from app_run.models import Run, AthleteInfo, Challenge, Position
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, PositionSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from geopy.distance import geodesic




class PositionApiViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    def create(self, request, *args, **kwargs):
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            current_run = serializer.validated_data['run']
            current_run_id = current_run.id
            run = Run.objects.get(id=current_run_id)
            run_status = run.status
            if run_status != 'in_progress':
                return Response({'detail': 'Невозможно добавить позицию в забег, который не в процессе.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def destroy(self, request, *args, **kwargs):
    #     run_id = request.data.pop('id', None)
    #     run = Run.objects.get(id=run_id)
    #     run.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    # def list(self, request, *args, **kwargs):
    #     run_id = request.query_params.get('run_id', None)
    #     if run_id is not None:
    #         positions = Position.objects.filter(run=run_id)
    #     else:
    #         positions = Position.objects.all()
    #     serializer = PositionSerializer(positions, many=True)
    #     return Response(serializer.data, status=HTTP_200_OK)


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

def calculate_distance(coordinates_list):
    distance = 0.0
    for i in range(len(coordinates_list)-1):
        segment = geodesic(coordinates_list[i], coordinates_list[i+1]).km
        distance += segment
    return distance

# тестовая функция для проверки расчета дистанции
def mock_data():
    print('test')
    coordinates_list = Position.objects.filter(run_id=2).values_list('latitude', 'longitude')
    distance = calculate_distance(coordinates_list)
    print(coordinates_list)
    distance = calculate_distance(coordinates_list)
    print(distance)

def challenge10runs(athlete):
    total_runs = Run.objects.filter(athlete=athlete, status='finished').count()
    if total_runs >= 10:
        challenge10, created = Challenge.objects.get_or_create(
            athlete=athlete,
            full_name='Сделай 10 Забегов!'
        )
        return challenge10
    return None


def challenge50km(athlete):
    total_distance = Run.objects.filter(athlete=athlete, status='finished').aggregate(total_distance=Sum('distance'))['total_distance'] or 0
    if total_distance >= 50:
        challenge50, created = Challenge.objects.get_or_create(
            athlete=athlete,
            full_name='Пробеги 50 километров!'
        )
        return challenge50
    return None


class RunStopApiView(APIView):
    def post(self, request, *args, **kwargs):
        run_id = self.kwargs.get('run_id')

        try:
            run = Run.objects.get(id=run_id)
            if run.status == 'in_progress':
            # if run.status == 'finished':
                run.status = 'finished'
                coordinates_list = Position.objects.filter(run_id=run_id).values_list('latitude', 'longitude')
                distance = calculate_distance(coordinates_list)
                run.distance = distance
                run.save()
                data = {"message": "Забег окончил"}
                # Проверка и создание челленджа "Сделай 10 Забегов!"
                athlete = Run.objects.get(id=run_id).athlete
                challenge10runs(athlete)
                challenge50km(athlete)


            # try:
            #         athlete = Run.objects.get(id=run_id).athlete
            #         total_runs = Run.objects.filter(athlete=athlete, status='finished').count()
            #     except Run.DoesNotExist:
            #         total_runs = 0
            #     if total_runs >= 10:
            #         challenge10, created = Challenge.objects.get_or_create(
            #             athlete=athlete,
            #             full_name='Сделай 10 Забегов!'
            #         )
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

        mock_data() #тестовый вызов

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
    # pagination_class = RunsPagination
    # def list(self, request, *args, **kwargs):
    #     user = self.request.user  # текущий пользователь
        # ... ваш код ...
        # print(user)
        # return super().list(request, *args, **kwargs)

