"""
Tests for the health check API.
"""
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckTests(APITestCase):
    """Test the health check API."""

    def test_health_check(self):
        """Test health check API."""
        url = reverse("health-check")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
