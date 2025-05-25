import json
import os
from django.conf import settings
from .models import Ingredient, Recipe, RecipeIngredient
from user_login.models import User


def load_ingredients_from_json():
    json_file = 'ingredients.json'
    file_path = os.path.join(settings.BASE_DIR, 'data', json_file)

    if not os.path.exists(file_path):
        print(f"Файл {json_file} не найден по пути: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            ingredients = json.load(file)

            created_count = 0
            for item in ingredients:
                _, created = Ingredient.objects.get_or_create(
                    name=item['name'].strip().lower(),
                    measurement_unit=item['measurement_unit'].lower()
                )
                if created:
                    created_count += 1

            total = len(ingredients)
            print(
                f"Успешно обработано {total} ингредиентов. Добавлено новых: {created_count}")
            return True

    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {str(e)}")
    except KeyError as e:
        print(f"Некорректная структура данных: отсутствует ключ {str(e)}")
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")

    return False


def load_recipes_from_json():
    json_file = 'recipes.json'
    file_path = os.path.join(settings.BASE_DIR, 'data', json_file)

    if not os.path.exists(file_path):
        print(f"Файл {json_file} не найден по пути: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            recipes_data = json.load(file)

            created_count = 0
            for recipe_data in recipes_data:
                try:
                    author = User.objects.get(
                        email=recipe_data['author_email'])
                except User.DoesNotExist:
                    print(
                        f"Автор с email {recipe_data['author_email']} не найден. Пропускаем рецепт.")
                    continue

                recipe, created = Recipe.objects.get_or_create(
                    author=author,
                    name=recipe_data['name'],
                    defaults={
                        'image': recipe_data['image'],
                        'text': recipe_data['text'],
                        'cooking_time': recipe_data['cooking_time']
                    }
                )

                if not created:
                    recipe.image = recipe_data['image']
                    recipe.text = recipe_data['text']
                    recipe.cooking_time = recipe_data['cooking_time']
                    recipe.save()

                RecipeIngredient.objects.filter(recipe=recipe).delete()

                for component in recipe_data['components']:
                    try:
                        ingredient = Ingredient.objects.get(
                            name=component['name'].lower())
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient=ingredient,
                            amount=component['amount']
                        )
                    except Ingredient.DoesNotExist:
                        print(
                            f"Ингредиент {component['name']} не найден. Пропускаем.")

                if created:
                    created_count += 1

            total = len(recipes_data)
            print(
                f"Успешно обработано {total} рецептов. Добавлено новых: {created_count}")
            return True

    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {str(e)}")
    except KeyError as e:
        print(f"Некорректная структура данных: отсутствует ключ {str(e)}")
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")

    return False
