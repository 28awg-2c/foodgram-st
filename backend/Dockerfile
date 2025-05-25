FROM python:3.10-slim

WORKDIR /work_dir

RUN apt-get update && apt-get install -y wait-for-it && \
    rm -rf /var/lib/apt/lists/*

COPY foodgram/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /work_dir/foodgram

CMD ["sh", "-c", "/usr/bin/wait-for-it db:5432 -- python manage.py migrate && python manage.py collectstatic --noinput && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"]