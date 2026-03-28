from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.views import merge_cart_on_login
from orders.models import Order
from .forms import UserRegistrationForm, UserProfileForm, AddressForm, LoginForm
from .models import Address


def register_view(request):
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            merge_cart_on_login(request)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('products:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            from django.contrib.auth.models import User
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                merge_cart_on_login(request)
                messages.success(request, f'Welcome back, {user.first_name}!')
                next_url = request.GET.get('next', 'products:home')
                if next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('products:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        if form.is_valid():
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)

    addresses = Address.objects.filter(user=request.user)
    context = {
        'form': form,
        'addresses': addresses,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('accounts:profile')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add Address'})


@login_required
def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('accounts:profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Address'})


@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted.')
    return redirect('accounts:profile')


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related('order_items')

    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related('order_items', 'order_items__product_variant'),
        pk=pk, customer=request.user
    )
    return render(request, 'accounts/order_detail.html', {'order': order})
