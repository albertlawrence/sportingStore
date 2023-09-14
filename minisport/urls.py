from django.urls import path
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.register, name="register"),
    path('login', views.login, name="login"),
    path('forgot_password', views.forgot_password, name="forgot_password"),
    path('index', views.index, name="index"),
     path('logout/', views.user_logout, name='logout'),
]

