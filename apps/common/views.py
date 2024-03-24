from django.contrib.auth import logout
from django.shortcuts import render, redirect

from .forms import UserForm


def home(request):
    return render(request, 'common/home.html')


def logout_user(request):
    logout(request)
    return redirect('common:home')


def signup_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('common:login')
    else:
        form = UserForm()
    context = {'form': form}
    return render(request, 'common/signup.html', context)
