from multiprocessing import AuthenticationError
from urllib import request
from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth import logout as auth_logout
import logging
from django.contrib.auth.models import User
from django.contrib.auth import login as lg,authenticate
from .models import UserProfile 

# def register(request):
#     if request.method=="POST":
#         user=User.objects.create_user(username=request.POST.get('username'),email=request.POST.get('email'),password=request.POST.get('password'))
#         user.save()
#         return render(request,"login.html")
#     return render(request,"register.html")

from django.db import IntegrityError

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('useremail')
        password = request.POST.get('password')
        number = request.POST.get('usernumber')

        try:
            # Create a new user
            user = User.objects.create_user(username=username, email=email, password=password)

            # Create a UserProfile associated with the user
            user_profile = UserProfile(user=user, number=number)
            user_profile.save()

            # Log in the user
            lg(request, user)

            return redirect('login')  # Redirect to the login page after successful registration

        except IntegrityError as e:
            # Handle the IntegrityError (e.g., duplicate number)
            error_message = "Registration failed. This number is already registered."
            return render(request, "register.html", {"error_message": error_message})

    return render(request, "register.html")




def login(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            lg(request, user)
            return redirect('index')  # Redirect to the index page after successful login
        else:
            context = {'error': 'Invalid Credentials'}

    return render(request, "login.html", context)


def forgot_password(request):
    return render(request,"forgot_password.html")

def index(request):
    return render(request,"index.html")


from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('login')  # Replace 'login' with the name of your login URL pattern.

