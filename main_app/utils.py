from django.contrib import messages
import json
from main_app.models import Item

def cookieCart(request):
    #Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
    except Exception as e:
        cart = {}

    items = {'all': []}
    order = {'get_total':0, 'get_cart_items':0, 'items': items}
    # cartItems = order['get_cart_items']

    for key, value in cart.items():
        #We use try block to prevent items in cart that may have been removed from causing error
        try:
            # if(value['quantity']>0): #items with negative quantity = lot of freebies
            requested_quantity = value['quantity'] # cart quantity
            # cartItems += requested_quantity

            prod_key = key.split('/')
            slug, pk = prod_key[0], prod_key[1]
            
            product = Item.objects.get(slug=slug, pk=pk)

            total_price = product.price * requested_quantity
            total_discount_price = product.discount_price * requested_quantity if product.discount_price else 0

            if total_discount_price > 0: order['get_total'] += total_discount_price
            else: order['get_total'] += total_price
            order['get_cart_items'] += requested_quantity

            total_discount_amount = total_price - total_discount_price if total_discount_price > 0 else 0
            cartitem = {
                'item': {'slug': slug, 'pk': pk, 'title': product.title,
                        'price': product.price, 'discount_price': product.discount_price, 
                        'image': {'url': product.image.url},
                        'get_url': product.get_url,
                        'quantity': product.quantity, # stock quantity
                        },
                'quantity': requested_quantity, # cart quantity
                'get_total_price': total_price,
                'get_total_discount_price': total_discount_price,
                'get_discount_amount': total_discount_amount
            }
            items['all'].append(cartitem)
        except Exception as error:
            messages.error(request, 'cookieCart utils: ' + error)
            pass

    return {'order': order}