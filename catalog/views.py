import logging
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Product, Category, ProductImage, ProductDiscount
from .serializers import ProductSerializer, CategorySerializer, ProductImageSerializer

logger = logging.getLogger(__name__)


class ProductListView(generics.ListAPIView):
	serializer_class = ProductSerializer
	permission_classes = [permissions.AllowAny]

	def get_queryset(self):
		# select_related/prefetch_related to reduce DB queries during serialization
		queryset = Product.objects.filter(is_active=True).select_related('category', 'discount').prefetch_related('images')
		category_slug = self.request.query_params.get('category')
		if category_slug:
			queryset = queryset.filter(category__slug=category_slug)
		return queryset

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['request'] = self.request
		return context



class ProductDetailView(generics.RetrieveAPIView):
	# Include related objects to avoid extra queries during serialization
	queryset = Product.objects.filter(is_active=True).select_related('category', 'discount').prefetch_related('images')
	serializer_class = ProductSerializer
	permission_classes = [permissions.AllowAny]

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['request'] = self.request
		return context


class CategoryListView(generics.ListAPIView):
	serializer_class = CategorySerializer
	permission_classes = [permissions.AllowAny]
	
	def get_queryset(self):
		return Category.objects.filter(is_active=True, parent_category__isnull=True)


class CategoryProductsView(generics.ListAPIView):
	serializer_class = ProductSerializer
	permission_classes = [permissions.AllowAny]

	def get_queryset(self):
		slug = self.kwargs.get('slug')
		return Product.objects.filter(category__slug=slug, is_active=True)

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['request'] = self.request
		return context


