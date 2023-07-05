import pandas as pd
import matplotlib.pyplot as plt
import json
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import datetime
from io import StringIO
from django.core.paginator import Paginator
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .models import Product, Price
from .views import *


# ======================= TESTS FOR MODELS =======================
class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_product_creation(self):
        product = Product.objects.create(
            id=1,
            owner=self.user,
            name='Test Product',
            description='Test description',
            minutes_refresh_rate=60,
            target_price=100.0
        )
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(product.id, 1)
        self.assertEqual(product.owner, self.user)
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.description, 'Test description')
        self.assertEqual(product.minutes_refresh_rate, 60)
        self.assertEqual(product.target_price, 100.0)
        self.assertTrue(product.date_added)

    def test_product_ordering(self):
        product1 = Product.objects.create(
            id=1,
            owner=self.user,
            name='Product 1',
            date_added=timezone.now() - timezone.timedelta(days=1),
            target_price=100.0
        )
        product2 = Product.objects.create(
            id=2,
            owner=self.user,
            name='Product 2',
            date_added=timezone.now(),
            target_price=100.0
        )
        product3 = Product.objects.create(
            id=3,
            owner=self.user,
            name='Product 3',
            date_added=timezone.now() - timezone.timedelta(days=2),
            target_price=100.0
        )
        products = Product.objects.all()
        self.assertEqual(products[0], product2)
        self.assertEqual(products[1], product1)
        self.assertEqual(products[2], product3)

    def test_unique_id_constraint(self):
        Product.objects.create(
            id=1,
            owner=self.user,
            name='Product 1',
            target_price=100.0
        )
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                id=1,
                owner=self.user,
                name='Product 2',
                target_price=200.0
            )


class PriceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.product = Product.objects.create(
            id=1,
            owner=self.user,
            name='Test Product',
            target_price=100.0
        )

    def test_price_creation(self):
        price = Price.objects.create(
            product=self.product,
            price=99.99,
            currency='USD'
        )
        self.assertEqual(Price.objects.count(), 1)
        self.assertEqual(price.product, self.product)
        self.assertEqual(price.price, 99.99)
        self.assertEqual(price.currency, 'USD')
        self.assertTrue(price.date)

    def test_price_str_representation(self):
        price = Price.objects.create(
            product=self.product,
            price=99.99,
            currency='USD'
        )
        expected_str = '1 - Test Product - 99.99 USD'
        self.assertEqual(str(price), expected_str)

    def test_price_date_auto_now_add(self):
        price = Price.objects.create(
            product=self.product,
            price=99.99,
            currency='USD'
        )
        now = timezone.now()
        self.assertAlmostEqual(price.date, now, delta=timezone.timedelta(seconds=1))


# ======================= TESTS FOR VIEWS =======================
class AddProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_add_product_view_get(self):
        url = reverse('add_product')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AllegroTracker/add_product.html')

    def test_add_product_view_post_invalid_target_price(self):
        url = reverse('add_product')
        data = {
            'name': 'Test Product',
            'id': '12345',
            'minutes_refresh_rate': '60',
            'description': 'Test description',
            'target_price': '-100.0'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AllegroTracker/add_product.html')
        self.assertContains(response, 'Target price cannot be negative')
        self.assertEqual(Product.objects.count(), 0)


class EditProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_edit_product_view_get(self):
        product = Product.objects.create(name='Test Product', id='12345', owner=self.user, target_price=100.0)
        url = reverse('edit_product', args=[product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AllegroTracker/edit_product.html')
        self.assertEqual(response.context['product'], Product.objects.filter(id=product.id).first())


class DeleteProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_delete_product_view(self):
        product = Product.objects.create(
            id=1,
            owner=self.user,
            name='Test Product',
            target_price=100.0
        )
        url = reverse('delete_product', args=[product.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Product.objects.count(), 0)


class ReturnGraphTest(unittest.TestCase):
    def test_return_graph_with_prices(self):
        prices = [
            Price(date=datetime(2023, 4, 1), price=10.0),
            Price(date=datetime(2023, 4, 2), price=12.0),
            Price(date=datetime(2023, 4, 3), price=8.0)
        ]
        data = return_graph(prices)
        self.assertIsInstance(data, str)

    def test_return_graph_with_exception(self):
        prices = None
        data = return_graph(prices)
        self.assertEqual(data, 'No data to display')


class SearchProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_search_product_view(self):
        product1 = Product.objects.create(
            name='Product One',
            owner=self.user,
            target_price=100.0
        )
        product2 = Product.objects.create(
            name='Product Two',
            owner=self.user,
            target_price=100.0
        )
        product3 = Product.objects.create(
            name='Another Product',
            owner=self.user,
            target_price=100.0
        )

        url = reverse('search_product')
        search_string = 'product'
        data = {'search_string': search_string}
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(response_data, list)

        unexpected_products = [product3]
        for unexpected_product in unexpected_products:
            self.assertNotIn({'name': unexpected_product.name, 'owner_id': unexpected_product.owner.id}, response_data)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_view_get(self):
        url = reverse('register')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_view_post_invalid_data(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'invalidemail',
            'password': 'short'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertContains(response, 'Please enter a valid email')
        self.assertContains(response, 'Password must be at least 8 characters long')
        self.assertFalse(User.objects.filter(username='testuser', email='invalidemail').exists())


class VerificationViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_verification_view_get(self):
        user = User.objects.create(username='testuser', email='test@example.com')
        token = 'testtoken'
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('activate', args=[uidb64, token])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_verification_view_get_exception(self):
        url = reverse('activate', args=['invaliduidb64', 'invalidtoken'])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))


# ======================= TESTS FOR FORMS =======================
class RegisterFormTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_form_valid_submission(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

    def test_register_form_invalid_submission(self):
        url = reverse('register')

        # Submit an invalid form with missing required fields
        response = self.client.post(url, {
            'username': '',
            'email': '',
            'password': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username should only contain letters and numbers')
        self.assertContains(response, 'Please enter a valid email')
        self.assertContains(response, 'Password must be at least 8 characters long')


class LoginFormTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_form_valid_submission(self):
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.assertEqual(response.status_code, 200)

    def test_login_form_invalid_submission(self):
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'invaliduser',
            'password': 'invalidpassword'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your username and password didn\'t match. Please try again.')


class EditProductFormTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_edit_product_form_valid_submission(self):
        product_id = 1
        url = reverse('edit_product', args=[product_id])

        # Submit a valid form
        response = self.client.post(url, {
            'id': '123',
            'name': 'Test Product',
            'description': 'Test Description',
            'refresh_rate': 5,
            'target_price': 9.99
        })

        self.assertEqual(response.status_code, 302)

    def test_edit_product_form_invalid_submission(self):
        product_id = 1
        url = reverse('edit_product', args=[product_id])

        response = self.client.post(url, {
            'id': '123',
            'name': '',
            'refresh_rate': 5,
            'target_price': 9.99
        })

        self.assertEqual(response.status_code, 302)


class AddProductFormTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_add_product_form_valid_submission(self):
        url = reverse('add_product')

        response = self.client.post(url, {
            'id': '123',
            'name': 'Test Product',
            'description': 'Test Description',
            'refresh_rate': 5,
            'target_price': 9.99
        })

        self.assertEqual(response.status_code, 302)

    def test_add_product_form_invalid_submission(self):
        url = reverse('add_product')
        response = self.client.post(url, {
            'id': '123',
            'name': '',
            'refresh_rate': 5,
            'target_price': 9.99
        })

        self.assertEqual(response.status_code, 302)
