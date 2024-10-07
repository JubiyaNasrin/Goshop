from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login ,logout 
from django.shortcuts import render, redirect,get_object_or_404
from app.models import Category,Product,Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from .utils import _cart_id  # Import your utility function for retrieving the cart ID
import uuid
from django.http import Http404
from django.db.models import Q  # Import Q for complex queries
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.urls import reverse
from .models import UserProfile  # Import the UserProfile model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
import razorpay
from django.core.mail import send_mail  # or use your SMS API to send OTP
import random
from django.views.decorators.csrf import csrf_exempt
import re





# Create your views here.

# def signup(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirmpassword = request.POST.get('confirmpassword')

#         # validate the passwords
#         if password != confirmpassword:
#             return render(request, 'signup.html', {'error': 'Passwords do not match'})
#          # Check if the username already exists
#         if User.objects.filter(username=username).exists():
#             return render(request, 'signup.html', {'error': 'Username already exists'})
        
#         # Create a new user
#         user = User.objects.create_user(username=username, email=email, password=password)
        
#         # Log the user in
#         auth_login(request, user)
#          # Redirect to the signin page after successful signup
#         return redirect('app:signin')
    
#     # Clear the form when the page is loaded or reloaded
#     return render(request, 'signup.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        # Check if passwords match
        if password != confirmpassword:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already exists'})

        # Enforce strong password policy
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            return render(request, 'signup.html', {'error': 'Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character.'})

        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Log the user in and redirect to the signin page
        auth_login(request, user)
        return redirect('app:signin')

    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('app:home')  # Redirect to the home page after successful login
        else:
            # Pass error message to the template if login fails
            return render(request, 'signin.html', {'error': 'Invalid username or password'})
    
    return render(request, 'signin.html')  # Render the sign-in page for GET requests




# def signin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             auth_login(request, user)
#             return redirect('app:home')  # Redirect to the home page after successful login
#         else:
#             # Redirect to the signup page if credentials are invalid
#             return redirect('app:signup')
#     else:
#         return render(request, 'signin.html')  # Render the sign-in page for GET requests
    
def signout(request):
    logout(request)
    return redirect('app:signin')  # Redirect to signin page after signout


# product search
def product_search(request):
    query = request.GET.get('q', '')  # Get the search query from the GET parameters
    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)) if query else []  # Filter products by name or description

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'search.html', context)  # Render a new template to display the search results


def home(request,c_slug=None):
    categories = Category.objects.all()
    products_by_category = {}  # Dictionary to store products categorized by each category

    for category in categories:
          # Fetch products related to each category
        product = Product.objects.filter(category=category, available=True)
          # Add the category and its products to the dictionary
        products_by_category[category] =product
        electronics = products_by_category.get(Category.objects.get(name='Electronics'), [])
        cosmetics = products_by_category.get(Category.objects.get(name='Cosmetics'), [])
    
    
    context = {
        'products_by_category': products_by_category,
        'electronics': electronics,
        'cosmetics': cosmetics,
    }
    return render(request, 'productlist.html', context)

     
def detail(request, id):
    product = get_object_or_404(Product, id=id)  # Fetch the product by ID
    return render(request, "detail.html", {'d': product})


def cart_detail(request, id=None):
    cart_id = _cart_id(request)  # Get the cart ID from session or other logic

    # Retrieve the correct Cart instance or None if it doesn't exist
    cart = None
    if id:
        cart = Cart.objects.filter(id=id).first()
    elif cart_id:
        cart = Cart.objects.filter(cart_id=cart_id).first()

    # Retrieve active cart items
    cart_items = CartItem.objects.filter(cart=cart, active=True) if cart else []
    
    # Calculate total items in cart
    item_count = sum(item.quantity for item in cart_items)

    # Check if the cart is empty
    cart_empty = item_count == 0

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'item_count': item_count,
        'cart_empty': cart_empty,  # Pass the empty status to the template
    }

    return render(request, 'cart.html', context)


def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
# Add product to cart
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()

    # Redirect to cart details page after adding the product to the cart
    return redirect('app:cart_detail',id=cart.id)

def _cart_id(request):
    # Retrieve the current session key
    cart_id = request.session.get('cart_id')
    
    # If the cart_id does not exist, create a new one
    if not cart_id:
        # Generate a new cart_id
        cart_id = str(uuid.uuid4())
        # Save the new cart_id in the session
        request.session['cart_id'] = cart_id

    return cart_id



def cart_remove(request, product_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        raise Http404("Cart not found")

    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
    except CartItem.DoesNotExist:
        raise Http404("Cart item not found")

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('app:cart_detail',id=cart.id)


def forgtpss(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the username and check if the new passwords match
        if new_password == confirm_password:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)  # Set the new password
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('app:signin')  # Redirect to sign-in page
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request,'forgot_password.html')

def home1(request):
    if request.method == "POST":
        name = request.POST.get('name')
        amount = 500

        client = razorpay.Client(
            auth=("rzp_test_JAeLcxoJpwFjEq", "PvjOeaEQA5b2gH4XHxEGEhMB"))

        payment = client.order.create({'amount': amount, 'currency': 'INR',
                                       'payment_capture': '1'})
                                       
    return render(request, 'payment.html')

def payment(request,id):
    product = get_object_or_404(Product, id=id)
    return render(request,'payment.html',{'d':product})


@csrf_exempt
def payment_success(request, id):
    # Logic to handle successful payment, e.g. update order status
    context = {'id': id}
    return render(request, 'payment_success.html', context)



def generate_otp():
    return random.randint(100000, 999999)

def send_otp_to_user(phone_number, otp):
    # Use your SMS API here to send the OTP
    pass

def payment_request(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        otp = generate_otp()
        send_otp_to_user(phone_number, otp)
        request.session['otp'] = otp
        request.session['phone_number'] = phone_number
        return redirect('app:otp_verification')

    return render(request, 'payment_page.html')

def otp_verification(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        if input_otp == str(request.session.get('otp')):
            return redirect('app:payment_page')  # Redirect to the payment page
        else:
            return render(request, 'otp_verification.html', {'error': 'Invalid OTP'})

    return render(request, 'otp_verification.html')



