from multiprocessing import AuthenticationError
from urllib import request
from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth import logout as auth_logout
import logging
from django.contrib.auth.models import User
from django.contrib.auth import login as lg,authenticate
from .models import UserProfile 
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
            if user.is_superuser:
                return redirect('adminapproval')  
            else:
                return redirect('index') 
        else:
            context = {'error': 'Invalid Credentials'}

    return render(request, "login.html", context)


def forgot_password(request):
    return render(request,"forgot_password.html")


def index(request):
    approved_products = Product.objects.filter(approved=True)
    return render(request, "index.html", {'products': approved_products})


from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('login') 


from django.core.exceptions import ValidationError

def upload_product(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        name = request.POST.get('name')
        size = request.POST.get('size', None)
        price = request.POST.get('price')
        image = request.FILES.get('image')
        product_count = request.POST.get('product_count')
        allowed_formats = ['jpg', 'jpeg', 'png', 'gif']
        file_extension = image.name.split('.')[-1].lower()

        if file_extension not in allowed_formats:
            return render(request, 'upload_product.html', {'error_message': 'Only image files (jpg, jpeg, png, gif) are allowed.'})

        try:
            product = Product.objects.create(
                category=category,
                name=name,
                size=size,
                price=price,
                image=image,
                approved=False,
                product_count=product_count
            )
            product.save()
            return redirect('upload_product')
        except Exception as e:
            print(e)
            return render(request, 'upload_product.html', {'error_message': 'Error occurred while saving the product.'})

    return render(request, 'upload_product.html')




# def show_products(request):
#     products = Product.objects.all()
#     return render(request, 'show_products.html', {'products': products})


from django.shortcuts import render, redirect
from .models import Product

def adminapproval(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')  # Assuming you have a hidden input for product_id in your form
        try:
            product = Product.objects.get(id=product_id)
            product.approved = not product.approved  # Toggle the 'approved' status
            product.save()
        except Product.DoesNotExist:
            pass  # Handle the case where the product does not exist

    products = Product.objects.all()
    return render(request, 'adminapproval.html', {'products': products})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def toggle_approval(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.approved = not product.approved
    product.save()
    return redirect('adminapproval')





from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
import razorpay
from .models import UserProfile

razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def paymentform(request: HttpRequest):
    currency = 'INR'
    amount = int(request.GET.get("amount")) * 100  # Rs. 200

    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount / 100
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'paymentform.html', context=context)

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                amount = 20000 
                authenticated_user = request.user
                user_profile = UserProfile.objects.get(user=authenticated_user)
                user_profile.subscribed = True
                user_profile.save()
                
                return render(request, 'index.html')
            else:
                return render(request, 'errorpage.html')
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()



# views.py
from django.shortcuts import render
from .models import Product  # Import your Product model

def productdetail(request, pk):  # Add the 'pk' parameter
    try:
        product = Product.objects.get(pk=pk)
        return render(request, 'productdetail.html', {'product': product})
    except Product.DoesNotExist:
        # Handle the case where the product with the given 'pk' doesn't exist
        return render(request, 'index.html')  # Create a template for this case





from django.shortcuts import render, redirect
from .models import Product, Cart, CartItem

def add_to_cart(request, product_id):
    # Get the product based on the product_id
    product = Product.objects.get(pk=product_id)

    # Get or create the user's cart
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Handle for anonymous users if needed
        pass

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
    
    if not created:
        # If the product is already in the cart, increase the quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

def view_cart(request):
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=user_cart)
    else:
        cart_items = []

    return render(request, 'cart.html', {'cart_items': cart_items})
