import base64

from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import Ingredient, RecipeIngredient, Recipe, Tag
from users.models import User, Subscription


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username',
                  'first_name', 'last_name',
                  'password'
                  )

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Пользователь с таким именем не может быть создан')
        return value


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return not user.is_anonymous and Subscription.objects.filter(
            user=user, author=obj).exists()


class SubscriptionSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate_subscribe(self, value):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise ValidationError('Вы уже подписаны',
                                  code=status.HTTP_400_BAD_REQUEST
                                  )
        if user == author:
            raise ValidationError('Невозможно подписаться на себя',
                                  code=status.HTTP_400_BAD_REQUEST
                                  )
        return value

    def get_recipes_count(self, value):
        return value.recipes.count()

    def get_recipes(self, value):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = value.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeFavoriteSerializer(recipes, many=True, read_only=True)
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time',
                  )

    def get_ingredients(self, value):
        recipe = value
        ingredient = []
        for ingredient in recipe.ingredients.all():
            ingredient.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit,
                'amount': ingredient.recipeingredient_set.get(recipe=recipe).amount
            })
        return ingredient

    def get_is_favorited(self, value):
        user = self.context.get('request').user
        return not user.is_anonymous and user.favorites_user.filter(
            recipe=value).exists()

    def get_is_in_shopping_cart(self, value):
        return self.context.get('request').user.is_authenticated \
               and self.context.get('request').user.shopping_user.filter(
            recipe=value).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'author', 'ingredients',
            'name', 'image',
            'text', 'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({'Поле не должно быть пустым'})

        ingredients_list = [get_object_or_404(Ingredient, id=item['id'])
                            for item in ingredients]
        if len(set(ingredients_list)) != len(ingredients_list):
            raise ValidationError({'Ингредиенты не должны повторяться'})

        if any(int(item['amount']) <= 0
               for item in ingredients):
            raise ValidationError({'Количество должно быть больше нуля'})
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'Должен быть выбран хотя бы один тег'})
        if len(tags) != len(set(tags)):
            raise ValidationError({'Теги не могут повторяться'})
        return value

    @transaction.atomic
    def ingredient_amounts(self, ingredients, recipe):
        ingredient_value = []
        for ingredient in ingredients:
            ingredient_value.append(
                RecipeIngredient(
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    recipe=recipe,
                    amount=ingredient['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_value)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredient_amounts(recipe=recipe,
                                ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.ingredient_amounts(recipe=instance,
                                ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance,
                                context=self.context).data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
