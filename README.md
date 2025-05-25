## Инструкция
### 1. Клонируйте репозиторий

```bash
git clone git@github.com:28awg-2c/foodgram-st.git
cd foodgram-st
```

### 2. `.env` файл

Файл `infra/.env` уже создан и содержит все секреты:

### 3. Соберите и запустите контейнеры

```bash
docker-compose -f infra/docker-compose.yml up -d --build
```


## Доступ

* **Backend:** [http://localhost:8000](http://localhost:8000)
* **Frontend:** [http://localhost/](http://localhost/)
* **Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)


## Небольшое уточнение

* При первом запуске необходимо дождаться загрузки тестовых данных, чтобы увидеть список рецептов на главной странице для неавторизированного пользователя
* Этот момент можно отследить в логах контейнера бэкенда(foodgram_diploma_backend) 
