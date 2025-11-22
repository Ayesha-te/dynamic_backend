from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from catalog.models import Product, Category
import logging
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from django.utils import timezone


class AdminOrderViewSet(viewsets.ModelViewSet):
	"""Admin-only endpoints to list and retrieve orders and mark them paid via a custom action."""
	queryset = Order.objects.all().order_by("-created_at")
	serializer_class = OrderSerializer
	permission_classes = [IsAdminUser]

	def partial_update(self, request, *args, **kwargs):
		# allow admins to update status or is_paid
		order = self.get_object()
		data = request.data
		changed = False
		if "status" in data:
			order.status = data.get("status")
			changed = True
		if "is_paid" in data:
			is_paid = bool(data.get("is_paid"))
			order.is_paid = is_paid
			if is_paid and not order.paid_at:
				order.paid_at = timezone.now()
			if not is_paid:
				order.paid_at = None
			changed = True
		if changed:
			order.save()
		return Response(OrderSerializer(order).data)


class UserCartView(generics.RetrieveAPIView):
	serializer_class = CartSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
		return cart


class AddToCartView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		product_id = request.data.get("product_id")
		quantity = int(request.data.get("quantity", 1))
		color = request.data.get("color", "Default")
		product = get_object_or_404(Product, pk=product_id, is_active=True)
		cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
		item, created = CartItem.objects.get_or_create(cart=cart, product=product, color=color)
		if not created:
			item.quantity = item.quantity + quantity
		else:
			item.quantity = quantity
		item.save()
		return Response(CartSerializer(cart).data)


class RemoveFromCartView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		item_id = request.data.get("item_id")
		cart = get_object_or_404(Cart, user=request.user, is_active=True)
		item = get_object_or_404(CartItem, pk=item_id, cart=cart)
		item.delete()
		return Response(CartSerializer(cart).data)


class CheckoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		cart = get_object_or_404(Cart, user=request.user, is_active=True)
		
		shipping_data = request.data.get("shipping", {})
		items_data = request.data.get("items", [])
		
		total = 0
		for it in cart.items.all():
			total += float(it.product.price) * it.quantity
		
		phone = shipping_data.get("phone", "")
		address = shipping_data.get("address", "") or request.user.email
		city = shipping_data.get("city", "")
		postal = shipping_data.get("postal", "")
		
		order = Order.objects.create(
			user=request.user,
			cart=cart,
			total_amount=total,
			phone=phone,
			address=address,
			city=city,
			postal_code=postal
		)
		
		color_map = {item["id"]: item.get("color", "Default") for item in items_data}
		
		for it in cart.items.all():
			color = color_map.get(it.id, "Default")
			order.items.create(
				product=it.product,
				quantity=it.quantity,
				price=it.product.price,
				color=color
			)
		
		cart.is_active = False
		cart.save()
		return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class AdminStatsView(APIView):
	"""Return small, fast summary stats for the admin dashboard.
	Provides counts and small recent lists so the admin dashboard can render quickly.
	"""
	permission_classes = [IsAdminUser]

	def get(self, request):
		try:
			product_count = Product.objects.count()
			category_count = Category.objects.count()
			order_count = Order.objects.count()

			recent_orders_qs = Order.objects.select_related('user').order_by('-created_at')[:4]
			recent_orders = [
				{
					'id': o.id,
					'user': {
						'id': getattr(o.user, 'id', None),
						'username': getattr(o.user, 'username', ''),
						'email': getattr(o.user, 'email', ''),
					},
					'total_amount': str(o.total_amount),
					'is_paid': o.is_paid,
					'paid_at': o.paid_at.isoformat() if o.paid_at else None,
					'created_at': o.created_at.isoformat() if o.created_at else None,
				}
				for o in recent_orders_qs
			]

			low_stock_qs = Product.objects.filter(stock__lt=10).order_by('stock')[:4]
			low_stock = [
				{
					'id': p.id,
					'name': p.name,
					'sku': p.sku,
					'stock': p.stock,
				}
				for p in low_stock_qs
			]

			return Response({
				'product_count': product_count,
				'category_count': category_count,
				'order_count': order_count,
				'recent_orders': recent_orders,
				'low_stock': low_stock,
			})
		except Exception as e:
			logger = logging.getLogger(__name__)
			logger.exception("Failed to build admin stats: %s", e)
			return Response({'error': 'Failed to build admin stats'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

