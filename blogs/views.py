import logging
from django.core.files.storage import default_storage
import os
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from .models import Blog, BlogImage
from .serializers import BlogSerializer, BlogImageSerializer

logger = logging.getLogger(__name__)


class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = Blog.objects.filter(is_published=True)
        return queryset


class AdminBlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        try:
            logger.debug(f"Creating blog with data: {serializer.validated_data}")
            serializer.save()
        except Exception as e:
            logger.exception(f"Error creating blog: {str(e)}")
            raise

    def perform_update(self, serializer):
        try:
            logger.debug(f"Updating blog {self.get_object().id} with data: {serializer.validated_data}")
            serializer.save()
        except Exception as e:
            logger.exception(f"Error updating blog: {str(e)}")
            raise


class UploadBlogImageView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            logger.error(f"Blog {blog_id} not found")
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

        image_file = request.FILES.get("featured_image")
        if not image_file:
            logger.error("No image file provided")
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blog.featured_image = image_file
            blog.save()
            logger.info(f"Featured image uploaded for blog {blog_id}")
            
            serializer = BlogSerializer(blog, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error uploading image: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadBlogPDFView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            logger.error(f"Blog {blog_id} not found")
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

        pdf_file = request.FILES.get("pdf_file")
        if not pdf_file:
            logger.error("No PDF file provided")
            return Response({"error": "No PDF file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not pdf_file.content_type == "application/pdf":
            logger.error("Invalid file type")
            return Response({"error": "File must be a PDF"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blog.pdf_file = pdf_file
            
            pdf_thumbnail = request.FILES.get("pdf_thumbnail")
            if pdf_thumbnail:
                blog.pdf_thumbnail = pdf_thumbnail
            
            blog.save()
            logger.info(f"PDF uploaded for blog {blog_id}")
            
            serializer = BlogSerializer(blog, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error uploading PDF: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadBlogMultiImageView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            logger.error(f"Blog {blog_id} not found")
            return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

        image_file = request.FILES.get("image")
        alt_text = request.data.get("alt_text", "")
        ordering = request.data.get("ordering", 0)

        if not image_file:
            logger.error("No image file provided")
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            media_dir = os.path.join(str(settings.MEDIA_ROOT), 'blogs', 'images')
            os.makedirs(media_dir, exist_ok=True)

            orig_name = getattr(image_file, 'name', 'upload')
            storage_name = os.path.join('blogs', 'images', orig_name)
            storage_name = default_storage.get_available_name(storage_name)
            saved_name = default_storage.save(storage_name, image_file)

            blog_image = BlogImage.objects.create(
                blog=blog,
                image=saved_name,
                alt_text=alt_text,
                ordering=ordering
            )
            logger.info(f"Saved image to storage: {saved_name}")

            image_serializer = BlogImageSerializer(blog_image, context={"request": request})
            blog_serializer = BlogSerializer(blog, context={"request": request})
            return Response({
                "image": image_serializer.data,
                "blog": blog_serializer.data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Error uploading image: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteBlogImageView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, image_id):
        try:
            blog_image = BlogImage.objects.get(id=image_id)
        except BlogImage.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        if blog_image.image:
            try:
                blog_image.image.delete(save=False)
            except Exception:
                logger.exception("Failed to delete image file from storage")

        blog_image.delete()
        return Response({"message": "Image deleted"}, status=status.HTTP_204_NO_CONTENT)
