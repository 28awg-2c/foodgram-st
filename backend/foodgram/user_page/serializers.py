from rest_framework import serializers
from foodgram_app.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    Возвращает id, name и measurement_unit ингредиента.
    """
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']