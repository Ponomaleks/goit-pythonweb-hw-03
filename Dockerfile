FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  APP_DATA_DIR=/data

WORKDIR /app

# Install dependencies from Pipfile into the system environment.
COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv \
  && pipenv install --system --deploy --ignore-pipfile \
  && pip uninstall -y pipenv

COPY . .

# Ensure runtime directories exist and volume path is writable.
RUN useradd --create-home appuser \
  && mkdir -p /data \
  && chmod 777 /data \
  && mkdir -p /app/storage \
  && chown -R appuser:appuser /app

USER appuser

EXPOSE 3000

VOLUME ["/data"]

CMD ["python", "main.py"]