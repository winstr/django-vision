from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


app_name = 'common'
urlpatterns = [
    path('', views.home, name='home'),
    path('auth/login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/signup/', views.signup, name='signup'),
]