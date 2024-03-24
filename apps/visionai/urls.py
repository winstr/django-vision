from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


app_name = 'vision-ai'

urlpatterns = [
    path('monitor/', views.monitor, name='monitor'),

    path('stream/', views.render_stream, name='stream'),
    path('control/', views.control, name='control'),
]