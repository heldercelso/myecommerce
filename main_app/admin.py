from django.contrib import admin
from main_app.models import Item, OrderItem, Order, Coupon, Refund, BillingAddress, UserProfile, Category
from mercadopago_payment.models import Payment
from django.urls import reverse
from django.utils.html import format_html
from django.utils.html import mark_safe

def accept_refund(modeladmin, request, queryset):
    user_order = queryset.get()
    user_refund = Refund.objects.filter(user_order=user_order)[0]
    user_refund.accepted=True
    user_refund.save()

    queryset.update(refund_requested=False, refund_accepted=True)
accept_refund.short_description = 'Accept selected refunds'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ref_code',
                    'id',
                    'finished',
                    'finished_date',
                    'paid',
                    'on_the_road',
                    'delivered',
                    'refund_requested',
                    'refund_accepted',
                    'billing_address',
                    'payment',
                    'coupon',
                    'start_date', 'list_products']

    def link_to_user(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', link, obj.user.username)
    link_to_user.short_description = 'Usuário'

    def link_to_id(self, obj):
        link = reverse("admin:main_app_order_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', link, obj.id)
    link_to_id.short_description = 'Pedido ID'

    def link_to_billing_address(self, obj):
        link = reverse("admin:main_app_billingaddress_change", args=[obj.billing_address.id])
        return format_html('<a href="{}">{}</a>', link, obj.billing_address)
    link_to_billing_address.short_description = 'Endereço'

    def link_to_payment(self, obj):
        link = reverse("admin:mercadopago_payment_payment_change", args=[obj.payment.id])
        return format_html('<a href="{}">{}</a>', link, obj.payment.mercado_pago_id)
    link_to_payment.short_description = 'Pagamento (M. Pago ID)'

    # def link_to_coupon(self, obj):
    #     if obj:
    #         link = reverse("admin:main_app_coupon_change", args=[obj.coupon.id])
    #         if link:
    #             return format_html('<a href="{}">{}</a>', link, obj.coupon.code)
    # link_to_coupon.short_description = 'Coupon'

    def list_products(self, obj):
        # each obj will be an Order obj/instance/row
        to_return = '<ul>'
        # I'm assuming that there is a name field under the event.Product model. If not change accordingly.
        to_return += '\n'.join('<li>{}</li>'.format(prod_name) for prod_name in obj.items.all())
        to_return += '</ul>'
        return mark_safe(to_return)
    list_products.short_description = 'Produtos'

    list_filter = ['finished',
                   'on_the_road',
                   'delivered',
                   'refund_requested',
                   'refund_accepted']
    search_fields = ['user__username', 'ref_code']
    actions = [accept_refund]

class RefundAdmin(admin.ModelAdmin):
    list_display = ['user_order',
                    'ref_code',
                    'reason',
                    'accepted',
                    'email']

    @admin.display(ordering='user_order__ref_code', description='Ref code')
    def ref_code(self, object):
        return object.user_order.ref_code

    def save_model(self, request, obj, form, change):
        user_order = Order.objects.get(ref_code=obj.user_order.ref_code)
        user_order.refund_accepted = obj.accepted
        user_order.save()
        super().save_model(request, obj, form, change)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'link_to_user',
                    # 'link_to_orderitem',
                    'link_to_order',
                    'item',
                    'quantity',
                    'finished']
    def link_to_user(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.user_order.user_id])
        return format_html('<a href="{}">{}</a>', link, obj.user_order.user.username)
    link_to_user.short_description = 'Usuário'

    def link_to_order(self, obj):
        link = reverse("admin:main_app_order_change", args=[obj.user_order.id])
        if obj.user_order.ref_code:
            return format_html('<a href="{}">{}</a>', link, str(obj.user_order.id) + " - " + str(obj.user_order.ref_code))
        else:
            return format_html('<a href="{}">{}</a>', link, str(obj.user_order.id))
    link_to_order.short_description = 'Pedido'

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund, RefundAdmin)
admin.site.register(UserProfile)

