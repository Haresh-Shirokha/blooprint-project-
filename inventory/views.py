from django.shortcuts import render
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from .models import InventoryItem
from .serializers import UserSerializer, InventoryItemSerializer

# Create your views here.
logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User {user.username} created.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        item_id = kwargs['pk']
        cached_item = cache.get(f'inventory_item_{item_id}')
        if cached_item:
            logger.info(f"Fetched item {item_id} from cache.")
            return Response(cached_item)

        try:
            item = self.get_object()
            cache.set(f'inventory_item_{item_id}', self.get_serializer(item).data)
            logger.info(f"Fetched item {item_id} from database and cached it.")
            return Response(self.get_serializer(item).data)
        except InventoryItem.DoesNotExist:
            logger.error(f"Item {item_id} not found.")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"Item created: {serializer.data['name']}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            serializer = self.get_serializer(item, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f"Item updated: {serializer.data['name']}")
            return Response(serializer.data)
        except InventoryItem.DoesNotExist:
            logger.error(f"Item {kwargs['pk']} not found.")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            item.delete()
            logger.info(f"Item deleted: {kwargs['pk']}")
            return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except InventoryItem.DoesNotExist:
            logger.error(f"Item {kwargs['pk']} not found.")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)