from django.urls import path
from django.contrib.auth.views import LogoutView
from app import views 
app_name= 'app'

urlpatterns=[
    path('search/', views.product_search, name='product_search'),
    path('home/',views.home,name='home'),
    path('reg/',views.signup,name='signup'),
    path('',views.signin,name='signin'),
    path('logout/',views.signout,name='signout'),
   

    path('<slug:c_slug>/',views.home,name='products_by_category'),
    path("detail/<int:id>/",views.detail,name='detail'),
    path('add/<int:product_id>/',views.add_cart,name='add_cart'),
    path('cartdetail/<int:id>/', views.cart_detail, name='cart_detail'),  
    path('remove/<int:product_id>/',views.cart_remove,name='cart_remove'),
    path('forgot_password',views.forgtpss,name='forgot_password'),
    path('payment/<int:id>/',views.payment,name='payment'),
    path('success',views.home1,name='success'),
    path('payment/<int:id>/success', views.payment_success, name='payment_success'),
    path('payment_request/', views.payment_request, name='payment_request'),  # For OTP generation and initial payment request
    path('otp-verification/', views.otp_verification, name='otp_verification'),  # For OTP verification page





] 