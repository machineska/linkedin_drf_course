import os.path

from django.conf import settings
from django.urls import reverse_lazy, reverse

from rest_framework.test import APITestCase


from .models import Product


class ProductCreateTestCase(APITestCase):
    def setUp(self):
        self.initial_product_count = Product.objects.count()
        
    def test_create_product(self):
        product_attrs = {
            'name': 'New Product',
            'description': 'Awesome Product',
            'price': '123.45',
        }
        response = self.client.post(reverse_lazy('prod-new'), product_attrs)
        if response.status_code != 201:
            print(response.data)
        self.assertEqual(
            Product.objects.count(), self.initial_product_count + 1,
        )
        for attr, expected_value in product_attrs.items():
            self.assertEqual(response.data[attr], expected_value)
        self.initial_product_count += 1
        self.assertEqual(response.data['is_on_sale'], False)
        self.assertEqual(
            response.data['current_price'],
            float(product_attrs['price']),
        )
        
    
class ProductDeleteTestCase(APITestCase):
    def setUp(self):
        self.initial_product_count = Product.objects.count()
        
    def test_delete_product(self):
        initial_product_count = Product.objects.count()
        product_id = Product.objects.first().id
        kwargs = {
            'id': product_id, 
        }
        url = reverse('prod-update', kwargs=kwargs)
        self.client.delete(
            url, 
            # f'/api/v1/products/{product_id}'
        )
        self.assertEqual(
            Product.objects.count(), self.initial_product_count - 1
        )
        
        self.assertRaises(
            Product.DoesNotExist,
            Product.objects.get, id=product_id,
        )
        
        
class ProductListTestCase(APITestCase):
    def test_list_product(self):
        product_count = Product.objects.count()
        url = reverse('prod-list')
        response = self.client.get(url)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['count'], product_count)
        self.assertEqual(len(response.data['results']), product_count)


class ProductUpdateTestCase(APITestCase):
    def test_update_product(self):
        product = Product.objects.first()
        kwargs = {
            'id': product.id,
        }
        url = reverse('prod-update', kwargs=kwargs)
        context = {
            'name': 'New Product',
            'description': 'Awesome Product',
            'price': 123.45,            
        }
        response = self.client.patch(url, context, format='json',)
        updated = Product.objects.get(id=product.id)
        self.assertEqual(
            updated.name, context['name']
        )
        
    def test_upload_product_photo(self):
        product = Product.objects.first()
        original_photo = product.photo
        photo_path = os.path.join(
            settings.MEDIA_ROOT, 'products', 'vitamin-iron.jpg',
        )
        kwargs = {
            'id': product.id,
        }
        url = reverse('prod-update', kwargs=kwargs)
        context = {
            
        }
        
        with open(photo_path, 'rb') as photo_data:
            response = self.client.patch(
                url, {'photo': photo_data}, 
                format='multipart', 
            )
            
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['photo'], original_photo)
        
        try:
            updated = Product.objects.get(id=product.id)
            expected_photo = os.path.join(
                settings.MEDIA_ROOT, 'products', 'vitamin-iron',
            )
            self.assertTrue(
                updated.photo.path.startswith(expected_photo)
            )
        finally:
            os.remove(updated.photo.path)
        
