/* ============================================
   MJ Ekdantay Masala Centre — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // CSRF Token helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // ========================================
    // Toast Notifications
    // ========================================
    window.showToast = function(message, type = 'success') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const icon = type === 'success' ? '✓' : '✕';
        const toast = document.createElement('div');
        toast.className = `custom-toast ${type === 'error' ? 'error' : ''}`;
        toast.innerHTML = `<span style="font-size:1.2rem;color:${type === 'success' ? 'var(--success)' : 'var(--danger)'}">${icon}</span><span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };

    // ========================================
    // Add to Cart (AJAX)
    // ========================================
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const btn = this.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            btn.disabled = true;

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                    // Update cart badge
                    const badge = document.querySelector('.cart-count-badge');
                    if (badge) {
                        badge.textContent = data.cart_count;
                        badge.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
                    }
                } else {
                    showToast(data.error || 'Error adding to cart', 'error');
                }
            })
            .catch(() => showToast('Something went wrong', 'error'))
            .finally(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            });
        });
    });

    // ========================================
    // Cart Page: Update Quantity (AJAX)
    // ========================================
    document.querySelectorAll('.cart-qty-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const action = this.dataset.action;
            const qtyDisplay = document.querySelector(`#qty-${itemId}`);
            let currentQty = parseInt(qtyDisplay.textContent);

            if (action === 'increase') currentQty++;
            else if (action === 'decrease') currentQty--;

            if (currentQty < 1) {
                // Remove item
                removeCartItem(itemId);
                return;
            }

            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('quantity', currentQty);

            fetch('/cart/update/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    qtyDisplay.textContent = data.quantity;
                    document.querySelector(`#line-total-${itemId}`).textContent = '₹' + data.line_total.toFixed(2);
                    updateCartSummary(data);
                }
            });
        });
    });

    function removeCartItem(itemId) {
        const formData = new FormData();
        formData.append('item_id', itemId);

        fetch('/cart/remove/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const row = document.querySelector(`#cart-row-${itemId}`);
                if (row) {
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(-20px)';
                    row.style.transition = 'all 0.3s ease';
                    setTimeout(() => {
                        row.remove();
                        updateCartSummary(data);
                        if (data.cart_count === 0) location.reload();
                    }, 300);
                }
            }
        });
    }

    // Remove buttons
    document.querySelectorAll('.cart-remove-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            removeCartItem(this.dataset.itemId);
        });
    });

    function updateCartSummary(data) {
        const subtotalEl = document.getElementById('cart-subtotal');
        const deliveryEl = document.getElementById('cart-delivery');
        const grandTotalEl = document.getElementById('cart-grand-total');
        const badgeEl = document.querySelector('.cart-count-badge');

        if (subtotalEl) subtotalEl.textContent = '₹' + data.subtotal.toFixed(2);
        if (deliveryEl) {
            deliveryEl.textContent = data.delivery_charge > 0 ? '₹' + data.delivery_charge.toFixed(2) : 'FREE';
        }
        if (grandTotalEl) grandTotalEl.textContent = '₹' + data.grand_total.toFixed(2);
        if (badgeEl) {
            badgeEl.textContent = data.cart_count;
            badgeEl.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
        }
    }

    // ========================================
    // Product Detail: Variant Selector
    // ========================================
    document.querySelectorAll('.variant-select-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.variant-select-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const price = this.dataset.price;
            const stock = parseInt(this.dataset.stock);
            const variantId = this.dataset.variantId;

            // Update price
            const priceEl = document.getElementById('variant-price');
            if (priceEl) priceEl.textContent = '₹' + parseFloat(price).toFixed(2);

            // Update stock badge
            const stockBadge = document.getElementById('stock-badge');
            if (stockBadge) {
                if (stock > 0) {
                    stockBadge.className = 'stock-badge in-stock';
                    stockBadge.innerHTML = '● In Stock';
                } else {
                    stockBadge.className = 'stock-badge out-of-stock';
                    stockBadge.innerHTML = '● Out of Stock';
                }
            }

            // Update hidden variant ID
            const hiddenInput = document.getElementById('selected-variant-id');
            if (hiddenInput) hiddenInput.value = variantId;

            // Enable/disable add to cart button
            const addBtn = document.getElementById('add-to-cart-btn');
            if (addBtn) addBtn.disabled = stock <= 0;
        });
    });

    // ========================================
    // Product Detail: Quantity Spinner
    // ========================================
    const qtyIncrease = document.getElementById('qty-increase');
    const qtyDecrease = document.getElementById('qty-decrease');
    const qtyInput = document.getElementById('qty-input');

    if (qtyIncrease && qtyDecrease && qtyInput) {
        qtyIncrease.addEventListener('click', () => {
            qtyInput.value = parseInt(qtyInput.value) + 1;
        });
        qtyDecrease.addEventListener('click', () => {
            if (parseInt(qtyInput.value) > 1) {
                qtyInput.value = parseInt(qtyInput.value) - 1;
            }
        });
    }

    // ========================================
    // Checkout: Address Selection
    // ========================================
    document.querySelectorAll('.address-select-radio').forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('.address-card').forEach(card => card.classList.remove('active'));
            this.closest('.address-card').classList.add('active');

            // Toggle new address form
            const newForm = document.getElementById('new-address-form');
            if (newForm) {
                newForm.style.display = this.value === 'new' ? 'block' : 'none';
            }
        });
    });

    // ========================================
    // Checkout: Razorpay Payment
    // ========================================
    const payNowBtn = document.getElementById('pay-now-btn');
    if (payNowBtn) {
        payNowBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Validate address
            const selectedAddress = document.querySelector('input[name="address_choice"]:checked');
            if (!selectedAddress) {
                showToast('Please select or enter an address', 'error');
                return;
            }

            const btn = this;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

            // Collect form data
            const formData = new FormData();
            if (selectedAddress.value !== 'new') {
                formData.append('address_id', selectedAddress.value);
            } else {
                formData.append('full_name', document.getElementById('new-full-name').value);
                formData.append('phone', document.getElementById('new-phone').value);
                formData.append('address_line1', document.getElementById('new-address-line1').value);
                formData.append('city', document.getElementById('new-city').value);
                formData.append('state', document.getElementById('new-state').value);
                formData.append('pincode', document.getElementById('new-pincode').value);
                const saveAddr = document.getElementById('save-address-check');
                if (saveAddr && saveAddr.checked) formData.append('save_address', '1');
            }

            fetch('/checkout/create-order/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrftoken,
                },
            })
            .then(res => res.json())
            .then(data => {
                if (data.error && data.fallback) {
                    // Razorpay not configured — show success page
                    showToast('Order placed! (Payment gateway not configured)', 'success');
                    setTimeout(() => {
                        window.location.href = '/payment/success/page/?order_id=' + data.django_order_id;
                    }, 1500);
                    return;
                }

                if (data.error) {
                    showToast(data.error, 'error');
                    btn.disabled = false;
                    btn.innerHTML = '<i class="bi bi-shield-lock me-2"></i>Pay Now';
                    return;
                }

                // Open Razorpay popup
                const options = {
                    key: data.key_id,
                    amount: data.amount,
                    currency: 'INR',
                    name: 'MJ Ekdantay Masala Centre',
                    description: 'Order Payment',
                    order_id: data.order_id,
                    handler: function(response) {
                        // Send payment details for verification
                        const paymentForm = new FormData();
                        paymentForm.append('razorpay_payment_id', response.razorpay_payment_id);
                        paymentForm.append('razorpay_order_id', response.razorpay_order_id);
                        paymentForm.append('razorpay_signature', response.razorpay_signature);
                        paymentForm.append('django_order_id', data.django_order_id);

                        fetch('/payment/success/', {
                            method: 'POST',
                            body: paymentForm,
                            headers: { 'X-CSRFToken': csrftoken },
                        })
                        .then(res => {
                            if (res.redirected) {
                                window.location.href = res.url;
                            } else {
                                return res.text();
                            }
                        })
                        .then(html => {
                            if (html) {
                                document.open();
                                document.write(html);
                                document.close();
                            }
                        });
                    },
                    prefill: {
                        name: data.customer_name,
                        email: data.customer_email,
                        contact: data.customer_phone,
                    },
                    theme: { color: '#D4520A' },
                    modal: {
                        ondismiss: function() {
                            btn.disabled = false;
                            btn.innerHTML = '<i class="bi bi-shield-lock me-2"></i>Pay Now';
                        }
                    }
                };

                const rzp = new Razorpay(options);
                rzp.open();
            })
            .catch(err => {
                showToast('Something went wrong', 'error');
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-shield-lock me-2"></i>Pay Now';
            });
        });
    }

    // ========================================
    // Shop Page: Product Card Variant Pill click
    // ========================================
    document.querySelectorAll('.card-variant-pill').forEach(pill => {
        pill.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const card = this.closest('.product-card');
            card.querySelectorAll('.card-variant-pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');

            const price = this.dataset.price;
            const variantId = this.dataset.variantId;
            const priceEl = card.querySelector('.card-price-value');
            const variantInput = card.querySelector('.card-variant-input');

            if (priceEl) priceEl.textContent = '₹' + parseFloat(price).toFixed(2);
            if (variantInput) variantInput.value = variantId;
        });
    });
});
