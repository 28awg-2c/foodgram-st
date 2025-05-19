from django.db import models
from user_login.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Models):
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resipe')
    title = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='posts/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    cook_time_min = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredient')
