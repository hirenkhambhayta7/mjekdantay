from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:slug>/', views.category_products, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]