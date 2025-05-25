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


