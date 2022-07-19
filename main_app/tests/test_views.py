import pytest
from django.urls import resolve, reverse
from pytest_django.asserts import assertTemplateUsed

pytestmark = pytest.mark.django_db


@pytest.fixture # just to reuse the method
def home_response(client):
    return client.get(reverse("home-page"))

@pytest.fixture # just to reuse the method
def category_response(client, category):
    return client.get(reverse("home-page", kwargs={"slug": category.slug}))

@pytest.fixture # just to reuse the method
def search_response(client):
    return client.get(reverse("search-query"))

@pytest.fixture # just to reuse the method
def product_response(client, product):
    return client.get(reverse("product", kwargs={"slug": product.slug, "pk": product.id}))

@pytest.fixture # just to reuse the method
def cart_response(client):
    return client.get(reverse("mycart"))

@pytest.fixture # just to reuse the method
def refund_response(logged_client):
    return logged_client.get(reverse("refund-request"))


########################################################
##################### HOME TESTS #######################
########################################################


class TestHomePageView:
    def test_reverse_resolve(self):
        # main home
        assert reverse("home-page") == "/" #from view name to url
        assert resolve("/").view_name == "home-page" #from url to view name

        # category home
        assert reverse("home-page", kwargs={"slug": "test-slug"}) == "/category/test-slug/"
        assert resolve("/category/test-slug/").view_name == "home-page"

        # search home
        assert reverse("search-query") == "/search/"
        assert resolve("/search/").view_name == "search-query"

    def test_status_code(self, home_response, category_response, search_response):
        # main home
        assert home_response.status_code == 200

        # category home
        assert category_response.status_code == 200

        # search home
        assert search_response.status_code == 200

    def test_template(self, home_response, category_response, search_response):
        assertTemplateUsed(home_response, "home-page.html")
        assertTemplateUsed(category_response, "home-page.html")
        assertTemplateUsed(search_response, "home-page.html")


########################################################
#################### PROFILE TESTS #####################
########################################################


class TestProfileView:
    def test_reverse_resolve(self):
        # addresses profile
        assert reverse("profile-user-address", kwargs={"crud": "test-crud", "dest": "test-dest"}) == "/profile/address/test-crud/test-dest/"
        assert resolve("/profile/address/test-crud/test-dest/").view_name == "profile-user-address"
    
        url = reverse("profile-user-address", kwargs={"crud": "test-crud",
                                                       "address": "test-address",
                                                       "number": "test-number",
                                                       "zipcode": "test-zipcode",
                                                       "dest": "test-dest"})
        assert url == "/profile/address/test-crud/test-address/test-number/test-zipcode/test-dest/"
        assert resolve("/profile/address/test-crud/test-address/test-number/test-zipcode/test-dest/").view_name == "profile-user-address"

        # user-data profile
        assert reverse("profile-user-data") == "/profile/user-data/"
        assert resolve("/profile/user-data/").view_name == "profile-user-data"
    
        # user-orders profile
        assert reverse("profile-user-orders") == "/profile/user-orders/"
        assert resolve("/profile/user-orders/").view_name == "profile-user-orders"

    def test_status_code(self, logged_client):
        # addresses profile
        resp = logged_client.get(reverse("profile-user-address", kwargs={"crud": "test-crud", "dest": "test-dest"}))
        assert resp.status_code == 200
        resp = logged_client.get(reverse("profile-user-address", kwargs={"crud": "test-crud",
                                                       "address": "test-address",
                                                       "number": "test-number",
                                                       "zipcode": "test-zipcode",
                                                       "dest": "test-dest"}))
        assert resp.status_code == 200

        # user-data profile
        resp = logged_client.get(reverse("profile-user-data"))
        assert resp.status_code == 200

        # user-orders profile
        resp = logged_client.get(reverse("profile-user-orders"))
        assert resp.status_code == 200

    def test_template(self, logged_client):
        resp = logged_client.get(reverse("profile-user-address", kwargs={"crud": "test-crud", "dest": "test-dest"}))
        assertTemplateUsed(resp, "profile-user-address.html")
        resp = logged_client.get(reverse("profile-user-address", kwargs={"crud": "test-crud",
                                                       "address": "test-address",
                                                       "number": "test-number",
                                                       "zipcode": "test-zipcode",
                                                       "dest": "test-dest"}))
        assertTemplateUsed(resp, "profile-user-address.html")

        resp = logged_client.get(reverse("profile-user-data"))
        assertTemplateUsed(resp, "profile-user-data.html")

        resp = logged_client.get(reverse("profile-user-orders"))
        assertTemplateUsed(resp, "profile-user-orders.html")


########################################################
#################### PRODUCT TESTS #####################
########################################################


