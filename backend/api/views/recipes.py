from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOnly
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, RecipeCreateSerializer,
                             RecipeFavoriteSerializer)
from foodgram.settings import filename
from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                            ShoppingCart, Tag)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_in(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_in(ShoppingCart, request.user, pk)
        return self.delete_from(ShoppingCart, request.user, pk)

    def add_in(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeFavoriteSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = get_object_or_404(model, user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        shopping_cart_list = 'Список покупок:\n'
        for ingredient in ingredients:
            shopping_cart_list += (
                f' {ingredient["ingredient__name"]} - {ingredient["total"]}'
                f'({ingredient["ingredient__measurement_unit"]})\n')

        response = HttpResponse(shopping_cart_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
