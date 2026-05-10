"""
Test cases for API
"""

from django.test import TestCase
from rest_framework.test import APIClient
from .models import Hospital, Address, Doctor


class HospitalAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.address = Address(
            street='123 Main St',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001'
        )
        self.hospital = Hospital(
            name='Test Hospital',
            email='test@hospital.com',
            phone='+1234567890',
            address=self.address,
            license_number='LIC123',
            specialties=['Cardiology', 'Neurology']
        )
        self.hospital.save()

    def test_hospital_creation(self):
        """Test creating a new hospital"""
        self.assertEqual(self.hospital.name, 'Test Hospital')
        self.assertEqual(self.hospital.email, 'test@hospital.com')

    def test_hospital_list(self):
        """Test retrieving hospital list"""
        response = self.client.get('/api/hospitals/')
        self.assertEqual(response.status_code, 200)
