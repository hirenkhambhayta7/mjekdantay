from django import template

register = template.Library()


@register.filter
def currency(value):
    """Format a number as Indian Rupee currency."""
    try:
        return f'₹{float(value):,.2f}'
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
