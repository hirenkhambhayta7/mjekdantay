from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product_variant', 'quantity']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'created_at']
    list_filter = ['created_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_label', 'quantity', 'price_at_purchase', 'total_price']

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total'


def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status='shipped')
mark_as_shipped.short_description = 'Mark selected orders as Shipped'


def mark_as_delivered(modeladmin, request, queryset):
    queryset.update(status='delivered')
mark_as_delivered.short_description = 'Mark selected orders as Delivered'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['customer__email', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['razorpay_order_id', 'created_at']
    actions = [mark_as_shipped, mark_as_delivered]
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'razorpay_payment_id', 'amount', 'status', 'paid_at']
    list_filter = ['status', 'paid_at']
    readonly_fields = ['razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature']
