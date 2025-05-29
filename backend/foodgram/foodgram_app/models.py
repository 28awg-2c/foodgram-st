from django.db import models
from user_login.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

MIN_COOK_AND_AMOUNT = 1
MAX_COOK_AND_AMOUNT = 32000
MAX_NAME_LENGTH = 200
MAX_MEASUREMENT_LENGTH = 50


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=MAX_MEASUREMENT_LENGTH,
                                        verbose_name='Мера')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resipe',
        verbose_name='Автор')
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='static/posts/', verbose_name='Фото')
    text = models.TextField(verbose_name='Рецепт')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления', validators=[
            MinValueValidator(MIN_COOK_AND_AMOUNT),
            MaxValueValidator(MAX_COOK_AND_AMOUNT)
        ])

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Кол-во ингредиента', validators=[
            MinValueValidator(MIN_COOK_AND_AMOUNT),
            MaxValueValidator(MAX_COOK_AND_AMOUNT)
        ])

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Рецепт/Ингредиент'
        unique_together = ('recipe', 'ingredient')
