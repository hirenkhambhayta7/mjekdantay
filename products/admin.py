from django.contrib import admin
from django.utils.html import mark_safe
from .models import Category, Product, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['weight_label', 'price', 'stock_quantity', 'get_stock_status']
    readonly_fields = ['get_stock_status']

    def get_stock_status(self, obj):
        if obj.pk is None:
            return '-'
        if obj.stock_quantity < 10:
            return mark_safe(f'<span style="color: red; font-weight: bold;">⚠ Low Stock ({obj.stock_quantity})</span>')
        return mark_safe(f'<span style="color: green;">✓ In Stock ({obj.stock_quantity})</span>')
    get_stock_status.short_description = 'Stock Status'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured']
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'weight_label', 'price', 'stock_quantity', 'get_stock_status']
    list_filter = ['product__category']
    search_fields = ['product__name']

    def get_stock_status(self, obj):
        if obj.stock_quantity < 10:
            return mark_safe(f'<span style="color: red; font-weight: bold;">⚠ Low ({obj.stock_quantity})</span>')
        return mark_safe(f'<span style="color: green;">✓ OK ({obj.stock_quantity})</span>')
    get_stock_status.short_description = 'Stock Status'
