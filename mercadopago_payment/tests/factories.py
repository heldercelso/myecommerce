from decimal import Decimal
import factory

from main_app.tests.factories import OrderFactory

from mercadopago_payment.models import Payment


class PaymentFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    transaction_amount = Decimal(1.0)
    installments = factory.Faker("random_int", min=1, max=12)
    payment_method_id = "visa"
    card_holder = factory.Faker("name")
    email = factory.Faker("email")
    doc_type = "cpf"
    doc_number = factory.Faker("cpf", locale="pt_BR")
    mercado_pago_id = "123"
    mercado_pago_status = "rejected"
    mercado_pago_status_detail = "cc_rejected_other_reason"

    class Meta:
        model = Payment


class PaymentFormFactory(factory.DictFactory):
    transaction_amount = Decimal(1.0)
    installments = factory.Faker("random_int", min=1, max=12)
    payment_method_id = "master"
    email = factory.Faker("email")
    type = "CPF"
    number = factory.Faker("cpf", locale="pt_BR")
    card_holder = factory.Faker("name")#"APRO"
    token = factory.Faker("password", length=32, special_chars=False, upper_case=False)