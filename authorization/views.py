from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserCreds
from django.http import HttpResponseRedirect
from django.views import generic
import smtplib
import random
from django.urls import reverse
import os
from dotenv import load_dotenv

# Create your views here.
load_dotenv()

class SignUP(generic.ListView):
    template_name = 'authorization/signup.html'
    def get_queryset(self):
        return
class Index(generic.DetailView):
    model = UserCreds
    context_object_name = 'user'
    template_name = 'authorization/index.html'

    def get_object(self):
        username = self.request.session.get('just_signed_up')
        return get_object_or_404(UserCreds, username=username)

def getUserData(request):
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
    except:
        return render(request, 'authorization/signup.html', {'error_message':"Enter valid data!"})
    else:
        if password != password_confirm:
            return render(request, 'authorization/signup.html', {'error_message':"Password do not match!"})
    
        random_otp = random.randint(1000,9999)
        sender_email = os.environ.get('SENDER_EMAIL')
        app_password = os.environ.get('APP_PASSWORD')
        receiver_email = email

        subject = "OTP verification from front page clone"
        body = f"Hello! Your OTP for front page clone app is {random_otp}"
        message = f"Subject: {subject}\n\n{body}"

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, receiver_email, message)
        except Exception as e:
            print("Email sending failed:", e)

        request.session['signup_data'] = {
        'username': username,
        'email': email,
        'password': password,
        'otp': str(random_otp),
    }
        context = {"show_otp": True, "otp":random_otp, 'username':username}
        return render(request, 'authorization/signup.html', context=context)

def verifyOTP(request):
    signup_data = request.session.get('signup_data')
    if "otp_tries" not in request.session:
        request.session['otp_tries'] = 0
    
    if request.session['otp_tries'] > 3:
        request.session['otp_tries'] = 0
        return render(request, 'authorization/signup.html', {'show_otp':False, "error_message": "Try again! Failed to verify OTP"})
    if not signup_data:
        return render(request, 'authorization/signup.html', {
        'error_message': 'Session expired. Please sign up again.'
    })
    input_otp = request.POST.get('user_otp')
    if input_otp != signup_data['otp']:
        request.session['otp_tries']+=1
        return render(request, 'authorization/signup.html', {"show_otp": True, "error_message":"Incorrect OTP! Try Again", 'email':signup_data['email']})
    user = User.objects.create_user(username=signup_data['username'], email=signup_data['email'], password=signup_data['password'])
    new_user = UserCreds.objects.create(username=signup_data['username'], email=signup_data['email'])
    request.session.flush()
    request.session['just_signed_up'] = signup_data['username']
    return HttpResponseRedirect(reverse("authorization:index"))