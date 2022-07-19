import json
# from multiprocessing import Queue
# import queue

import pytest
from django.urls import resolve, reverse

from main_app.models import Order
from main_app.tests.factories import ItemFactory
from mercadopago_payment.forms import PaymentForm
from mercadopago_payment.models import Payment
from .factories import PaymentFactory, PaymentFormFactory
from ..utils import DecimalEncoder
# import threading
pytestmark = pytest.mark.django_db
# import django_thread


@pytest.fixture
def client_with_order(logged_user, client, product):
    client.post(
        reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}),
        follow=True
    )
    # just to create the session id
    client.get(reverse("mycart"))

    order = Order.objects.get(user=logged_user, payment=None)

    return order


def test_reverse_resolve():
    assert reverse("payments:process") == "/payments/process/"
    assert resolve("/payments/process/").view_name == "payments:process"

    assert reverse("payments:failure") == "/payments/failure/"
    assert resolve("/payments/failure/").view_name == "payments:failure"

    assert reverse("payments:pending") == "/payments/pending/"
    assert resolve("/payments/pending/").view_name == "payments:pending"

    assert reverse("payments:success") == "/payments/success/"
    assert resolve("/payments/success/").view_name == "payments:success"

    assert reverse("payments:webhook") == "/payments/webhook/"
    assert resolve("/payments/webhook/").view_name == "payments:webhook"


def test_status_code(client):
    response = client.get(reverse("payments:process"))
    assert response.status_code == 404

    response = client.get(reverse("payments:failure"))
    assert response.status_code == 200

    response = client.get(reverse("payments:pending"))
    assert response.status_code == 200

    response = client.get(reverse("payments:success"))
    assert response.status_code == 200

    response = client.get(reverse("payments:webhook"))
    assert response.status_code == 405


def test_double_payment_same_product(mocker, order_gen):
    # def teste2(item2):
    item = ItemFactory(quantity=1)
    order1 = order_gen(item, orditem_quantity=1)
    order2 = order_gen(item, orditem_quantity=1)

    form1 = PaymentForm(
        order=order1,
        data=PaymentFormFactory(transaction_amount=order1.get_total()),
    )
    form2 = PaymentForm(
        order=order2,
        data=PaymentFormFactory(transaction_amount=order2.get_total()),
    )
    assert form1.is_valid()
    assert form2.is_valid()
    mocker.patch(
        "mercadopago.resources.Payment.create",
        return_value={
            "status": 201,
            "response": {
                "id": "135",
                "status_detail": "accredited",
                "status": "approved",
            },
        },
    )

    form1.save()
    msg = form2.save()
    assert msg == 'Infelizmente o produto já foi vendido e saiu de estoque.'
    
    payment1 = Payment.objects.get(mercado_pago_id="135")
    assert payment1.mercado_pago_status == "approved"


def test_payment_success(client_with_order, client, mocker):
    mocker.patch(
        "mercadopago.resources.Payment.create",
        return_value={
            "status": 201,
            "response": {
                "id": "123",
                "status_detail": "accredited",
                "status": "approved",
            },
        },
    )
    payment_data = PaymentFormFactory(transaction_amount=client_with_order.get_total())

    response = client.post(
        reverse("payments:process"),
        #, 'cls=DecimalEncoder' is just to avoid the error TypeError: Object of type Decimal is not JSON serializable
        json.dumps(payment_data, cls=DecimalEncoder),
        content_type="application/json;"
    )

    assert response.json()['redirect_url'] == '/payments/success/'
    # assertTemplateUsed(response, "mercadopago_payment/success.html")


