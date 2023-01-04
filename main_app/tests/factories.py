# from products.tests.factories import ProductFactory
from decimal import Decimal
import factory
import factory.fuzzy

from datetime import datetime, timedelta
import random, pytz
from django.utils.text import slugify

from main_app.models import BillingAddress, Item, Order, Category, OrderItem, Coupon, UserProfile, Refund, LABEL_OPTIONS
from django.contrib.auth.models import User


LABELS_IDS = [x[0] for x in LABEL_OPTIONS]
TWOPLACES = Decimal(10) ** -2 # same as Decimal('0.01') - used to round two decimal places


class UserProfileFactory(factory.Factory):
    cpf = factory.Faker("cpf", locale="pt_BR")
    full_name = factory.Faker("name")
    cell_number = factory.Faker("phone_number", locale="pt_BR")

    class Meta:
        model = UserProfile


class UserFactory(factory.django.DjangoModelFactory):
    userprofile = factory.SubFactory(UserProfileFactory)
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = User
        django_get_or_create = ('userprofile',)


class CategoryFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText()
    description = factory.Faker("paragraph", nb_sentences=3, variable_nb_sentences=True)

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)

    class Meta:
        model = Category


class CouponFactory(factory.django.DjangoModelFactory):
    code = factory.fuzzy.FuzzyText()
    amount = factory.fuzzy.FuzzyDecimal(10.0, 9999.99)
    is_active = factory.Faker("pybool")

    class Meta:
        model = Coupon


class ItemFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText()
    description = factory.Faker("paragraph", nb_sentences=3, variable_nb_sentences=True)
    price = factory.fuzzy.FuzzyDecimal(10.0, 9999.99)
    discount_price = factory.LazyAttribute(lambda x: Decimal(random.uniform(5.0, float(x.price)/2.0)).quantize(TWOPLACES))
    # discount_price = factory.LazyAttribute(lambda x: factory.fuzzy.FuzzyDecimal(random.randrange(5, x.price/2)))
    category = factory.SubFactory(CategoryFactory)
    label = factory.fuzzy.FuzzyChoice(choices=LABELS_IDS)
    quantity = factory.Faker("random_int", min=10, max=500)
    image = factory.django.ImageField()

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)

    class Meta:
        model = Item

class BillingAddressFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    address = factory.Faker("street_name", locale="pt_BR")
    number = factory.Faker("building_number", locale="pt_BR")
    city = factory.Faker("city", locale="pt_BR")
    state = factory.Faker("estado_sigla", locale="pt_BR")
    zipcode = factory.Faker("postcode", locale="pt_BR")
    complement = factory.Faker("paragraph", nb_sentences=1)
    is_active = factory.Faker("pybool")
    default = factory.Faker("pybool")

    class Meta:
        model = BillingAddress

# @factory.django.mute_signals(post_save)
class OrderFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    start_date = factory.fuzzy.FuzzyDateTime(start_dt=datetime.now(pytz.timezone('America/Sao_Paulo')))
    finished = factory.Faker("pybool")
    finished_date = factory.fuzzy.FuzzyDateTime(start_dt=start_date.fuzz(), end_dt=start_date.fuzz()+timedelta(days=random.randint(0, 30), minutes=random.randint(10, 60)))
    items = factory.RelatedFactoryList('main_app.tests.factories.OrderItemFactory', size=3) # size=lambda: random.randint(1, 5)
    # items = factory.List([factory.SubFactory('main_app.tests.factories.OrderItemFactory')])
    billing_address = factory.SubFactory('main_app.tests.factories.BillingAddressFactory')
    paid = False
    payment = factory.SubFactory('mercadopago_payment.tests.factories.PaymentFactory')
    coupon = factory.SubFactory(CouponFactory)
    on_the_road = factory.Faker("pybool")
    delivered = factory.Faker("pybool")
    refund_requested = factory.Faker("pybool")
    refund_accepted = factory.Faker("pybool")
    ref_code = factory.Faker('uuid4')

    class Meta:
        model = Order
        # django_get_or_create = ('billing_address',)

    # it is being used to instantiate the RelatedFactoryList on the create method of conftest.py - otherwise the items field would be None
    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for item in extracted:
                # If sqlachemy orm is used change from add to append
                self.items.add(item)


# @factory.django.mute_signals(post_save)
class OrderItemFactory(factory.django.DjangoModelFactory):
    user_order = factory.SubFactory(OrderFactory)
    item = factory.SubFactory(ItemFactory)
    quantity = factory.Faker("random_int", min=1, max=10)
    finished = factory.Faker("pybool")

    class Meta:
        model = OrderItem


class RefundFactory(factory.django.DjangoModelFactory):
    user_order = factory.SubFactory(OrderFactory)
    reason = factory.Faker("paragraph", nb_sentences=3, variable_nb_sentences=True)
    accepted = False
    email = factory.Faker("email")

    class Meta:
        model = Refund