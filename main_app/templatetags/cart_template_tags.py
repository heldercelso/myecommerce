import json
from django import template
from django.conf import settings
from main_app.models import Order
from babel.numbers import format_currency

register = template.Library()

def order(request):
    user_order = Order.objects.filter(user=request.user,
                                      payment__mercado_pago_status__in=[None, "null", "rejected"])
    if not user_order.exists():
        user_order = Order.objects.filter(user=request.user, payment__isnull=True)
    return user_order

@register.filter(name='count_cart_items')
def count_cart_items(request):
    result=0
    if request.user.is_authenticated:
        user_order = order(request)
        if user_order.exists():
            user_order = user_order.first()
            for order_item in user_order.items.all():
                result += (order_item.quantity)
            if result == 0 and 'cart' in request.COOKIES and request.COOKIES['cart']:
                try:
                    cart = json.loads(request.COOKIES['cart'])
                except:
                    cart = {}
                for i in cart:
                    result += cart[i]['quantity']
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        for i in cart:
            result += cart[i]['quantity']
    return result

@register.filter(name='currency_format')
def currency_format(decimal_value):
    return format_currency(decimal_value, settings.CURRENCY, locale=settings.LANGUAGE_CODE.replace("-", "_"))