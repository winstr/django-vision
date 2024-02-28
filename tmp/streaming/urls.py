from django.urls import path

from . import views


app_name = 'streaming'
urlpatterns = [
    path('', views.sample, name='sample'),
    path('stream/', views.stream, name='stream'),
]