from django.shortcuts import render, redirect

from .forms import UserForm


def home(request):
    return render(request, 'common/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('common:login')
    else:
        form = UserForm()

    context = { 'form': form }
    return render(request, 'common/signup.html', context)