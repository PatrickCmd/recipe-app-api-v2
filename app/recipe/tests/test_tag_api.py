"""
Tests for the tags APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, **params):
    """Create and return a sample tag."""
    defaults = {
        "name": "Sample tag name",
    }
    defaults.update(params)
    tag = Tag.objects.create(user=user, **defaults)

    return tag


class PublicTagsAPITests(APITestCase):
    """Test unauthenticated API requests."""

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(APITestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        create_tag(user=self.user, name="Vegan")
        create_tag(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_list_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        other_user = create_user(email="otheruser@example.com", password="testpass123")
        create_tag(user=other_user, name="Fruity")
        tag = create_tag(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating tag."""
        tag = create_tag(user=self.user, name="After dinner")

        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag successful."""
        tag = create_tag(user=self.user)
        url = detail_url(tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags by those assigned to recipes."""
        tag1 = create_tag(user=self.user, name="Vegan")
        tag2 = create_tag(user=self.user, name="Vegetarian")
        recipe = Recipe.objects.create(
            title="Vegan Crumble",
            time_minutes=5,
            price=Decimal("5.45"),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = create_tag(user=self.user, name="Vegan")
        create_tag(user=self.user, name="Vegetarian")
        recipe1 = Recipe.objects.create(
            title="Vegan Crumble",
            time_minutes=5,
            price=Decimal("5.45"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Vegetarian Crumble",
            time_minutes=50,
            price=Decimal("6.45"),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
