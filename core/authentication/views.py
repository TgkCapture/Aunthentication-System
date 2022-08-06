from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from core import settings
from django.core.mail import send_mail




def home(request):
    return render(request, 'authentication/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('home')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('home')
        elif len(username) < 6:
            messages.error(request, "Username must be at least 6 characters")
            return redirect('home')
        elif password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('home')
        elif not username.isalnum():
            messages.error(request, "Username must be alphanumeric")
            return redirect('home')
        else:
            myuser = User.objects.create_user(username=username, first_name=firstName, last_name=lastName, email=email, password=password)
            myuser.save()
            messages.success(request, "You are now registered , verify your email to login")

            # Welcome Email
            subject = 'Welcome to Django Authentication'
            message = 'Hi ' + myuser.first_name + ', welcome to Django Authentication'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [myuser.email]
            send_mail( subject, message, email_from, recipient_list, fail_silently=False )


            return redirect('login')


        # myuser = User.objects.create_user(username, email, password)
        # myuser.first_name = firstName
        # myuser.last_name = lastName

        # myuser.save()

        # messages.success(request, "Your account has been successfully created")
        # return redirect('/login')


    return render(request, 'authentication/register.html')

def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            firstName = user.first_name
            messages.success(request, "You are now logged in")
            return render(request, 'authentication/index.html', {'firstName': firstName})
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('home')


    return render(request, 'authentication/login.html')

def logout(request):
    auth_logout(request)
    messages.success(request, "You are now logged out") 
    return redirect('home')