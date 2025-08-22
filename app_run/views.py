from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

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

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_role = self.request.query_params.get('type')
        if user_role == 'athlete':
            qs = qs.filter(is_staff=False)
        elif user_role == 'coach':
            qs = qs.filter(is_staff=True)
        return qs