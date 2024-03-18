from django.urls import path

from . import views


app_name = 'ai/vision'
urlpatterns = [
    path('', views.intro, name='intro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('control/', views.control, name='control'),
    path('stream/show/', views.show_stream, name='show_stream'),
]