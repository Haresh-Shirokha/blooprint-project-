from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import InventoryItem
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# Create your tests here.

class InventoryTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)  # This gives you the access token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_item(self):
        url = reverse('inventoryitem-list')
        data = {'name': 'Item 1', 'description': 'Test item', 'quantity': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_read_item(self):
        item = InventoryItem.objects.create(name='Item 2', description='Test item 2', quantity=5)
        url = reverse('inventoryitem-detail', args=[item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item(self):
        item = InventoryItem.objects.create(name='Item 3', description='Test item 3', quantity=20)
        url = reverse('inventoryitem-detail', args=[item.id])
        data = {'name': 'Updated Item 3'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_item(self):
        item = InventoryItem.objects.create(name='Item 4', description='Test item 4', quantity=15)
        url = reverse('inventoryitem-detail', args=[item.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
