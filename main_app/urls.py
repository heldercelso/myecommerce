from django.urls import include, path
from .views import CartSummaryView, HomeView, ItemDetailView, CheckoutView, ProfileView, AddressView, OrderView, \
                AddCouponView, RemoveCouponView, RefundView, \
                add_item_to_cart, remove_item_from_cart, delete_item_from_cart

urlpatterns = [
    # Home page
    path('', HomeView.as_view(), name='home-page'),
    path('category/<slug>/', HomeView.as_view(), name='home-page'),
    path('search/', HomeView.as_view(), name='search-query'),

    # Profile
    path('profile/address/<crud>/<dest>/', AddressView.as_view(), name='profile-user-address'),
    path('profile/address/<crud>/<address>/<number>/<zipcode>/<dest>/', AddressView.as_view(), name='profile-user-address'),
    path('profile/user-data/', ProfileView.as_view(), name='profile-user-data'),
    path('profile/user-orders/', OrderView.as_view(), name='profile-user-orders'),

    # Product
    path('product/<slug>/<pk>/', ItemDetailView.as_view(), name='product'),

    # Cart
    path('mycart/', CartSummaryView.as_view(), name='mycart'),
    path('cart-item/add/<slug>/<pk>/<dest>/', add_item_to_cart, name='add-item-to-cart'),
    path('cart-item/remove/<slug>/<pk>/<dest>/', remove_item_from_cart, name='remove-item-from-cart'),
    path('cart-item/delete/<slug>/<pk>/<dest>/', delete_item_from_cart, name='delete-item-from-cart'),

    # Coupon
    path('coupon/add/', AddCouponView.as_view(), name='add-coupon'),
    path('coupon/remove/<dest>/', RemoveCouponView.as_view(), name='remove-coupon'),

    # Order summary
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # Payment
    path('payments/', include('mercadopago_payment.urls', namespace='payments')),

    # Refund
    path('refund-request/', RefundView.as_view(), name='refund-request'),
    path('refund-request/<cod>/', RefundView.as_view(), name='refund-request'),    
]
