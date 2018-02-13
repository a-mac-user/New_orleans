from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate


def entry(request):
    return render(request, 'entry.html')


def acc_login(request):
    error = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            request.session.set_expire(60*60)
        else:
            error["error"] = 'Wrong username or password!'
    return render(request, 'login.html', {'error': error})


def acc_logout(request):
    logout(request)
    return redirect('/login')


@login_required()
def swing_index(request):
    return render(request, '')
