from itertools import count

from openpyxl.pivot.fields import Number
from rest_framework import serializers
from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem, Subscribe

from django.contrib.auth.models import User


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ['name', 'uid', 'longitude', 'latitude', 'value', 'picture']


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField(source='runs_finished_count', read_only=True)

    # Если нужно посчитать в сериализаторе (плохо) и получить N+1 запросов
    # runs_finished = serializers.SerializerMethodField()
    # def get_runs_finished(self, obj):
    #     ❌ ПЛОХО: отдельный запрос для каждого пользователя
    # return obj.runs.filter(status='finished').count()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'


class UserDetailSerializer(UserSerializer):
    items = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['items']

    def get_items(self, obj):
        return CollectibleItemSerializer(obj.items.all(), many=True).data


class AthleteDetailSerializer(UserDetailSerializer):
    coach = serializers.SerializerMethodField()

    class Meta(UserDetailSerializer.Meta):
        model = User
        fields = UserDetailSerializer.Meta.fields + ['coach']

    def get_coach(self, obj):
        subscription = Subscribe.objects.filter(athlete=obj).first()
        return subscription.coach.id if subscription else None


class CoachDetailSerializer(UserDetailSerializer):
    athletes = serializers.SerializerMethodField()

    class Meta(UserDetailSerializer.Meta):
        model = User
        fields = UserDetailSerializer.Meta.fields + ['athletes']

    def get_athletes(self, obj):
        return list(Subscribe.objects.filter(coach=obj).values_list('athlete_id', flat=True))


class AthletRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthletRunSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = '__all__'


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'


class ChallengesSummarySerializer(serializers.ModelSerializer):
    athletes = serializers.SerializerMethodField()
    name_to_display = serializers.CharField(source='full_name')

    class Meta:
        model = Challenge
        fields = ['name_to_display'] + ['athletes']

    def get_athletes(self, obj):
        athletes = User.objects.filter(challenges=obj)
        return [
            {
                'id': athlete.id,
                'full_name': f"{athlete.first_name} {athlete.last_name}",
                'username': athlete.username
            }
            for athlete in athletes
        ]


class PositionSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')
    speed = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ['id', 'run', 'latitude', 'longitude', 'date_time', 'speed', 'distance']

    def get_speed(self, obj):
        return round(obj.speed, 2) if obj.speed is not None else None

    def get_distance(self, obj):
        return round(obj.distance, 2) if obj.distance is not None else None
