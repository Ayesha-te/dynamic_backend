import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import Newsletter
from .serializers import NewsletterSerializer, NewsletterSubscribeSerializer

logger = logging.getLogger(__name__)


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get_permissions(self):
        if self.action == 'subscribe':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminUser()]
        return [IsAdminUser()]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def subscribe(self, request):
        try:
            serializer = NewsletterSubscribeSerializer(data=request.data)
            if serializer.is_valid():
                newsletter = serializer.save()
                return Response(
                    {'message': 'Successfully subscribed', 'email': newsletter.email},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Newsletter subscription error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to process subscription', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def unsubscribe(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            newsletter = Newsletter.objects.get(email=email)
            newsletter.is_active = False
            newsletter.save()
            return Response({'message': 'Successfully unsubscribed'}, status=status.HTTP_200_OK)
        except Newsletter.DoesNotExist:
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Newsletter unsubscribe error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to process unsubscription', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def active_subscribers(self, request):
        try:
            subscribers = Newsletter.objects.filter(is_active=True)
            serializer = self.get_serializer(subscribers, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch active subscribers: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch subscribers', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
