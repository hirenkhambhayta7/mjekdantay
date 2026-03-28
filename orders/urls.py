from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/create-order/', views.create_order, name='create_order'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/success/page/', views.payment_success_page, name='payment_success_page'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
]