class AdminProductViewSet(viewsets.ModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	permission_classes = [permissions.IsAdminUser]
	parser_classes = (JSONParser, MultiPartParser, FormParser)

	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['request'] = self.request
		return context

	def perform_create(self, serializer):
		try:
			logger.debug(f"Creating product with data: {serializer.validated_data}")
			product = serializer.save()
			# Handle optional discount fields sent by admin frontend
			discount_price = None
			original_price = None
			try:
				discount_price = self.request.data.get('discount_price', None)
			except Exception:
				discount_price = None
			try:
				original_price = self.request.data.get('original_price', None)
			except Exception:
				original_price = None
			if discount_price not in (None, '', 'null'):
				from decimal import Decimal
				dp = Decimal(str(discount_price))
				op = Decimal(str(original_price)) if original_price not in (None, '', 'null') else product.price
				# create or update ProductDiscount
				ProductDiscount.objects.update_or_create(
					product=product,
					defaults={
						'original_price': op,
						'discount_price': dp,
						'is_active': True,
					}
				)
		except Exception as e:
			logger.exception(f"Error creating product: {str(e)}")
			raise

	def perform_update(self, serializer):
		try:
			logger.debug(f"Updating product {self.get_object().id} with data: {serializer.validated_data}")
			# Capture current product instance for reference
			product_before = self.get_object()
			product = serializer.save()
			# Manage discount creation/update/deletion based on incoming data
			try:
				discount_price = self.request.data.get('discount_price', None)
			except Exception:
				discount_price = None
			try:
				original_price = self.request.data.get('original_price', None)
			except Exception:
				original_price = None
			from decimal import Decimal
			# If discount_price explicitly provided and non-empty -> create/update
			if discount_price not in (None, '', 'null'):
				try:
					dp = Decimal(str(discount_price))
					op = Decimal(str(original_price)) if original_price not in (None, '', 'null') else product.price
					ProductDiscount.objects.update_or_create(
						product=product,
						defaults={
							'original_price': op,
							'discount_price': dp,
							'is_active': True,
						}
					)
				except Exception:
					logger.exception("Failed to create/update ProductDiscount")
			# If discount_price is empty/null - remove any existing discount
			elif discount_price in (None, '', 'null'):
				try:
					ProductDiscount.objects.filter(product=product).delete()
				except Exception:
					logger.exception("Failed to remove ProductDiscount")
		except Exception as e:
			logger.exception(f"Error updating product: {str(e)}")
			raise


class AdminCategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [permissions.IsAdminUser]


class UploadProductImageView(APIView):
	permission_classes = [permissions.IsAdminUser]
	parser_classes = (MultiPartParser, FormParser)

	def post(self, request, product_id):
		"""Upload a product image. Optionally clear_old previous images.
		If the product has no main `image` set, set this uploaded image as the main image.
		Returns the created ProductImage with absolute URL (serializer context includes request).
		"""
		try:
			product = Product.objects.get(id=product_id)
		except Product.DoesNotExist:
			logger.error(f"Product {product_id} not found")
			return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

		image_file = request.FILES.get("image")
		color = request.data.get("color", "Default")
		alt_text = request.data.get("alt_text", "")
		clear_old = request.data.get("clear_old", "false").lower() == "true"

		logger.debug(f"Upload image request: product_id={product_id}, color={color}, clear_old={clear_old}, file={image_file}")

		# Log incoming files and data for debugging
		try:
			logger.debug(f"Request FILES keys: {list(request.FILES.keys())}")
			logger.debug(f"Request.data keys: {list(request.data.keys())}")
			if image_file:
				logger.debug(f"Incoming image file: name={getattr(image_file, 'name', None)} size={getattr(image_file, 'size', None)} content_type={getattr(image_file, 'content_type', None)}")
		except Exception:
			logger.exception("Failed to log request FILES/data")

		if not image_file:
			logger.error("No image file provided")
			return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

		try:
			if clear_old:
				old_images = ProductImage.objects.filter(product=product)
				logger.debug(f"Deleting {old_images.count()} old images")
				for old_img in old_images:
					if old_img.image:
						old_img.image.delete(save=False)
					old_img.delete()

			# Save file explicitly into storage to ensure it's written and to log the saved path
			# Ensure media subdirs exist
			media_dir = os.path.join(str(settings.MEDIA_ROOT), 'products', 'images')
			os.makedirs(media_dir, exist_ok=True)

			# Build a safe storage name and save
			orig_name = getattr(image_file, 'name', 'upload')
			storage_name = os.path.join('products', 'images', orig_name)
			storage_name = default_storage.get_available_name(storage_name)
			saved_name = default_storage.save(storage_name, image_file)

			# Create ProductImage and assign the saved path
			product_image = ProductImage.objects.create(
				product=product,
				image=saved_name,
				color=color,
				alt_text=alt_text
			)
			logger.info(f"Saved uploaded file to storage: {saved_name}")

			# If product doesn't have a main image set, set this uploaded image as the main image
			try:
				if not product.image:
					product.image = product_image.image
					product.save()
			except Exception:
				# Don't fail the request if updating product image fails; continue
				logger.exception("Failed to set product.image")

			# Return both the created ProductImage and the updated Product so the admin UI can refresh immediately
			image_serializer = ProductImageSerializer(product_image, context={"request": request})
			product_serializer = ProductSerializer(product, context={"request": request})
			return Response({
				"image": image_serializer.data,
				"product": product_serializer.data,
			}, status=status.HTTP_201_CREATED)
		except Exception as e:
			logger.exception(f"Error uploading image: {str(e)}")
			return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteProductImageView(APIView):
	permission_classes = [permissions.IsAdminUser]

	def delete(self, request, image_id):
		try:
			product_image = ProductImage.objects.get(id=image_id)
		except ProductImage.DoesNotExist:
			return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

		# Optionally clear product.image if it references this image
		try:
			product = product_image.product
		except Exception:
			product = None

		# Delete the image file and the model
		if product_image.image:
			try:
				product_image.image.delete(save=False)
			except Exception:
				logger.exception("Failed to delete image file from storage")

		product_image.delete()

		# If the product's main image pointed to this file, clear it
		if product and product.image and getattr(product.image, 'name', None) == getattr(product_image.image, 'name', None):
			product.image = None
			product.save()

		return Response({"message": "Image deleted"}, status=status.HTTP_204_NO_CONTENT)

