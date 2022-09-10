"""
Tests for the ingredients APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from core.models import Ingredient, Recipe
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

    def test_delete_ingredient(self):
        """Test deleting an ingredient successful."""
        ingredient = create_ingredient(user=self.user)
        url = detail_url(ingredient.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes."""
        in1 = create_ingredient(user=self.user, name="Pepper")
        in2 = create_ingredient(user=self.user, name="Turkey")
        recipe = Recipe.objects.create(
            title="Pepper Crumble",
            time_minutes=5,
            price=Decimal("5.45"),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ing = create_ingredient(user=self.user, name="Pepper")
        create_ingredient(user=self.user, name="Turkey")
        recipe1 = Recipe.objects.create(
            title="Pepper Crumble",
            time_minutes=5,
            price=Decimal("5.45"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Turkey Crumble",
            time_minutes=50,
            price=Decimal("6.45"),
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
