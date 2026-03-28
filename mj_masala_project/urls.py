from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store-admin/', include('products.admin_urls')),
    path('', include('products.urls')),
    path('', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'MJ Ekdantay Masala Centre — Admin'
admin.site.site_title = 'MJ Masala Admin'
admin.site.index_title = 'Dashboard'
