"""
Views for the recipe APIs.
"""
from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import (
    IngredientSerializer,
    RecipeDetailSerializer,
    RecipeSerializer,
    TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage recipe APIs."""

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == "list":
            return RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewset for recipe attributes."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Filter queryset to an authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-name")


class TagViewSet(BaseRecipeAttrViewSet):
    """View to manage Tag APIs."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """View to manage Ingredients APIs."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
