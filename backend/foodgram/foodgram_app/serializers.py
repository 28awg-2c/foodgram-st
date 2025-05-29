from rest_framework import serializers
from .models import Recipe, RecipeIngredient, Ingredient
import base64
import uuid
from django.core.files.base import ContentFile
from user_login.serializers import UserReadSerializer

MIN_COOK_AND_AMOUNT = 1
MAX_COOK_AND_AMOUNT = 32000


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        try:
            if ';base64,' in data:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                return ContentFile(base64.b64decode(imgstr), name=filename)
            return super().to_internal_value(data)
        except Exception:
            raise serializers.ValidationError(
                "Неправильный формат изображения")


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        max_value=MAX_COOK_AND_AMOUNT, min_value=MIN_COOK_AND_AMOUNT)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient',
        many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.in_favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.shopping_carts.filter(user=user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField(
        max_value=MAX_COOK_AND_AMOUNT,
        min_value=MIN_COOK_AND_AMOUNT)

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]
        read_only_fields = ['id', 'author',
                            'is_favorited', 'is_in_shopping_cart']

    def validate(self, data):
        if 'ingredients' not in data or not data['ingredients']:
            raise serializers.ValidationError({
                'ingredients': 'Должен быть указан хотя бы один ингредиент'
            })

        ingredients = [item['id'] for item in data['ingredients']]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться'
            })

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        self._create_ingredient_relations(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)

        self._update_recipe_fields(instance, validated_data)

        if ingredients_data:
            self._refresh_recipe_ingredients(instance, ingredients_data)

        return instance

    def _update_recipe_fields(self, instance, fields_data):
        for field, value in fields_data.items():
            setattr(instance, field, value)
        instance.save()

    def _refresh_recipe_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.recipe_ingredient.all().delete()

        self._create_ingredient_relations(recipe, ingredients_data)

    def _create_ingredient_relations(self, recipe, ingredients_data):
        for ingredient_item in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_item['id'],
                amount=ingredient_item['amount']
            )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and obj.shopping_carts.filter(user=request.user).exists()
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
