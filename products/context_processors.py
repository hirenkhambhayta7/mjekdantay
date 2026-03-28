from .models import Category
from orders.models import Cart


def categories_processor(request):
    return {
        'all_categories': Category.objects.all()
    }
