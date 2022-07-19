import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView

from main_app.models import Order

from .forms import PaymentForm, UpdatePaymentForm
from .models import Payment

class PaymentView(CreateView):
    """ Checkout page template view """
    model = Payment
    form_class = PaymentForm

    @cached_property
    def order(self):
        order_id = self.request.session.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        return order

    def get(self, *args, **kwargs):
        get_http = super().get(*args, **kwargs)
        # If the user type the url directly without passing through checkout it returns to checkout
        # it was necessary to assurance checkout verification like max limit of transaction
        if not self.request.META.get('HTTP_REFERER'):
            return redirect('checkout')
        return get_http

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.order
        context["publishable_key"] = settings.MERCADO_PAGO_PUBLIC_KEY
        context["language_code"] = settings.LANGUAGE_CODE
        return context

    # It is called by process-payment.js, where mercadopago v2 is implemented
    def post(self, *args, **kwargs):
        form_dict = json.loads(self.request.body)
        form = PaymentForm(data=form_dict, order=self.order)

        if form.is_valid():
            error_msg = form.save()
            if error_msg:
                error = {"Erro": [{"message": error_msg}]}
                return JsonResponse({"errors": error}, safe=False)

            redirect_url = "payments:failure"
            status = form.instance.mercado_pago_status

            if status == "approved":
                redirect_url = "payments:success"
            if status == "in_process":
                redirect_url = "payments:pending"

            if status and status != "rejected":
                del self.request.session["order_id"]
            # return redirect(reverse(redirect_url))

            return JsonResponse({"redirect_url": reverse(redirect_url)},
                                #  "errors": json.loads(form.errors.as_json())},
                                  safe=False)
        else:
            # labels = {f.name: f.verbose_name for f in Payment._meta.get_fields()}
            labels = {'doc_number': 'CPF', 'card_holder': 'Titular', 'email': 'E-mail'}
            for k in tuple(form.errors.keys()):
                form.errors[labels[k]] = form.errors.pop(k)
            return JsonResponse({"redirect_url": reverse('payments:process'),
                                 "errors": json.loads(form.errors.as_json())},
                                  safe=False)

class PaymentFailureView(TemplateView):
    template_name = "mercadopago_payment/failure.html"


class PaymentPendingView(TemplateView):
    template_name = "mercadopago_payment/pending.html"


class PaymentSuccessView(TemplateView):
    template_name = "mercadopago_payment/success.html"

# Using postman
# {"action": "payment.updated",
# "data": {"id": "1246831283"}}

@require_POST # accept only post
@csrf_exempt # it is defining csrf is not necessary (the post will be called externally of the application)
# for this to work will be necessary to configure mercadopago webhook on its platform (or you can simulate using postman):
# https://www.mercadopago.com.br/developers/panel/notifications
def payment_webhook(request):
    data = json.loads(request.body)
    form = UpdatePaymentForm(data)
    if form.is_valid():
        form.save()

    return HttpResponse(status=200)