def test_payment_failure(client_with_order, client, mocker):
    mocker.patch(
        "mercadopago.resources.Payment.create",
        return_value={
            "status": 201,
            "response": {
                "id": "123",
                "status_detail": "cc_rejected_bad_filled_card_number",
                "status": "rejected",
            },
        },
    )

    payment_data = PaymentFormFactory(transaction_amount=client_with_order.get_total())
    response = client.post(
        reverse("payments:process"),
        json.dumps(payment_data, cls=DecimalEncoder),
        content_type="text/html;"
    )
    assert response.json()['errors']['Erro'][0]['message'] == 'Revise o número do cartão.'
    # assert response.json()['redirect_url'] == '/payments/failure/'
    # assertTemplateUsed(response, "mercadopago_payment/failure.html")


def test_payment_pending(client_with_order, client, mocker):
    mocker.patch(
        "mercadopago.resources.Payment.create",
        return_value={
            "status": 201,
            "response": {
                "id": "123",
                "status_detail": "pending_review_manual",
                "status": "in_process",
            },
        },
    )
    payment_data = PaymentFormFactory(transaction_amount=client_with_order.get_total())
    response = client.post(
        reverse("payments:process"),
        json.dumps(payment_data, cls=DecimalEncoder),
        content_type="text/html;"
    )
    assert response.json()['redirect_url'] == '/payments/pending/'
    # assertTemplateUsed(response, "payments/pending.html")


def test_payment_webhook(order, client, mocker):
    PaymentFactory(order=order, mercado_pago_id="12345")
    mocker.patch(
        "mercadopago.resources.Payment.get",
        return_value={
            "response": {
                "status": "approved",
                "status_detail": "accredited",
            },
        },
    )
    payment_data = {
        "action": "payment.updated",
        "data": {
            "id": "12345",
        },
    }
    response = client.post(
        reverse("payments:webhook"),
        json.dumps(payment_data, cls=DecimalEncoder),
        content_type="application/json",
    )
    assert response.status_code == 200


# def test_save(mocker, order_gen):
#     item = ItemFactory(quantity=1)
#     order1 = order_gen(item, orditem_quantity=1)
#     # order2 = order_gen(item, orditem_quantity=1)
#     # orderitems = list(order1.items.all())

#     form1 = PaymentForm(
#         order=order1,
#         data=PaymentFormFactory(transaction_amount=order1.get_total()),
#     )
#     # form2 = PaymentForm(
#     #     order=order2,
#     #     data=PaymentFormFactory(transaction_amount=order2.get_total()),
#     # )
#     assert form1.is_valid()
#     # assert form2.is_valid()
#     mocker.patch(
#         "mercadopago.resources.Payment.create",
#         return_value={
#             "status": 201,
#             "response": {
#                 "id": "135",
#                 "status_detail": "accredited",
#                 "status": "approved",
#             },
#         },
#     )

#     def save_form(form, queue_res1):
#         form.save(queue_res1)

#     queue_res1 = queue.Queue()
#     # x1 = threading.Thread(target=save_form, args=[form1, queue_res1, order1.items.all()])
#     x1 = threading.Thread(target=save_form, args=[form1, queue_res1])
#     # x1.daemon = True
#     # queue_res2 = queue.Queue()
#     # x2 = threading.Thread(target=form2.save(queue_res2))
#     # x2.daemon = True

#     # x2.start()
#     x1.start()
    
#     # x2.join()
#     x1.join()
#     assert queue_res1.empty() == False
#     # assert queue_res1.empty() == True

#     msg1 = queue_res1.get(timeout=5)
#     assert msg1 == "Pagamento efetuado."

#     # msg2 = queue_res2.get(timeout=5)
#     # assert msg2 == "Infelizmente o produto já foi vendido e saiu de estoque."

#     # assert msg == 'Infelizmente o produto já foi vendido e saiu de estoque.'
#     # mocker.patch(
#     #     "mercadopago.resources.Payment.create",
#     #     return_value={
#     #         "status": 201,
#     #         "response": {
#     #             "id": "159",
#     #             "status_detail": "accredited",
#     #             "status": "approved",
#     #         },
#     #     },
#     # )
#     payment1 = Payment.objects.get(mercado_pago_id="135")
#     assert payment1.mercado_pago_status == "approved"