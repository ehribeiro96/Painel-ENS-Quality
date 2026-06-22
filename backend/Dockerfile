FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend/itam-platform
COPY frontend/itam-platform/package*.json ./
RUN npm ci
COPY frontend/itam-platform ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend:/app \
    APP_HOST=0.0.0.0 \
    APP_PORT=8080 \
    ENS_BUILD_FRONTEND=0

WORKDIR /app


COPY backend/requirements.txt /app/backend-requirements.txt
COPY requirements-legacy.txt /app/legacy-requirements.txt
RUN pip install --no-cache-dir -r /app/backend-requirements.txt \
    && pip install --no-cache-dir -r /app/legacy-requirements.txt

COPY backend /app/backend
COPY src /app/src
COPY assets /app/assets
COPY run.py /app/run.py
COPY --from=frontend-builder /app/frontend/itam-platform/dist /app/frontend/itam-platform/dist

EXPOSE 8080
CMD ["python", "run.py"]
