import json
import os
from django.conf import settings
from .models import User


def load_users_from_json():
    json_file = 'users.json'
    file_path = os.path.join(settings.BASE_DIR, 'data', json_file)

    if not os.path.exists(file_path):
        print(f"Файл {json_file} не найден по пути: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            users_data = json.load(file)

            created_count = 0
            for user_data in users_data:
                try:
                    # Создаем пользователя с хешированием пароля
                    user, created = User.objects.get_or_create(
                        email=user_data['email'],
                        defaults={
                            'username': user_data['username'],
                            'first_name': user_data['first_name'],
                            'last_name': user_data['last_name'],
                            'avatar': user_data.get('avatar', ''),
                        }
                    )

                    if created:
                        user.set_password(user_data['password'])
                        user.save()
                        created_count += 1
                    else:
                        print(
                            f"Пользователь с email {user_data['email']} уже существует. Пропускаем.")

                except IntegrityError as e:
                    print(
                        f"Ошибка при создании пользователя {user_data['email']}: {str(e)}")
                    continue

            total = len(users_data)
            print(
                f"Успешно обработано {total} пользователей. Добавлено новых: {created_count}")
            return True

    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {str(e)}")
    except KeyError as e:
        print(f"Некорректная структура данных: отсутствует ключ {str(e)}")
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")

    return False
