import pytest

from .factories import PaymentFactory

pytestmark = pytest.mark.django_db


def test___str__(order):
    payment = PaymentFactory(order=order)
    assert payment.__str__() == f"{payment.mercado_pago_status} - M.Pago ID: {payment.mercado_pago_id}"
    assert str(payment) == f"{payment.mercado_pago_status} - M.Pago ID: {payment.mercado_pago_id}"