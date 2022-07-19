import pytest

from ..forms import PaymentForm, UpdatePaymentForm
from ..models import Payment
from .factories import PaymentFactory, PaymentFormFactory

pytestmark = pytest.mark.django_db


def test_clean_transaction_amount(order):
    form = PaymentForm(
        order=order,
        data=PaymentFormFactory(transaction_amount=order.get_total()),
    )
    assert form.is_valid()

    form = PaymentForm(
        order=order,
        data=PaymentFormFactory(
            transaction_amount=str(float(order.get_total()) + 1.0)
        ),
    )
    assert not form.is_valid()
    assert form.errors["transaction_amount"] == [
        "Negado! Valor da transação difere do valor da compra!"
    ]


def test_save(order, mocker):
    assert not order.paid

    form = PaymentForm(
        order=order,
        data=PaymentFormFactory(transaction_amount=order.get_total()),
    )
    
    assert form.is_valid()

    mocker.patch(
        "mercadopago.resources.Payment.create",
        return_value={
            "status": 201,
            "response": {
                "id": "1234",
                "status_detail": "accredited",
                "status": "approved",
            },
        },
    )
    form.save()
    order.refresh_from_db()
    assert order.paid
    payment = Payment.objects.get(mercado_pago_id="1234")
    assert payment.mercado_pago_status == "approved"
    assert payment.mercado_pago_status_detail == "accredited"


def test_update_form_paid(order, mocker):
    assert not order.paid
    payment = PaymentFactory(order=order, mercado_pago_id="12345")
    form = UpdatePaymentForm(
        data={
            "action": "payment.updated",
            "data": {
                "id": "12345",
            },
        }
    )
    assert form.is_valid()
    mocker.patch(
        "mercadopago.resources.Payment.get",
        return_value={
            "response": {
                "status": "approved",
                "status_detail": "accredited",
            },
        },
    )
    form.save()
    order.refresh_from_db()
    payment.refresh_from_db()
    assert order.paid
    assert payment.mercado_pago_status == "approved"
    assert payment.mercado_pago_status_detail == "accredited"


def test_update_form_rejected(order, mocker):
    payment = PaymentFactory(
        order=order,
        mercado_pago_id="12345",
        mercado_pago_status="approved",
        mercado_pago_status_detail="accredited",
    )
    form = UpdatePaymentForm(
        data={
            "action": "payment.updated",
            "data": {
                "id": "12345",
            },
        }
    )
    assert form.is_valid()
    mocker.patch(
        "mercadopago.resources.Payment.get",
        return_value={
            "response": {
                "status": "rejected",
                "status_detail": "cc_rejected_other_reason",
            },
        },
    )
    form.save()
    order.refresh_from_db()
    payment.refresh_from_db()
    assert not order.paid
    assert payment.mercado_pago_status == "rejected"
    assert payment.mercado_pago_status_detail == "cc_rejected_other_reason"