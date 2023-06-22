from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from api.fields import Base64ImageField
from recipes.models import Ingredient, RecipeIngredient, Recipe, Tag
from users.models import User, Subscription


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
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, value):
        return (
                self.context.get('request').user.is_authenticated
                and Subscription.objects.filter(user=self.context['request'].user,
                                                author=value).exists()
        )

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


class RecipeIngredientListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientListSerializer(many=True,
                                                 read_only=True,
                                                 source='recipes')
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

    def get_is_favorited(self, value):
        user = self.context.get('request').user
        return not user.is_anonymous and user.favorites_user.filter(
            recipe=value).exists()

    def get_is_in_shopping_cart(self, value):
        return (self.context.get('request').user.is_authenticated
                and self.context.get('request').user.shopping_user.filter(
                    recipe=value).exists())


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
        if not value:
            raise ValidationError({'Поле не должно быть пустым'})

        ingredients_list = [get_object_or_404(Ingredient, id=item['id'])
                            for item in value]
        if len(set(ingredients_list)) != len(ingredients_list):
            raise ValidationError({'Ингредиенты не должны повторяться'})

        if any(int(item['amount']) <= 0
               for item in value):
            raise ValidationError({'Количество должно быть больше нуля'})
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError({'Должен быть выбран хотя бы один тег'})
        if len(value) != len(set(value)):
            raise ValidationError({'Теги не могут повторяться'})
        return value

    @transaction.atomic
    def ingredient_amounts(self, ingredients, recipe):
        ingredient_value = []
        for ingredient in ingredients:
            ingredient_value.append(
                RecipeIngredient(
                    ingredient_id=ingredient['id'],
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
