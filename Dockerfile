FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY --from=frontend /frontend/dist /app/frontend/dist

WORKDIR /app/backend
ENV PORT=5000
EXPOSE 5000

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120"]
