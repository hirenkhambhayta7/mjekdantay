from django.urls import path
from . import admin_views

app_name = 'store_admin'

urlpatterns = [
    path('', admin_views.dashboard, name='dashboard'),
    path('orders/', admin_views.orders_list, name='orders_list'),
    path('orders/bulk-update/', admin_views.order_bulk_update, name='order_bulk_update'),
    path('orders/<int:pk>/', admin_views.order_detail, name='order_detail'),
    path('products/', admin_views.products_list, name='products_list'),
    path('products/add/', admin_views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', admin_views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', admin_views.product_delete, name='product_delete'),
    path('products/<int:pk>/toggle/', admin_views.product_toggle, name='product_toggle'),
    path('categories/', admin_views.categories_list, name='categories'),
    path('customers/', admin_views.customers_list, name='customers'),
]
