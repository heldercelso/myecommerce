from decimal import Decimal
import pytest

from django.contrib.auth.models import User
from main_app.models import Item, UserProfile
from django.db.models import Q, Sum
from main_app.tests.factories import ItemFactory, OrderFactory, OrderItemFactory
from pytest_django.asserts import assertQuerysetEqual

pytestmark = pytest.mark.django_db

########################################################
##################### USER TESTS #######################
########################################################


def test_create_user():
    user = User.objects.create_user(
        username="usuario_test", email="usuario@test.com", password="passw0rd"
    )

    assert user.username == "usuario_test"
    assert user.email == "usuario@test.com"
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


def test_create_superuser():
    user = User.objects.create_superuser(
        username="admin_test", email="admin@test.com", password="passw0rd"
    )
    assert user.username == "admin_test"
    assert user.email == "admin@test.com"
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser

def test_login_user(client):
    user = User.objects.get_or_create(username='testuser', email='testemail@test.com')[0]
    user.set_password('testpass')
    user.save()

    logged_in = client.login(username='testuser', password='testpass')
    assert logged_in
    client.logout()

    logged_in = client.login(email='testemail@test.com', password='testpass')
    assert logged_in
    client.logout()

    user_profile = UserProfile.objects.get(user=user)
    assert user_profile


#################################################################
#################### PRODUCT/CATEGORY TESTS #####################
#################################################################


class TestCategoryModel:
    def test_category__str__(self, category): # category is a fixture created on conftest.py
        # test str function declared on models
        assert category.__str__() == category.title
        assert str(category) == category.title


class TestItemModel:
    def test___str__(self, product): # product is a fixture created on conftest.py
        # test str function declared on models
        assert product.__str__() == product.title
        assert str(product) == product.title

    def test_get_url(self, product):
        # test get_url function declared on models
        url = product.get_url()
        assert url == f"/product/{product.slug}/{product.id}/"

    def test_get_add_item_to_cart_url(self, product):
        # test get_url function declared on models
        url = product.get_add_item_to_cart_url()
        assert url == f"/cart-item/add/{product.slug}/{product.id}/product/"

    def test_get_remove_item_from_cart_url(self, product):
        # test get_url function declared on models
        url = product.get_remove_item_from_cart_url()
        assert url == f"/cart-item/remove/{product.slug}/{product.id}/product/"

    def test_get_delete_item_from_cart_url(self, product):
        # test get_url function declared on models
        url = product.get_delete_item_from_cart_url()
        assert url == f"/cart-item/delete/{product.slug}/{product.id}/product/"

    def test_available_products(self):
        # test product quantity
        ItemFactory(quantity=5)
        ItemFactory(quantity=2)
        ItemFactory(quantity=0)

        assert Item.objects.count() == 3
        assert Item.objects.filter(quantity__gt=0).count() == 2
        assert Item.objects.aggregate(Sum('quantity')).get('quantity__sum') == 7

        # query check: all products should be equal to all products with quantity greater or equal to 0
        assertQuerysetEqual(
            Item.objects.all(),
            Item.objects.filter(quantity__gte=0),
            transform=lambda x: x,
        )


######################################################
#################### ORDERITEM TESTS #################
######################################################

class TestOrderItemModel:
    def test_orderitem__str__(self, orderitem):
        assert orderitem.__str__() == f"{orderitem.quantity} de {orderitem.item.title}"
        assert str(orderitem) == f"{orderitem.quantity} de {orderitem.item.title}"

    def test_orderitem_get_total_price(self, orderitem):
        assert orderitem.get_total_price() == orderitem.quantity * orderitem.item.price

        order_factory = OrderFactory(items=None, payment=None)
        orderitem2 = OrderItemFactory(user_order=order_factory, quantity=3)
        assert orderitem2.get_total_price() ==  3 * orderitem2.item.price

    def test_orderitem_get_total_discount_price(self, orderitem):
        assert orderitem.get_total_discount_price() == orderitem.quantity * orderitem.item.discount_price

        order_factory = OrderFactory(items=None, payment=None)
        orderitem2 = OrderItemFactory(user_order=order_factory, quantity=3)
        assert orderitem2.get_total_discount_price() ==  3 * orderitem2.item.discount_price

    def test_orderitem_get_discount_amount(self, orderitem):
        assert orderitem.get_discount_amount() == orderitem.get_total_price() - orderitem.get_total_discount_price()

        order_factory = OrderFactory(items=None, payment=None)
        orderitem2 = OrderItemFactory(user_order=order_factory, quantity=3)
        assert orderitem2.get_discount_amount() == 3 * orderitem2.item.price - 3 * orderitem2.item.discount_price


######################################################
#################### ORDER TESTS #####################
######################################################

class TestOrderModel:
    def test_order__str__(self, order):
        assert order.__str__() == f"{order.user.username}"
        assert str(order) == f"{order.user.username}"

    def test_order_get_total_price(self, order):
        # total=0
        total_with_discount=0

        for orderitem in order.items.all():
            # total += float("{:.2f}".format(orderitem.item.price * orderitem.quantity))
            total_with_discount += orderitem.item.discount_price * orderitem.quantity
            assert orderitem.get_total_price() == orderitem.item.price * orderitem.quantity
            assert orderitem.get_total_discount_price() == orderitem.item.discount_price * orderitem.quantity
        if order.coupon:
            # total -= float("{:.2f}".format(order.coupon.amount))
            total_with_discount -= order.coupon.amount
        assert order.get_total() == total_with_discount

    def test_order_get_total(self, order):
        result = order.get_total_price()
        if order.coupon:
            result -= order.coupon.amount
        assert order.get_total() ==  result

    def test_order_get_total_items(self, order):
        result = 0
        for order_item in order.items.all():
            result += order_item.quantity
        assert order.get_total_items() == result

    def test_order_get_description(self, order):
        description = ", ".join([f"{order_item.quantity} x {order_item.item.title}" for order_item in order.items.all()])
        assert order.get_description() == description


######################################################
################ BILLING ADDRESS TESTS ###############
######################################################


def test_billingaddress__str__(billingaddress):
    assert billingaddress.__str__() == f"{billingaddress.address}, {billingaddress.number} - {billingaddress.city}, {billingaddress.state}"
    assert str(billingaddress) == f"{billingaddress.address}, {billingaddress.number} - {billingaddress.city}, {billingaddress.state}"


######################################################
#################### COUPON TESTS ####################
######################################################


def test_coupon__str__(coupon):
    assert coupon.__str__() == coupon.code
    assert str(coupon) == coupon.code


# ######################################################
# #################### REFUND TESTS ####################
# ######################################################


def test_refund__str__(refund):
    assert refund.__str__() == str(refund.pk)
    assert str(refund) == str(refund.pk)