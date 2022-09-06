"""
Tests for the ingredients APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Create and return an ingredient detail url."""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user, **params):
    """Create and return a sample ingredient."""
    defaults = {
        "name": "Sample ingredient name",
    }
    defaults.update(params)
    ingredient = Ingredient.objects.create(user=user, **defaults)

    return ingredient


class PublicIngredientsAPITests(APITestCase):
    """Test unauthenticated API requests."""

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(APITestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        create_ingredient(user=self.user, name="Black beans")
        create_ingredient(user=self.user, name="Avocado")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_list_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        other_user = create_user(email="otheruser@example.com", password="testpass123")
        create_ingredient(user=other_user, name="Avocado")
        ingredient = create_ingredient(user=self.user, name="Yellow pepper")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        """Test updating ingredient."""
        ingredient = create_ingredient(user=self.user, name="Pepper")

        payload = {"name": "Vanilla"}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])
