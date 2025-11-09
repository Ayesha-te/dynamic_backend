from django.urls import path, include
from rest_framework import routers
from .views import (
    BlogViewSet,
    AdminBlogViewSet,
    UploadBlogImageView,
    UploadBlogPDFView,
    UploadBlogMultiImageView,
    DeleteBlogImageView,
)

app_name = "blogs"

router = routers.DefaultRouter()
router.register(r"", BlogViewSet, basename="blog")
router.register(r"admin/blogs", AdminBlogViewSet, basename="admin-blogs")

urlpatterns = [
    path("admin/blogs/<int:blog_id>/upload-image/", UploadBlogImageView.as_view(), name="upload-blog-image"),
    path("admin/blogs/<int:blog_id>/upload-pdf/", UploadBlogPDFView.as_view(), name="upload-blog-pdf"),
    path("admin/blogs/<int:blog_id>/upload-multi-image/", UploadBlogMultiImageView.as_view(), name="upload-blog-multi-image"),
    path("admin/images/<int:image_id>/delete/", DeleteBlogImageView.as_view(), name="delete-blog-image"),
    path("", include(router.urls)),
]
