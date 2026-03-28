from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min
from .models import Category, Product, ProductVariant


def home(request):
    featured_products = Product.objects.filter(
        is_active=True, is_featured=True
    ).select_related('category').prefetch_related('variants')[:6]
    categories = Category.objects.all()
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def shop(request):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('variants')

    # Search
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Category filter
    category_slugs = request.GET.getlist('category')
    if category_slugs:
        products = products.filter(category__slug__in=category_slugs)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.annotate(min_variant_price=Min('variants__price')).filter(
            min_variant_price__gte=min_price
        )
    if max_price:
        products = products.annotate(min_variant_price=Min('variants__price')).filter(
            min_variant_price__lte=max_price
        )

    # Sort
    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products = products.annotate(min_variant_price=Min('variants__price')).order_by('min_variant_price')
    elif sort == 'price_high':
        products = products.annotate(min_variant_price=Min('variants__price')).order_by('-min_variant_price')
    elif sort == 'name':
        products = products.order_by('name')

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_categories': category_slugs,
        'sort': sort,
    }
    return render(request, 'products/shop.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category, is_active=True
    ).select_related('category').prefetch_related('variants')

    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products = products.annotate(min_variant_price=Min('variants__price')).order_by('min_variant_price')
    elif sort == 'price_high':
        products = products.annotate(min_variant_price=Min('variants__price')).order_by('-min_variant_price')

    context = {
        'category': category,
        'products': products,
        'sort': sort,
    }
    return render(request, 'products/category.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('variants'),
        slug=slug, is_active=True
    )
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id).prefetch_related('variants')[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)
 