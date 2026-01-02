from django.contrib import admin

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem, Subscribe

admin.site.register(Run, list_display=['id', 'athlete', 'status', 'created_at'])
admin.site.register(AthleteInfo, list_display=['user_id', 'weight'])
admin.site.register(Subscribe, list_display=['athlete', 'coach', 'subscribed_at'])
admin.site.register(Challenge, list_display=['full_name', 'athlete'])
admin.site.register(Position, list_display=['run', 'latitude', 'longitude'])
admin.site.register(CollectibleItem, list_display=['name', 'uid', 'picture', 'value', 'latitude', 'longitude'])
