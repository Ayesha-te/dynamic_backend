from django.urls import path, include
from rest_framework import routers
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
    CategoryProductsView,
    AdminProductViewSet,
    AdminCategoryViewSet,
    UploadProductImageView,
    DeleteProductImageView,
)

app_name = "catalog"

router = routers.DefaultRouter()
router.register(r"admin/products", AdminProductViewSet, basename="admin-products")
router.register(r"admin/categories", AdminCategoryViewSet, basename="admin-categories")

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<slug:slug>/products/", CategoryProductsView.as_view(), name="category-products"),
    path("admin/products/<int:product_id>/upload-image/", UploadProductImageView.as_view(), name="upload-product-image"),
    path("admin/images/<int:image_id>/delete/", DeleteProductImageView.as_view(), name="delete-product-image"),
    path("", include(router.urls)),
]
