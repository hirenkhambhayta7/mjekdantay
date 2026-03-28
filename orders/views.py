import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import F
from django.utils import timezone
from products.models import ProductVariant
from accounts.models import Address
from .models import Cart, CartItem, Order, OrderItem, Payment


def _get_or_create_cart(request):
    """Get or create a cart for the current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def merge_cart_on_login(request):
    """Merge guest session cart into user cart after login."""
    if not request.user.is_authenticated:
        return
    session_key = request.session.session_key
    if not session_key:
        return
    try:
        guest_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=request.user)

    for item in guest_cart.items.all():
        existing = user_cart.items.filter(product_variant=item.product_variant).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()

    guest_cart.delete()


def cart_view(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related(
        'product_variant', 'product_variant__product'
    ).all()
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def add_to_cart(request):
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if not variant.is_in_stock:
        return JsonResponse({'error': 'Out of stock'}, status=400)

    if quantity > variant.stock_quantity:
        return JsonResponse({'error': f'Only {variant.stock_quantity} available'}, status=400)

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product_variant=variant,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > variant.stock_quantity:
            cart_item.quantity = variant.stock_quantity
        cart_item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'message': f'{variant.product.name} ({variant.weight_label}) added to cart!'
        })

    return redirect('orders:cart')


@require_POST
def update_cart_item(request):
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))

    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if quantity <= 0:
        item.delete()
    else:
        if quantity > item.product_variant.stock_quantity:
            quantity = item.product_variant.stock_quantity
        item.quantity = quantity
        item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'subtotal': float(cart.subtotal),
            'delivery_charge': float(cart.delivery_charge),
            'grand_total': float(cart.grand_total),
            'line_total': float(item.line_total) if quantity > 0 else 0,
            'quantity': quantity,
        })

    return redirect('orders:cart')


@require_POST
def remove_cart_item(request):
    item_id = request.POST.get('item_id')
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'subtotal': float(cart.subtotal),
            'delivery_charge': float(cart.delivery_charge),
            'grand_total': float(cart.grand_total),
        })

    return redirect('orders:cart')


@login_required
def checkout(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related(
        'product_variant', 'product_variant__product'
    ).all()

    if not items:
        return redirect('orders:cart')

    addresses = Address.objects.filter(user=request.user)

    context = {
        'cart': cart,
        'items': items,
        'addresses': addresses,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@require_POST
def create_order(request):
    """Create Razorpay order and Django order."""
    cart = _get_or_create_cart(request)
    items = cart.items.select_related('product_variant', 'product_variant__product').all()

    if not items:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    # Get address data
    address_id = request.POST.get('address_id')
    if address_id:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        addr_full_name = address.full_name
        addr_phone = address.phone
        addr_line1 = address.address_line1
        addr_city = address.city
        addr_state = address.state
        addr_pincode = address.pincode
    else:
        addr_full_name = request.POST.get('full_name', '')
        addr_phone = request.POST.get('phone', '')
        addr_line1 = request.POST.get('address_line1', '')
        addr_city = request.POST.get('city', '')
        addr_state = request.POST.get('state', '')
        addr_pincode = request.POST.get('pincode', '')

        # Save address if requested
        if request.POST.get('save_address'):
            Address.objects.create(
                user=request.user,
                full_name=addr_full_name,
                phone=addr_phone,
                address_line1=addr_line1,
                city=addr_city,
                state=addr_state,
                pincode=addr_pincode,
            )

    # Create Django order
    order = Order.objects.create(
        customer=request.user,
        address_full_name=addr_full_name,
        address_phone=addr_phone,
        address_line1=addr_line1,
        address_city=addr_city,
        address_state=addr_state,
        address_pincode=addr_pincode,
        total_amount=cart.grand_total,
        delivery_charge=cart.delivery_charge,
        status='pending',
        payment_status='pending',
    )

    # Create order items with price_at_purchase
    for item in items:
        OrderItem.objects.create(
            order=order,
            product_variant=item.product_variant,
            product_name=item.product_variant.product.name,
            variant_label=item.product_variant.weight_label,
            quantity=item.quantity,
            price_at_purchase=item.product_variant.price,
        )

    # Create Razorpay order
    amount_paise = int(cart.grand_total * 100)

    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
        })
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order['id'],
            amount=cart.grand_total,
        )

        return JsonResponse({
            'order_id': razorpay_order['id'],
            'amount': amount_paise,
            'key_id': settings.RAZORPAY_KEY_ID,
            'django_order_id': order.id,
            'customer_name': request.user.get_full_name(),
            'customer_email': request.user.email,
            'customer_phone': addr_phone,
        })
    except Exception as e:
        # If Razorpay fails, still save order for manual payment
        order.razorpay_order_id = f'MANUAL-{order.id}'
        order.payment_status = 'paid'
        order.status = 'processing'
        order.save()

        Payment.objects.create(
            order=order,
            razorpay_order_id=f'MANUAL-{order.id}',
            amount=cart.grand_total,
            status='success',
            paid_at=timezone.now(),
        )

        # Reduce stock
        for item in order.order_items.all():
            if item.product_variant:
                ProductVariant.objects.filter(id=item.product_variant.id).update(
                    stock_quantity=F('stock_quantity') - item.quantity
                )

        # Clear cart
        cart.items.all().delete()

        return JsonResponse({
            'error': str(e),
            'fallback': True,
            'django_order_id': order.id,
        }, status=500)


@login_required
@require_POST
def payment_success(request):
    """Verify Razorpay payment and confirm order."""
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')
    django_order_id = request.POST.get('django_order_id', '')

    try:
        order = Order.objects.get(id=django_order_id, customer=request.user)
    except Order.DoesNotExist:
        return redirect('orders:payment_failed')

    # Verify signature
    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        verified = True
    except Exception:
        verified = False

    if verified:
        # Update order
        order.payment_status = 'paid'
        order.status = 'processing'
        order.save()

        # Update payment
        payment = order.payment
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'success'
        payment.paid_at = timezone.now()
        payment.save()

        # Reduce stock atomically
        for item in order.order_items.all():
            if item.product_variant:
                ProductVariant.objects.filter(id=item.product_variant.id).update(
                    stock_quantity=F('stock_quantity') - item.quantity
                )

        # Clear cart
        cart = _get_or_create_cart(request)
        cart.items.all().delete()

        # Send confirmation email
        try:
            send_mail(
                subject=f'Order Confirmed — #{order.id} | MJ Ekdantay Masala Centre',
                message=f'Thank you for your order! Your order #{order.id} has been placed successfully. Total: ₹{order.total_amount}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        return render(request, 'orders/payment_success.html', {'order': order})
    else:
        return redirect('orders:payment_failed')


def payment_success_page(request):
    """GET version for redirect after successful payment."""
    order_id = request.GET.get('order_id')
    if order_id and request.user.is_authenticated:
        try:
            order = Order.objects.get(id=order_id, customer=request.user)
            # Safety net: clear cart after successful order
            cart = _get_or_create_cart(request)
            cart.items.all().delete()
            return render(request, 'orders/payment_success.html', {'order': order})
        except Order.DoesNotExist:
            pass
    return render(request, 'orders/payment_success.html', {})


def payment_failed(request):
    return render(request, 'orders/payment_failed.html')