class TestProductView:
    def test_reverse_resolve(self):
        assert reverse("product", kwargs={"slug": "test-slug", "pk": "1"}) == "/product/test-slug/1/"
        assert resolve("/product/test-slug/1/").view_name == "product"

    def test_status_code(self, product_response):
        assert product_response.status_code == 200

    def test_template(self, product_response):
        assertTemplateUsed(product_response, "product.html")


#####################################################
#################### CART TESTS #####################
#####################################################


class TestCartView:
    def test_reverse_resolve(self):
        assert reverse("mycart") == "/mycart/"
        assert resolve("/mycart/").view_name == "mycart"

        assert reverse("add-item-to-cart", kwargs={"slug": "test-slug", "pk": "1", "dest": "test-dest"}) == "/cart-item/add/test-slug/1/test-dest/"
        assert resolve("/cart-item/add/test-slug/1/test-dest/").view_name == "add-item-to-cart"

        assert reverse("remove-item-from-cart", kwargs={"slug": "test-slug", "pk": "1", "dest": "test-dest"}) == "/cart-item/remove/test-slug/1/test-dest/"
        assert resolve("/cart-item/remove/test-slug/1/test-dest/").view_name == "remove-item-from-cart"

        assert reverse("delete-item-from-cart", kwargs={"slug": "test-slug", "pk": "1", "dest": "test-dest"}) == "/cart-item/delete/test-slug/1/test-dest/"
        assert resolve("/cart-item/delete/test-slug/1/test-dest/").view_name == "delete-item-from-cart"

    def test_status_code(self, cart_response, logged_client, product):
        assert cart_response.status_code == 200

        resp = logged_client.get(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "cart"}))
        assert resp.status_code == 302
        resp = logged_client.get(reverse("remove-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "cart"}))
        assert resp.status_code == 302
        resp = logged_client.get(reverse("delete-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "cart"}))
        assert resp.status_code == 302

    def test_template(self, cart_response, logged_client, product):
        assertTemplateUsed(cart_response, "cart.html")

        resp = logged_client.get(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "cart"}))
        assert resp['Location'] == reverse("mycart")

        resp = logged_client.get(reverse("remove-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "cart"}))
        assert resp['Location'] == reverse("mycart")

        resp = logged_client.get(reverse("delete-item-from-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "cart"}))
        assert resp['Location'] == reverse("mycart")


########################################################
##################### COUPON TESTS #####################
########################################################


class TestCouponView:
    def test_reverse_resolve(self):
        assert reverse("add-coupon") == "/coupon/add/"
        assert resolve("/coupon/add/").view_name == "add-coupon"

        assert reverse("remove-coupon", kwargs={"dest": "mycart"}) == "/coupon/remove/mycart/"
        assert resolve("/coupon/remove/mycart/").view_name == "remove-coupon"

    def test_status_code(self, logged_client):
        resp = logged_client.post(reverse("add-coupon"))
        assert resp.status_code == 302

        resp = logged_client.post(reverse("remove-coupon", kwargs={"dest": "checkout"}))
        assert resp.status_code == 302

    def test_template(self, logged_client):
        resp = logged_client.post(reverse("add-coupon"))
        assert resp['Location'] == reverse("checkout")

        resp = logged_client.post(reverse("remove-coupon", kwargs={"dest": "checkout"}))
        assert resp['Location'] == reverse("checkout")


########################################################
#################### CHECKOUT TESTS #####################
########################################################


class TestCheckoutView:
    def test_reverse_resolve(self):
        assert reverse("checkout") == "/checkout/"
        assert resolve("/checkout/").view_name == "checkout"

    def test_status_code(self, logged_client, product):
        logged_client.get(reverse("mycart"))
        logged_client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
        resp = logged_client.get(reverse("checkout"))
        assert resp.status_code == 200

    def test_template(self, logged_client, product):
        logged_client.get(reverse("mycart"))
        logged_client.post(reverse("add-item-to-cart", kwargs={"slug": product.slug, "pk": product.pk, "dest": "product"}))
        resp = logged_client.get(reverse("checkout"))
        assertTemplateUsed(resp, "checkout-page.html")


########################################################
#################### REFUND TESTS #####################
########################################################


class TestRefundView:
    def test_reverse_resolve(self):
        assert reverse("refund-request") == "/refund-request/"
        assert resolve("/refund-request/").view_name == "refund-request"

        assert reverse("refund-request", kwargs={"cod": "test-code"}) == "/refund-request/test-code/"
        assert resolve("/refund-request/test-code/").view_name == "refund-request"

    def test_status_code(self, refund_response):
        assert refund_response.status_code == 200

    def test_template(self, refund_response):
        assertTemplateUsed(refund_response, "refund-page.html")