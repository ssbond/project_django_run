from django.contrib import admin

from app_run.models import Run, AthleteInfo, Challenge, Position

admin.site.register(Run, list_display=['id', 'athlete', 'status', 'created_at'])
admin.site.register(AthleteInfo, list_display=['user_id', 'weight'])
admin.site.register(Challenge, list_display=['full_name', 'athlete'])
admin.site.register(Position, list_display=['run', 'latitude', 'longitude'])
