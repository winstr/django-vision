from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('common.urls')),
    path('ai/vision/', include('apps.ai.vision.urls')),

    path('admin/', admin.site.urls),
]
