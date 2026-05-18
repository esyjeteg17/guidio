# guidio

AI-помощник для дизайнеров: подбор шрифтов, мудбордов, цветовых палитр через чат.

## Стек

- **Backend:** Django 5.1 + DRF + PostgreSQL (pgvector) + SimpleJWT
- **Frontend:** Nuxt 4 (SPA) + TypeScript + Tailwind CSS 4 + Pinia
- **AI:** DeepSeek + локальные эмбеддинги (multilingual-e5-large)

## Запуск через Docker

```bash
cp .env.example .env
# заполни SECRET_KEY, DEEPSEEK_API_KEY и т.д.
docker compose up -d --build
```

Сайт будет доступен на `http://<host>/`. API — `http://<host>/api/`, админка — `http://<host>/admin/`.

### Загрузка шрифтов (после первого запуска)

```bash
docker compose exec backend python manage.py import_fonts_data
docker compose exec backend python manage.py extract_font_files
docker compose exec backend python manage.py generate_embeddings
```

## Локальный dev без Docker

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # заполни ключи
python manage.py migrate
python manage.py runserver 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
