from django.apps import AppConfig


class FoodgramAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodgram_app'

    def ready(self):
        from foodgram_app.load_test_data import (
            load_ingredients_from_json,
            load_recipes_from_json
        )
        load_ingredients_from_json()
        load_recipes_from_json()
