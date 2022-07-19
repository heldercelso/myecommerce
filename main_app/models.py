
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import post_save
from localflavor.br.models import BRCPFField, BRPostalCodeField, BRStateField
from django.dispatch import receiver
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from django.utils.text import slugify

LABEL_OPTIONS = (
    ('N', 'Novo'),
    ('D', 'Em Destaque'),
    ('P', 'Promoção'),
)

class UserProfile(models.Model):
    class Meta:
        verbose_name="Perfi"
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    cpf = BRCPFField("CPF")
    full_name = models.CharField("Nome Completo", max_length=200)
    cell_number = models.CharField("Celular", max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username
    def add_email_address(self, request, new_email):
        # Add a new email address for the user, and send email confirmation.
        # Old email will remain the primary until the new one is confirmed.
        return EmailAddress.objects.add_email(request, self.user, new_email, confirm=True)

@receiver(email_confirmed)
def update_user_email(sender, request, email_address, **kwargs):
    # Get rid of old email addresses
    # email_address is an instance of allauth.account.models.EmailAddress
    EmailAddress.objects.filter(user=email_address.user).exclude(primary=True).delete()
    # Once the email address is confirmed, make new email_address primary.
    # This also sets user.email to the new email address.
    email_address.set_as_primary()


class Category(models.Model):
    class Meta:
        verbose_name="Categoria"
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True, max_length=255)
    # slug = models.SlugField()

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(self.id)
            self.save()
    def __str__(self):
        return self.title


class Item(models.Model):
    class Meta:
        verbose_name="Produto"
        ordering = ['id']
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True) # discount is not mandatory
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    label = models.CharField(choices=LABEL_OPTIONS, max_length=1, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    slug = models.SlugField(unique=True, max_length=255)
    image = models.ImageField()

    def __str__(self):
        return self.title
    def get_url(self):
        return reverse("product", kwargs={'slug': self.slug, 'pk': self.id})
    def get_add_item_to_cart_url(self):
        return reverse("add-item-to-cart", kwargs={'slug': self.slug, 'pk': self.id, 'dest': 'product'})
    def get_remove_item_from_cart_url(self):
        return reverse("remove-item-from-cart", kwargs={'slug': self.slug, 'pk': self.id, 'dest': 'product'})
    def get_delete_item_from_cart_url(self):
        return reverse("delete-item-from-cart", kwargs={'slug': self.slug, 'pk': self.id, 'dest': 'product'})

class OrderItem(models.Model):
    class Meta:
        verbose_name="ItemsCarrinho"
    user_order = models.ForeignKey('Order', on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE) # if the item was deleted, the orderitem will be removed also.
    quantity = models.IntegerField(default=1)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, # user currently logged in django
    #                          on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} de {self.item.title}"
    def get_total_price(self):
        return self.quantity * self.item.price
    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price
    def get_discount_amount(self):
        return self.get_total_price() - self.get_total_discount_price()

class Order(models.Model):
    class Meta:
        verbose_name="Pedido"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, # user currently logged in django
                             on_delete=models.CASCADE,
                             verbose_name="Cliente")
    start_date = models.DateTimeField("Iniciado em:", auto_now_add=True)
    finished = models.BooleanField("Finalizado", default=False) # this field can be replaced, if date is not set it means the it is not finished
    finished_date = models.DateTimeField("Finalizado em:", blank=True, null=True)
    items = models.ManyToManyField('OrderItem')
    billing_address = models.ForeignKey('BillingAddress', verbose_name="Endereço",
                                        on_delete=models.CASCADE,
                                        blank=True, null=True)
    paid = models.BooleanField("Pago", default=False)
    payment = models.ForeignKey('mercadopago_payment.Payment', verbose_name="Pagamento", related_name="mercadopago",
                                on_delete=models.CASCADE,
                                blank=True, null=True)
    coupon = models.ForeignKey('Coupon', verbose_name="Cupom",
                                on_delete=models.CASCADE,
                                blank=True, null=True)
    on_the_road = models.BooleanField("Na estrada", default=False)
    delivered = models.BooleanField("Entregue", default=False)
    refund_requested = models.BooleanField("Desistencia Solicitada", default=False)
    refund_accepted = models.BooleanField("Desistencia Aceita", default=False)
    # ref_code = models.CharField(max_length=32, blank=True, null=True)
    ref_code = models.UUIDField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    def get_total_price(self):
        result = 0
        for order_item in self.items.all():
            if order_item.item.discount_price:
                result += order_item.get_total_discount_price()
            else:
                result += order_item.get_total_price()
        return result
    def get_total(self):
        result = self.get_total_price()
        if self.coupon:
            result -= self.coupon.amount
        return result
    def get_total_items(self):
        result = 0
        for order_item in self.items.all():
            result += order_item.quantity
        return result
    def get_description(self):
        return ", ".join(
            [f"{order_item.quantity} x {order_item.item.title}" for order_item in self.items.all()]
        )

class BillingAddress(models.Model):
    class Meta:
        verbose_name="Endereço"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, # user currently logged in django
                             on_delete=models.CASCADE)
    address = models.CharField(max_length=250)
    number = models.IntegerField()
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    district = models.CharField(max_length=250)
    # state = BRStateField()
    zipcode = BRPostalCodeField()
    complement = models.CharField(max_length=250, blank=True)
    is_active = models.BooleanField(default=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address}, {self.number} - {self.city}, {self.state}"


class Coupon(models.Model):
    class Meta:
        verbose_name="Cupom"
    code = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Refund(models.Model):
    class Meta:
        verbose_name="Desistência"
    user_order = models.ForeignKey('Order',
                                    on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return str(self.pk)

def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        # userprofile = UserProfile.objects.create(user=instance, email=instance.email)
        userprofile = UserProfile.objects.create(user=instance)

post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)