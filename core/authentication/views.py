from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from core import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from . tokens import account_activation_token



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
            myuser.is_active = False
            myuser.save()
            messages.success(request, "You are now registered , verify your email to login")

            # Welcome Email
            subject = 'Welcome to Django Authentication'
            message = 'Hi ' + myuser.first_name + ', welcome to Django Authentication'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [myuser.email]
            send_mail( subject, message, email_from, recipient_list, fail_silently=False )

            # Verification Email
            current_site = get_current_site(request)
            email_subject = 'Activate Your Django Authentication Account'
            email_message = render_to_string('acc_active_email.html', {
                'name': myuser.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                'token': account_activation_token.make_token(myuser),
            })
            email = EmailMessage(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [myuser.email],
            )
            email.fail_silently = False
            email.send()          

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

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    if myuser is not None and account_activation_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        auth_login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')