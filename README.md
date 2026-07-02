<div align="center">

# Генератор отмазок

**Ироничный веб-сервис для генерации правдоподобных оправданий на базе Google Gemini**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-3.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![Tailwind](https://img.shields.io/badge/Twind_CSS-CDN-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

</div>

---

## Что это?

Выбери ситуацию — получи готовое, правдоподобное оправдание. Сервис генерирует серьёзные, убедительные отмазки, которые можно использовать в реальной жизни.

### Возможности

- **4 предустановленных ситуации** — опоздание, забытый день рождения, невыполненная домашка, потерянный код
- **Правдоподобные отмазки** — генерируются с учётом контекста и деталей
- **Рейтинг правдоподобности** — визуальная оценка убедительности (0–100%)
- **Один клик** — копирование текста в буфер обмена
- **Безопасность** — защита от Prompt Injection через строгую валидацию типов

---

## Архитектура

```
┌─────────────┐      POST /api/v1/generate      ┌─────────────┐
│   Frontend  │  ──────────────────────────────► │   Backend   │
│  HTML/CSS   │ ◄────────────────────────────── │   FastAPI   │
│  Tailwind   │      JSON с отмазкой            │             │
└─────────────┘                                  └──────┬──────┘
                                                        │
                                                        ▼
                                                 ┌─────────────┐
                                                 │ Google      │
                                                 │ Gemini API  │
                                                 └─────────────┘
```

**Безопасность:** Пользователь не может передать произвольный текст — только `situation_id` из белого списка (`SituationEnum`). Это исключает Prompt Injection.

---

## Быстрый старт

### Клонирование

```bash
git clone https://github.com/4il228/GeminiExcuseGenerator.git
cd GeminiExcuseGenerator
```

### Установка

```bash
cd backend
pip install -r requirements.txt
```

### Настройка

Создайте файл `backend/.env` и добавьте ваш API-ключ:

```env
GEMINI_API_KEY=ваш_ключ_из_google_ai_studio
```

> Получить ключ: [Google AI Studio](https://aistudio.google.com/apikey)

### Запуск

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Откройте в браузере: [http://localhost:8000](http://localhost:8000)

---

## Docker

### Сборка образа

```bash
docker build -f backend/Dockerfile -t excuse-generator .
```

### Запуск контейнера

```bash
docker run -p 8000:8000 -e GEMINI_API_KEY=ваш_ключ excuse-generator
```

---

## API

### Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Главная страница (фронтенд) |
| `GET` | `/health` | Проверка работоспособности |
| `POST` | `/api/v1/generate` | Генерация отмазки |

### Пример запроса

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"situation_id": "late_work"}'
```

### Ответ

```json
{
  "excuse": "Произошёл редкий сбой системы умного дома — будильник перешёл на токийское время. Проснулся вовремя, но концептуально оказался в будущем.",
  "believability_score": 87
}
```

### Доступные ситуации

| ID | Описание |
|----|----------|
| `late_work` | Опоздание на работу |
| `missed_homework` | Не сделана домашка |
| `forgot_birthday` | Забыт день рождения |
| `dog_ate_code` | Собака съела код |

---

## Тесты

```bash
cd backend
python -m pytest test_api.py -v
```

---

## Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.13, FastAPI, Pydantic |
| AI | Google Gemini 3.5 Flash |
| Frontend | HTML5, Tailwind CSS |
| Тестирование | pytest, httpx |
| Контейнеризация | Docker |

---

## Структура проекта

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI приложение
│   │   └── models.py        # Pydantic модели
│   ├── .env.example         # Шаблон переменных окружения
│   ├── Dockerfile
│   ├── requirements.txt
│   └── test_api.py
├── frontend/
│   ├── index.html           # SPA интерфейс
│   └── styles.css
├── AGENTS.md                # Инструкции для AI-агентов
├── PLAN.md                  # План разработки
├── SPEC.md                  # Архитектурная спецификация
└── README.md
```

---

## Contributing

1. Fork проекта
2. Создайте ветку (`git checkout -b feature/your-feature`)
3. Коммитьте изменения (`git commit -m 'Add your feature'`)
4. Пушьте в ветку (`git push origin feature/your-feature`)
5. Откройте Pull Request

---

<div align="center">

**Сделано с иронией и любовью к деталям**

</div>
