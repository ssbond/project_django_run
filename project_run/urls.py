"""
URL configuration for project_run project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from app_run.views import company_details, RunViewSet, UserViewSet, RunStartApiView, RunStopApiView, AthleteInfoApiView, \
    ChallengeInfoApiViewSet, PositionApiViewSet, SubscribeToCoachApiView
from app_run.view_collectible_item import CollectibleItemApiViewSet, upload_collectible_items_xls

router = routers.DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)
router.register('api/challenges', ChallengeInfoApiViewSet)
router.register('api/positions', PositionApiViewSet)
router.register('api/collectible_item', CollectibleItemApiViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/upload_file/', UploadFileApiView.as_view(), name='upload-file'),
    path('api/upload_file/', upload_collectible_items_xls),
    path('api/company_details/', company_details),
    path('api/runs/<int:run_id>/start/', RunStartApiView.as_view(), name='run-start'),
    path('api/runs/<int:run_id>/stop/', RunStopApiView.as_view(), name='run-stop'),
    path('api/athlete_info/<int:athlete_id>/', AthleteInfoApiView.as_view(), name='athlete-info'),
    # path('api/users/<int:user_id>/', UserDetailApiView.as_view(), name='user-detail'),
    path('api/subscribe_to_coach/<int:id>/', SubscribeToCoachApiView.as_view(), name='subscribe-to-coach'),

    path('',include(router.urls)),
]