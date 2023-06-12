from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=200)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(verbose_name='Название',
                            unique=True, max_length=200)
    color = models.CharField(verbose_name='Цветовой HEX-код',
                             unique=True,
                             max_length=7,
                             validators=[RegexValidator(
                                 regex='^#([a-fA-F0-9]{6})',
                                 message='Цвет не в формате HEX')]
                             )
    slug = models.SlugField(verbose_name='Уникальный слаг',
                            unique=True, max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=200)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
        related_name='recipes',
    )
    text = models.TextField(verbose_name='Описание')

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в мин.',
        validators=[MinValueValidator(
            1, message='Значение не может быть меньше 1')]

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='recipes/'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            1, message='Значение не может быть меньше 1')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' {self.amount} '
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в избранном',
        related_name='favorites_recipe',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_recipe',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил в список покупок - {self.recipe}'
