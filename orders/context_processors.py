from .models import Cart


def cart_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            if not request.session.session_key:
                request.session.create()
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if cart:
            count = cart.total_items
    except Exception:
        pass
    return {'cart_item_count': count}
