import pytest
import uuid

from main_app.tests.factories import CategoryFactory, ItemFactory, OrderFactory, OrderItemFactory, BillingAddressFactory, CouponFactory, RefundFactory
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async


# temporary folder for media creations
@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def category():
    return CategoryFactory()


@pytest.fixture
def coupon():
    return CouponFactory()


@pytest.fixture
def refund():
    order_factory = OrderFactory(items=None, payment=None)
    return RefundFactory(user_order=order_factory)


@pytest.fixture
def product():
    return ItemFactory()
@pytest.fixture
def product2():
    return ItemFactory(quantity=1)


@pytest.fixture
def billingaddress():
    return BillingAddressFactory()


@pytest.fixture
def order():
    suborder_factory = OrderFactory(payment=None, items=None)
    order_factory = OrderFactory.create(items=(OrderItemFactory(user_order=suborder_factory), 
                                               OrderItemFactory(user_order=suborder_factory),
                                               OrderItemFactory(user_order=suborder_factory)),
                                        payment__order=suborder_factory,
                                        items__user_order=suborder_factory)

    # return OrderFactory(payment__order=suborder_factory, items__user_order=suborder_factory)
    return order_factory


@pytest.fixture
def orderitem():
    order_factory = OrderFactory(items=None, payment=None)
    return OrderItemFactory(user_order=order_factory)
    # orderitem_factory = OrderItemFactory(user_order=None)
    # order_factory = OrderFactory(payment=None, items=None)
    # return OrderItemFactory(user_order__items__user_order=order_factory, user_order__payment__order=order_factory)

@pytest.fixture
def logged_user(client):
    user = User.objects.get_or_create(username='testuser', email='testemail@test.com')[0]
    user.set_password('testpass')
    user.save()

    client.login(username='testuser', password='testpass')

    return user

@pytest.fixture
def logged_client(client):
    user = User.objects.get_or_create(username='testuser', email='testemail@test.com')[0]
    user.set_password('testpass')
    user.save()

    client.login(username='testuser', password='testpass')

    return client


@pytest.fixture
def test_password():
   return 'strong-test-pass'


@pytest.fixture
def create_user(db, django_user_model, test_password):
   def make_user(**kwargs):
       kwargs['password'] = test_password
       if 'username' not in kwargs:
           kwargs['username'] = str(uuid.uuid4())
       return django_user_model.objects.create_user(**kwargs)
   return make_user


@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
   def make_auto_login(user=None):
       if user is None:
           user = create_user()
       client.login(username=user.username, password=test_password)
       return client, user
   return make_auto_login


@pytest.fixture
def orditem_gen():
    def orditem(item, orditem_quantity=1):
        # item = ItemFactory(quantity=1)
        suborder_factory = OrderFactory(payment=None, items=None)
        oi = OrderItemFactory(user_order=suborder_factory, item=item, quantity=orditem_quantity)
        return oi
    return orditem


@pytest.fixture
def order_gen(orditem_gen):
    def order(item, orditem_quantity=1):
        suborder_factory1 = OrderFactory(payment=None, items=None)
        suborder_factory2 = OrderFactory(payment=None, items=None)
        ord1 = OrderItemFactory(user_order=OrderFactory(payment=None, items=None))
        ord2 = OrderItemFactory(user_order=OrderFactory(payment=None, items=None))
        order_factory = OrderFactory.create(items=(orditem_gen(item, orditem_quantity),
                                                                 ord1,
                                                                 ord2
                                                  ),
                                            payment__order=suborder_factory1,
                                            items__user_order=suborder_factory2
                                           )
                                      

        # return OrderFactory(payment__order=suborder_factory, items__user_order=suborder_factory)
        return order_factory
    return order