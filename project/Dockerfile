FROM node:18 AS frontend-builder

WORKDIR /frontend

COPY src/package.json src/package-lock.json ./

RUN npm install && npm cache clean --force

RUN mkdir -p src/static/scss/bootstrap && \
    mkdir -p src/static/css/bootstrap && \
    mkdir -p src/static/js/bootstrap

RUN cp -r node_modules/bootstrap/scss/* src/static/scss/bootstrap/

COPY src/static/scss/*.scss src/static/scss/

RUN apt-get update && \
    apt-get install -y sassc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    sassc -t compressed src/static/scss/style.scss src/static/css/style.css && \
    cp node_modules/bootstrap/dist/css/bootstrap.min.css src/static/css/bootstrap/ && \
    cp node_modules/bootstrap/dist/js/bootstrap.bundle.min.js src/static/js/bootstrap/

FROM python:3.13

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y gdal-bin postgis

COPY --from=frontend-builder /frontend/src/static /app/src/static

COPY . .

RUN python src/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]