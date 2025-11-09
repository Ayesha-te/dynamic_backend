from django.urls import path, include
from rest_framework import routers
from .views import UserCartView, AddToCartView, RemoveFromCartView, CheckoutView, AdminOrderViewSet

app_name = "orders"

router = routers.DefaultRouter()
router.register(r"admin/orders", AdminOrderViewSet, basename="admin-orders")

urlpatterns = [
    path("cart/", UserCartView.as_view(), name="user-cart"),
    path("cart/add/", AddToCartView.as_view(), name="cart-add"),
    path("cart/remove/", RemoveFromCartView.as_view(), name="cart-remove"),
    path("orders/checkout/", CheckoutView.as_view(), name="checkout"),
    path("", include(router.urls)),
]
