from django.apps import AppConfig


class UserLoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_login'

    def ready(self):
        from user_login.load_test_data import (
            load_users_from_json
        )
        load_users_from_json()
