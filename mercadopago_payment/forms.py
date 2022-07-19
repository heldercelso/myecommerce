import mercadopago
from django import forms
from django.conf import settings
from .models import Payment
from main_app.models import Item
from django.db.utils import OperationalError
import time
import traceback
from threading import Lock
from . import utils
lock = Lock()

# model/form name followed by names sent by process-payment.js (received as query_dict in the view)
# if the name is the same is not necessary to include here
FIELD_NAME_MAPPING = {
    'doc_type': 'type',
    'doc_number': 'number',
}

class PaymentForm(forms.ModelForm):
    token = forms.CharField(required=False)
    lista_lock = []

    class Meta:
        verbose_name="Pagamento"
        model = Payment
        fields = [ # required fields
            "transaction_amount",
            "installments",
            "payment_method_id",
            "email",
            "doc_type",
            "doc_number",
            "card_holder",
        ]

    # it being used just to receive the order passed in the PaymentForm instantiation on the views.py
    def __init__(self, *args, **kwargs):
        if "order" in kwargs:
            self.order = kwargs.pop("order")
        super(PaymentForm, self).__init__(*args, **kwargs)

    # this prefix is used to assign the form names with the names received on javascript POST
    def add_prefix(self, field_name):
        # look up field name; return original if not found
        field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
        return super(PaymentForm, self).add_prefix(field_name)

    # it was added to avoid some value change in the client-side
    def clean_transaction_amount(self):
        transaction_amount = float(self.cleaned_data["transaction_amount"])
        total = self.order.get_total()
        # print(transaction_amount, total)
        if transaction_amount != float(total):
            raise forms.ValidationError(
                "Negado! Valor da transação difere do valor da compra!"
            )
        return total

    def clear_product_wait(self):
        for orderitem in self.order.items.all():
            product = Item.objects.get(slug=orderitem.item.slug, pk=orderitem.item.pk)
            while f"{product.slug}_{product.pk}" in self.lista_lock:
                self.lista_lock.remove(f"{product.slug}_{product.pk}")

    def lock_products(self):
        for orderitem in self.order.items.all():
            product = Item.objects.get(slug=orderitem.item.slug, pk=orderitem.item.pk)
            count = 0
            # locking products that are already being sold
            # while f"{product.slug}_{product.pk}" in sum(self.lista_lock.values(), []):
            while f"{product.slug}_{product.pk}" in self.lista_lock:
                time.sleep(0.2)
                if count >= 5: # timeout
                    return False, 'Algo deu errado no pagamento ou o produto já foi vendido e saiu de estoque. Verifique e tente novamente.'
                else:
                    count += 0.2
            # if the product left the lista_lock so the user that locked it finalized its order and it is necessary to read the product again
            product = Item.objects.get(slug=orderitem.item.slug, pk=orderitem.item.pk)
            # if the stock is less than the order quantity so other user buyed the available units
            if product.quantity < orderitem.quantity:
                return False, 'Infelizmente o produto já foi vendido e saiu de estoque.'
            # if the product is available it is added in the lista_lock list to indicate it is being negotiated
            self.lista_lock.append(f"{product.slug}_{product.pk}")
            # self.lista_lock[self.order.user.username].append(f"{product.slug}_{product.pk}")
        return True, ''

    def save(self):
        try:
            # products that are being negotiated are kept in a list and the subsequents buyers of the same product needs to wait until it finishes
            lock.acquire()
            locked, msg = self.lock_products()
            lock.release()

            if not locked:
                # if queue: queue.put(msg) # just for testing with threads
                return msg
            
            # starting the payment by mercadopago
            cd = self.cleaned_data
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

            payment_data = {
                "transaction_amount": float(self.order.get_total()),
                "token": cd['token'],
                "description": self.order.get_description(),
                "installments": int(cd['installments']),
                "payment_method_id": cd['payment_method_id'],
                "payer": {
                    "first_name": cd['card_holder'],
                    "email": cd['email'],
                    "identification": {
                        "type": cd['doc_type'],
                        "number": cd['doc_number']},
                },
            }

            payment = sdk.payment().create(payment_data)
            if payment["status"] == 500:
                msg = "Erro interno com o servidor da pagadora. Recarregue e tente novamente. Caso o erro persista, entre em contato conosco."
                return msg

            elif payment["status"] == 201:
                self.instance.order = self.order
                self.instance.mercado_pago_id = payment["response"]["id"]
                self.instance.mercado_pago_status_detail = payment["response"]["status_detail"]
                self.instance.mercado_pago_status = payment["response"]["status"]
                
                self.order.payment = self.instance
                self.order.ref_code = utils.create_unique_ref_code()

                # order payment update
                if payment["response"]["status"] == "approved":
                    self.order.paid = True
                else:
                    self.order.paid = False

                # stock quantity update
                if payment["response"]["status"] in ["approved", "in_process", "in_mediation", "pending", "authorized"]:
                    order_items = self.order.items.all()
                    order_items.update(finished=True)
                    for orderitem in order_items:
                        orderitem.save()
                        product = Item.objects.get(slug=orderitem.item.slug, pk=orderitem.item.pk)
                        if product.quantity >= orderitem.quantity:
                            product.quantity -= orderitem.quantity
                        else:
                            product.quantity = 0
                        product.save()

                self.instance.save()
                self.order.save()
                if payment["response"]["status"] == "rejected":
                    msg = utils.rejected_error_msg(payment["response"]["status_detail"])
                    # if queue: queue.put(msg) # just for testing with threads
                    return msg
                # if queue: queue.put("Pagamento efetuado.") # just for testing with threads
            else:
                if "cause" in payment["response"] and payment["response"]["cause"] and "code" in payment["response"]["cause"][0]:
                    msg = utils.error_msg(payment["response"]["cause"][0]["code"])
                    # if queue: queue.put(msg) # just for testing with threads
                    return msg
                else:
                    msg = 'Aconteceu algum erro inesperado. Verifique os dados e tente novamente.'
                    # if queue: queue.put(msg) # just for testing with threads
                    return msg
            
        except OperationalError as error:
            return 'Infelizmente o produto já foi vendido e saiu de estoque.'
        except Exception as error:
            print(traceback.format_exc())
            return 'Ocorreu algum erro com o pagamento ou o produto saiu de estoque. Verifique e tente novamente'
        finally:
            # removing the products from the lock to others subsequents users
            # lock.acquire()
            self.clear_product_wait()
            # lock.release()
            

class UpdatePaymentForm(forms.Form):
    action = forms.CharField()
    data = forms.JSONField()

    def save(self):
        cd = self.cleaned_data
        mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        if cd["action"] == "payment.updated":
            mercado_pago_id = cd["data"]["id"]
            payment = Payment.objects.get(mercado_pago_id=mercado_pago_id)
            payment_mp = mp.payment().get(mercado_pago_id)

            payment.mercado_pago_status = payment_mp["response"]["status"]
            payment.mercado_pago_status_detail = payment_mp["response"]["status_detail"]

            # order payment update
            if payment_mp["response"]["status"] == "approved":
                payment.order.paid = True
                # TODO send email to user to notify the approved status
            else:
                payment.order.paid = False
                # TODO send email to user to notify the payment was rejected
            # print(payment, type(payment))
            # restoring stock quantity
            if payment_mp["response"]["status"] in ["refunded", "charged_back", "in_mediation", "pending", "authorized"]:
                order_items = payment.order.items.all()
                order_items.update(finished=True)
                for orderitem in order_items:
                    orderitem.save()
                    product = Item.objects.get(slug=orderitem.item.slug, pk=orderitem.item.pk)
                    product.quantity += orderitem.quantity
                    product.save()
            payment.order.save()
            payment.save()