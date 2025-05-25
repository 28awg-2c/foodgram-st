## Инструкция
### 1. Клонируйте репозиторий

```bash
git clone git@github.com:28awg-2c/foodgram-st.git
cd foodgram-st
```

### 2. Создайте `.env` файл

Создайте файл `infra/.env` подходящие для прохождения тестов:

```env
# PostgreSQL настройки
POSTGRES_DB=foodgram
POSTGRES_USER=anast
POSTGRES_PASSWORD=anastanast
POSTGRES_HOST=foodgram_diploma_db
POSTGRES_PORT=5432

# Django настройки
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Соберите и запустите контейнеры

```bash
docker-compose -f infra/docker-compose.yml up -d --build
```


## Доступ

* **Backend:** [http://localhost:8000](http://localhost:8000)
* **Frontend:** [http://localhost/](http://localhost/)
* **Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)


