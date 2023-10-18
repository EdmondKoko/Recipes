from django.contrib import admin
from django.contrib.admin import display

from .models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                     ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
  """Для модели Recipe создана кастомная админка."""
    list_display = ('name', 'id', 'author', 'add_in_favorite')
    readonly_fields = ('add_in_favorite',)
    list_filter = ('name', 'author', 'tags',)

    @display(description='Количество в избранном')
    def add_in_favorite(self, value):
        return value.favorites_recipe.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
  """Для модели Ingredient создана кастомная админка."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
  """Для модели Tag создана кастомная админка."""
    list_display = ('name', 'color', 'slug',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
  """Для модели ShopingCart создана кастомная админка."""
    list_display = ('user', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
  """Для модели Favorite создана кастомная админка."""
    list_display = ('user', 'recipe',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
  """Для модели RecipeIngredient создана кастомная админка."""
    list_display = ('recipe', 'ingredient', 'amount',)
