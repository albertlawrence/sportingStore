from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('register', views.register, name="register"),
    path('login', views.login, name="login"),
    path('forgot_password', views.forgot_password, name="forgot_password"),
    path('', views.index, name="index"),
    path('logout/', views.user_logout, name='logout'),
    path('upload_product/', views.upload_product, name='upload_product'),
     path('adminapproval/', views.adminapproval, name='adminapproval'),
    path('adminapproval/toggle/<int:product_id>/', views.toggle_approval, name='toggle_approval'),
    path('paymentform/', views.paymentform, name='paymentform'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('productdetail/<int:pk>/', views.productdetail, name='productdetail'),



    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

