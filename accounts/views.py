from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import logging

from .serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
	queryset = get_user_model().objects.all()
	permission_classes = [permissions.AllowAny]
	serializer_class = RegisterSerializer

	def create(self, request, *args, **kwargs):
		# Log incoming data for debugging (remove or lower level in production)
		logger.debug("Register request.data: %s", request.data)
		serializer = self.get_serializer(data=request.data)
		if not serializer.is_valid():
			logger.debug("Register serializer.errors: %s", serializer.errors)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MeView(generics.RetrieveAPIView):
	serializer_class = UserSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		return self.request.user
