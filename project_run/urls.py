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

from app_run.views import company_details, RunViewSet, UserViewSet, RunStartApiView, RunStopApiView, AthleteInfoApiView

router = routers.DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('api/runs/<int:run_id>/start/', RunStartApiView.as_view(), name='run-start'),
    path('api/runs/<int:run_id>/stop/', RunStopApiView.as_view(), name='run-stop'),
    path('api/athlete_info/<int:athlete_id>/', AthleteInfoApiView.as_view(), name='athlete-info'),

    path('',include(router.urls)),
]