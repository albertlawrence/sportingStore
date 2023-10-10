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

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login as lg
from .models import UserProfile

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login as lg
from django.contrib import messages
from .models import UserProfile

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('useremail')
        password = request.POST.get('password')
        number = request.POST.get('usernumber')
        pdf_file = request.FILES.get('pdf_file')  # Get the uploaded file
        
        # Check if a PDF file was provided and its extension is ".pdf"
        if pdf_file and pdf_file.name.endswith('.pdf'):
            try:
                user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
                user_profile = UserProfile(user=user, number=number, is_custom=False, is_seller=True, is_approved=False)
                user_profile.pdf_file_path = pdf_file.name  # Store the file path in the UserProfile
                user_profile.save()
                
                messages.info(request, "Please wait for admin approval.")
                return redirect('login')

            except IntegrityError as e:
                error_message = "Registration failed. This number is already registered."
                return render(request, "register.html", {"error_message": error_message})
        else:
            error_message = "Please upload a valid PDF file."
            return render(request, "register.html", {"error_message": error_message})

    return render(request, "register.html")





from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db import IntegrityError 
from .models import UserProfile 

def customsignup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('useremail')
        password = request.POST.get('password')
        number = request.POST.get('usernumber')
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user_profile = UserProfile(user=user, number=number, is_custom=True, is_seller=False, is_approved=True)
            user_profile.save()

            # Log in the user
            lg(request, user)

            return redirect('login')  

        except IntegrityError as e:
            error_message = "Registration failed. This number is already registered."
            return render(request, "customsignup.html", {"error_message": error_message})

    return render(request, "customsignup.html")



from django.contrib import messages
from django.contrib.auth import authenticate, login as lg
from django.shortcuts import render, redirect
from .models import UserProfile

def login(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                lg(request, user)
                return redirect('adminapproval')
            else:
                try:
                    profile = UserProfile.objects.get(user=user)
                    is_seller = profile.is_seller

                    if is_seller:
                        if profile.is_approved:
                            lg(request, user)
                            return redirect('index')
                        else:
                            context = {'error': 'Your seller account is not yet approved.'}
                    else:
                        context = {'error': 'You are not a registered seller.'}

                except UserProfile.DoesNotExist:
                    context = {'error': 'User profile does not exist.'}
        else:
            context = {'error': 'Invalid username or password.'}

    return render(request, "login.html", context)














def forgot_password(request):
    return render(request,"forgot_password.html")


from .models import UserProfile

def index(request):
    print(f"User ID: {request.user.id}")
    isSeller = False  # Initialize isSeller to False
    
    if request.user.is_authenticated:
        try:
            print(f"User ID before query: {request.user.id}")
            profile = UserProfile.objects.get(user_id=request.user.id)
            isSeller = profile.is_seller
        except UserProfile.DoesNotExist:
            # Handle the case where UserProfile does not exist
            print("UserProfile does not exist for this user.")

    print(f"isSeller: {isSeller}")

    approved_products = Product.objects.filter(approved=True)
    return render(request, "index.html", {'products': approved_products, 'isSeller': isSeller})




from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('index') 


from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from .models import Product

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
            if category == 'others':
                # If the category is "others," get the values of the new_category and new_product_name fields
                new_category = request.POST.get('new_category')
                new_product_name = request.POST.get('new_product_name')

                # Check if the new category already exists in the database
                if not Product.objects.filter(category=new_category).exists():
                    # Create a new category entry if it doesn't exist
                    Product.objects.create(category=new_category)

                # Set the category and name to the new category and new product name values
                category = new_category
                name = new_product_name

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
    user_cart = None 
    
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
    
    product = Product.objects.get(pk=product_id)
    
    if user_cart is not None:
        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
    
        if not created:
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


from django.shortcuts import render
from .models import Product, UserProfile

def adminapproval(request):
    sellers = UserProfile.objects.filter(is_seller=True, is_approved=False)
    products = Product.objects.all()

    # Create a list to store seller data with PDF information
    seller_data = []

    for seller in sellers:
        # Check if the seller has uploaded a PDF
        pdf_info = {
            'pdf_uploaded': False,
            'pdf_url': None,
        }
        if seller.pdf_file_path:
            pdf_info['pdf_uploaded'] = True
            pdf_info['pdf_url'] = seller.pdf_file_path.url

        seller_data.append({
            'seller': seller,
            'pdf_info': pdf_info,
            'is_approved': seller.is_approved,  
        })

    return render(request, 'adminapproval.html', {'seller_data': seller_data, 'products': products})





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Product

@login_required
def seller_approval(request, user_id):
    # Retrieve the seller profile based on user ID
    seller_profile = get_object_or_404(UserProfile, user__id=user_id)

    # Check if the seller is not approved yet
    if not seller_profile.is_approved:
        # Approve the seller and save the changes
        seller_profile.is_approved = True
        seller_profile.save()
        messages.success(request, 'Seller approved successfully.')
    else:
        messages.warning(request, 'Seller is already approved.')

    # Redirect to admin approval page (you can also pass a message if needed)
    return redirect('adminapproval')

@login_required
def seller_delete(request, user_id):
    # Retrieve the seller profile based on user ID
    seller_profile = get_object_or_404(UserProfile, user__id=user_id)

    # Delete the seller profile
    seller_profile.delete()
    messages.success(request, 'Seller deleted successfully.')

    # Redirect to admin approval page (you can also pass a message if needed)
    return redirect('adminapproval')

