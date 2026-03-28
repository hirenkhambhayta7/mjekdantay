from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta

from .models import Product, Category, ProductVariant
from .admin_forms import ProductForm, CategoryForm, ProductVariantFormSet
from orders.models import Order, OrderItem


# ──────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────

@staff_member_required
def dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()

    # Orders this month
    month_orders = Order.objects.filter(created_at__date__gte=thirty_days_ago).count()
    month_revenue = Order.objects.filter(
        created_at__date__gte=thirty_days_ago, payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Low stock variants (< 10 units)
    low_stock = ProductVariant.objects.filter(
        stock_quantity__lt=10
    ).select_related('product')[:10]

    # Recent orders
    recent_orders = Order.objects.select_related('customer').prefetch_related(
        'order_items'
    ).order_by('-created_at')[:10]

    # Top selling products
    top_products = OrderItem.objects.values(
        'product_name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'month_orders': month_orders,
        'month_revenue': month_revenue,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'total_products': total_products,
        'total_categories': total_categories,
        'active_page': 'dashboard',
    }
    return render(request, 'store_admin/dashboard.html', context)


# ──────────────────────────────────────────
# Orders
# ──────────────────────────────────────────

@staff_member_required
def orders_list(request):
    orders = Order.objects.select_related('customer').prefetch_related(
        'order_items'
    ).order_by('-created_at')

    # Filters
    status = request.GET.get('status', '')
    payment = request.GET.get('payment', '')
    search = request.GET.get('q', '')

    if status:
        orders = orders.filter(status=status)
    if payment:
        orders = orders.filter(payment_status=payment)
    if search:
        orders = orders.filter(
            Q(customer__email__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(id__icontains=search)
        )

    context = {
        'orders': orders,
        'status_filter': status,
        'payment_filter': payment,
        'search': search,
        'active_page': 'orders',
    }
    return render(request, 'store_admin/orders_list.html', context)


@staff_member_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('customer').prefetch_related(
            'order_items', 'order_items__product_variant'
        ), pk=pk
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}.')
            return redirect('store_admin:order_detail', pk=pk)

    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'active_page': 'orders',
    }
    return render(request, 'store_admin/order_detail.html', context)


@staff_member_required
def order_bulk_update(request):
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        new_status = request.POST.get('bulk_status')
        if order_ids and new_status:
            updated = Order.objects.filter(id__in=order_ids).update(status=new_status)
            messages.success(request, f'{updated} order(s) updated to {new_status}.')
    return redirect('store_admin:orders_list')


# ──────────────────────────────────────────
# Products
# ──────────────────────────────────────────

@staff_member_required
def products_list(request):
    products = Product.objects.select_related('category').prefetch_related('variants').order_by('-created_at')

    search = request.GET.get('q', '')
    category = request.GET.get('category', '')

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    if category:
        products = products.filter(category__slug=category)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'category_filter': category,
        'active_page': 'products',
    }
    return render(request, 'store_admin/products_list.html', context)


@staff_member_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductVariantFormSet(request.POST, prefix='variants')
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('store_admin:products_list')
    else:
        form = ProductForm()
        formset = ProductVariantFormSet(prefix='variants')

    context = {
        'form': form,
        'formset': formset,
        'title': 'Add Product',
        'active_page': 'products',
    }
    return render(request, 'store_admin/product_form.html', context)


@staff_member_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductVariantFormSet(request.POST, instance=product, prefix='variants')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('store_admin:products_list')
    else:
        form = ProductForm(instance=product)
        formset = ProductVariantFormSet(instance=product, prefix='variants')

    context = {
        'form': form,
        'formset': formset,
        'product': product,
        'title': f'Edit: {product.name}',
        'active_page': 'products',
    }
    return render(request, 'store_admin/product_form.html', context)


@staff_member_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
    return redirect('store_admin:products_list')


@staff_member_required
def product_toggle(request, pk):
    """Toggle product active/featured status via AJAX."""
    product = get_object_or_404(Product, pk=pk)
    field = request.POST.get('field', 'is_active')
    if field == 'is_active':
        product.is_active = not product.is_active
    elif field == 'is_featured':
        product.is_featured = not product.is_featured
    product.save()
    messages.success(request, f'{product.name}: {field} = {getattr(product, field)}')
    return redirect('store_admin:products_list')


# ──────────────────────────────────────────
# Categories
# ──────────────────────────────────────────

@staff_member_required
def categories_list(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')

    # Handle add/edit form submission
    edit_id = request.GET.get('edit')
    edit_category = None
    if edit_id:
        edit_category = get_object_or_404(Category, pk=edit_id)

    if request.method == 'POST':
        action = request.POST.get('action', 'add')

        if action == 'delete':
            cat_id = request.POST.get('category_id')
            cat = get_object_or_404(Category, pk=cat_id)
            cat_name = cat.name
            cat.delete()
            messages.success(request, f'Category "{cat_name}" deleted.')
            return redirect('store_admin:categories')

        if action == 'edit':
            cat_id = request.POST.get('category_id')
            cat = get_object_or_404(Category, pk=cat_id)
            form = CategoryForm(request.POST, request.FILES, instance=cat)
        else:
            form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Category saved successfully.')
            return redirect('store_admin:categories')
    else:
        if edit_category:
            form = CategoryForm(instance=edit_category)
        else:
            form = CategoryForm()

    context = {
        'categories': categories,
        'form': form,
        'edit_category': edit_category,
        'active_page': 'categories',
    }
    return render(request, 'store_admin/categories.html', context)


# ──────────────────────────────────────────
# Customers
# ──────────────────────────────────────────

@staff_member_required
def customers_list(request):
    from django.contrib.auth.models import User

    customers = User.objects.filter(
        is_staff=False
    ).annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).order_by('-date_joined')

    search = request.GET.get('q', '')
    if search:
        customers = customers.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    context = {
        'customers': customers,
        'search': search,
        'active_page': 'customers',
    }
    return render(request, 'store_admin/customers_list.html', context)
