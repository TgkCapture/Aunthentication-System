from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def home(request):
    return render(request, 'authentication/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['firstName']
        lname = request.POST['lastName']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']

        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created")
        return redirect('/login')


    return render(request, 'authentication/register.html')

def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in")
            return render(request, 'authentication/index.html', {'username': username})
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/login')


    return render(request, 'authentication/login.html')

def logout(request):
    pass 