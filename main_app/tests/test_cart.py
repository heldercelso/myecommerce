from django.urls import reverse
import pytest

from main_app.tests.factories import ItemFactory
from main_app.utils import cookieCart
from main_app.models import Order


pytestmark = pytest.mark.django_db

def test_create_empty_cookiecart(request):
    cookieData = cookieCart(request)
    user_order = cookieData['order']
    assert user_order['get_cart_items'] == 0
    assert user_order['get_total'] == 0
    assert user_order['items']['all'] == []


def test_create_empty_cart(logged_user, client, request):
    resp = client.get(reverse("mycart")) # just to create the order and session id

    order = Order.objects.get(user=logged_user, payment=None)
    assert order.items.exists() == False
    assert resp.context['request'].session['order_id'] == order.id


def test_get_non_empty_cart(logged_user, client, product):
    client.post(
        reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}),
    )

    order = Order.objects.get(user=logged_user, payment=None)
    assert order.items.exists()
    for orderitem in order.items.all():
        assert orderitem.quantity == 1


def test_add_product_to_empty_cart(logged_user, client, product):
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    order = Order.objects.get(user=logged_user, payment=None)
    assert order.items.count() == 1
    assert order.items.get(item=product, finished=False).quantity == 1


def test_add_product_to_empty_cart_quantity_gt_1(logged_user, client, product):
    client.get(reverse("mycart"))
    order = Order.objects.get(user=logged_user, payment=None)
    for quantity in range(0, 5):
        for orderitem in order.items.all():
            assert orderitem.quantity == quantity
        client.post(
            reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"})
        )
        assert order.items.count() == 1

def test_add_product_to_empty_cart_twice(logged_user, client, product):
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))

    product2 = ItemFactory()
    client.post(reverse("add-item-to-cart", kwargs={"slug": product2.slug, "pk": product2.pk, "dest": "product"}))

    order = Order.objects.get(user=logged_user, payment=None)
    assert order.items.count() == 2
    assert order.items.get(item=product, finished=False).quantity == 1
    assert order.items.get(item=product2, finished=False).quantity == 1


def test_remove_product(logged_user, client, product):
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("remove-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))

    order = Order.objects.filter(user=logged_user, payment=None).all()
    assert order.count() == 0

    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("remove-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("remove-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))

    order= order.first()
    assert order.items.count() == 1
    assert order.items.get(item=product, finished=False).quantity == 1


def test_remove_product_not_in_cart(logged_user, client, product):
    client.post(reverse("remove-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    order = Order.objects.filter(user=logged_user, payment=None).all()
    assert order.count() == 0

    client.post(reverse("delete-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    assert order.count() == 0


def test_delete_product(logged_user, client, product):
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("remove-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))

    order = Order.objects.filter(user=logged_user, payment=None).all()
    assert order.count() == 0

    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("delete-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))

    assert order.count() == 0


def test_cart_iter(logged_user, client):
    p1 = ItemFactory()
    p2 = ItemFactory()
    p3 = ItemFactory()

    client.post(reverse("add-item-to-cart", kwargs={"slug": p1.slug, "pk": p1.pk, "dest": "product"}))

    client.post(reverse("add-item-to-cart", kwargs={"slug": p2.slug, "pk": p2.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": p2.slug, "pk": p2.pk, "dest": "product"}))
    
    client.post(reverse("add-item-to-cart", kwargs={"slug": p3.slug, "pk": p3.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": p3.slug, "pk": p3.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": p3.slug, "pk": p3.pk, "dest": "product"}))

    products = [p1, p2, p3]
    quantities = [1, 2, 3]

    order = Order.objects.get(user=logged_user, payment=None)

    for product, quantity, orderitem in zip(products, quantities, order.items.all()):
        assert product.price == orderitem.item.price
        assert product.price * quantity == orderitem.get_total_price()
        assert product == orderitem.item
        assert orderitem.quantity == quantity


def test_cart_length(logged_user, client):
    p1 = ItemFactory()
    p2 = ItemFactory()

    order = Order.objects.filter(user=logged_user, payment=None).all()
    assert order.count() == 0

    client.post(reverse("add-item-to-cart", kwargs={"slug": p1.slug, "pk": p1.pk, "dest": "product"}))
    assert order.count() == 1
    assert order.first().items.count() == 1

    client.post(reverse("add-item-to-cart", kwargs={"slug": p2.slug, "pk": p2.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": p2.slug, "pk": p2.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": p2.slug, "pk": p2.pk, "dest": "product"}))
    assert order.count() == 1

    order=order.first()
    assert order.items.count() == 2

    orderitems = order.items.filter(finished=False)
    assert orderitems[0].quantity + orderitems[1].quantity == 4


def test_get_total_price(logged_user, client):
    p1 = ItemFactory()
    p2 = ItemFactory()

    client.post(reverse("add-item-to-cart", kwargs={"slug": p1.slug, "pk": p1.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": p2.slug, "pk": p2.pk, "dest": "product"}))
    client.post(reverse("add-item-to-cart", kwargs={"slug": p2.slug, "pk": p2.pk, "dest": "product"}))

    total_price = (p1.discount_price * 1) + (p2.discount_price * 2)

    order = Order.objects.get(user=logged_user, payment=None)
    assert order.get_total_price() == total_price


def test_cant_add_more_than_max_items(logged_user, product, client):
    client.get(reverse("mycart"))
    order = Order.objects.get(user=logged_user, payment=None)
    orderitems = order.items.filter(finished=False).all()

    # adding all product units
    for quantity in range(1, product.quantity+1):
        client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
        assert orderitems[0].quantity == quantity


    assert orderitems[0].quantity == product.quantity

    # adding additional units above the product quantity limit
    for _ in range(10):
        client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
        assert orderitems[0].quantity == product.quantity


def test_clear_cart(logged_user, client, product):

    for _ in range(1, product.quantity+1):
        client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
    client.post(reverse("delete-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))

    order = Order.objects.filter(user=logged_user, payment=None)
    assert order.count() == 0