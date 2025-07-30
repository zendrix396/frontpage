from django.urls import path
from . import views

app_name = 'authorization'
urlpatterns = [
    path('auth/', views.SignUP.as_view(), name='signup'),
    path('', views.Index.as_view(), name='index'),
    path('auth/otpverify/', views.verifyOTP, name='otpverify'),
    path('auth/signup/', views.getUserData, name='getUserData'),
    path('auth/login/', views.LoginPage.as_view(), name='login'),
    path('auth/loginCheck/', views.loginCheck, name='loginCheck'),
    path('logout/', views.logout_view, name='logout'),

]