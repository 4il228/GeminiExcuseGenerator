# SPEC.md: Архитектурная спецификация сервиса «Генератор отмазок»

---

## 1. Обзор системы и бизнес-логика

«Генератор отмазок» — это ироничный одностраничный веб-сервис (SPA), предназначенный для мгновенной генерации креативных оправданий на основе предопределенных жизненных ситуаций. Система спроектирована с упором на максимальную безопасность (Zero Prompt Injection) и детерминированную структуру ответов от LLM.

### Ключевые компоненты UI

* **Селектор ситуаций:** Интерактивные карточки или выпадающий список для выбора предустановленного сценария.
* **Экран выдачи:** Блок сгенерированного текста с анимацией появления.
* **Рейтинг правдоподобности:** Визуальный виджет (прогресс-бар/индикатор), отображающий оценку реалистичности отмазки.
* **Экшен-панель:** Кнопка быстрого копирования текста в буфер обмена.

---

## 2. Безопасный архитектурный воркфлоу (Data Flow)

Для исключения возможности внедрения стороннего промпта (Prompt Injection) архитектура полностью изолирует пользователя от прямого текстового ввода. Вся коммуникация с LLM строится на передаче строгих идентификаторов (ID).

```
[Client App] 
      │
      │ (POST /api/v1/generate {"situation_id": "late_to_work"})
      ▼
[FastAPI Endpoint] 
      │
      ├─► [Validator] (Проверка по белому списку Enum)
      │
      ▼
[Prompt Builder] (Сборка захардкоженного промпта + подстановка безопасного описания)
      │
      │ (Gemini API Call + JSON Schema + Temp 0.7)
      ▼
[Google Gemini API] 
      │
      │ (Возвращает строго валидный JSON)
      ▼
[FastAPI Endpoint] 
      │
      │ (Response Serialization)
      ▼
[Client App] (Отображение отмазки и скора)

```

---

## 3. Спецификация API и Backend (Python 3.13 + FastAPI)

### Схема данных (Pydantic Models)

```python
from enum import Enum
from pydantic import BaseModel, Field

class SituationEnum(str, Enum):
    LATE_WORK = "late_work"
    MISSED_HOMEWORK = "missed_homework"
    FORGOT_BIRTHDAY = "forgot_birthday"
    DOG_ATE_CODE = "dog_ate_code"

class ExcuseRequest(BaseModel):
    situation_id: SituationEnum = Field(
        ..., 
        description="Уникальный идентификатор валидной жизненной ситуации"
    )

class ExcuseResponse(BaseModel):
    excuse: str = Field(..., description="Текст сгенерированной отмазки")
    believability_score: int = Field(..., description="Рейтинг правдоподобности в процентах от 0 до 100")

```

### Безопасная реализация эндпоинта

```python
import os
from fastapi import FastAPI, HTTPException, status
import google.generativeai as genai
from google.generativeai.types import GenerateContentConfig

app = FastAPI(title="Excuse Generator API", version="1.0.0")

# Белый список маппинга ситуаций для системного промпта
SITUATION_MAP = {
    SituationEnum.LATE_WORK: "опоздание на рабочее место в будний день",
    SituationEnum.MISSED_HOMEWORK: "невыполнение домашнего задания к дедлайну",
    SituationEnum.FORGOT_BIRTHDAY: "забытый день рождения близкого человека или коллеги",
    SituationEnum.DOG_ATE_CODE: "непредвиденный технический сбой/потеря исходного кода"
}

# Инициализация Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY не задан в переменной окружения")

genai.configure(api_key=API_KEY)

@app.post(
    "/api/v1/generate", 
    response_model=ExcuseResponse, 
    status_code=status.HTTP_200_OK,
    summary="Безопасная генерация отмазки"
)
async def generate_excuse(payload: ExcuseRequest):
    # 1. Валидация входных данных уже выполнена Pydantic на этапе парсинга
    description = SITUATION_MAP.get(payload.situation_id)
    if not description:
        raise HTTPException(status_code=400, detail="Invalid situation mapping")
    
    # 2. Формирование изолированного системного промпта
    system_instruction = (
        "Ты — гениальный и ироничный мастер оправданий. Твоя задача — придумать "
        "максимально креативную, но при этом стилистически убедительную отмазку для заданной ситуации. "
        "Ты должен возвращать ответ строго в соответствии с заданной JSON-схемой."
    )
    
    user_prompt = f"Сгенерируй отмазку для следующей ситуации: {description}."

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 3. Конфигурация детерминированного вызова с JSON-схемой
        config = GenerateContentConfig(
            temperature=0.7,
            response_mime_type="application/json",
            response_schema=ExcuseResponse,
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            user_prompt,
            generation_config=config
        )
        
        # 4. Валидация и отправка ответа клиенту
        return ExcuseResponse.model_validate_json(response.text)
        
    except Exception as e:
        # Логирование ошибки (в продакшене использовать logger)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Ошибка генерации на стороне AI-провайдера"
        )

```

---

## 4. UI/UX Спецификация и Дизайн-система (google-stitch)

Дизайн спроектирован на базе современных дизайн-токенов с легким уклоном в «ироничный корпоративный минимализм» (Clean Neo-Brutalism/Corporate Irony).

### Цветовая палитра (Tailwind CSS)

* **Background (Фон):** `bg-slate-50` (Чистый, слегка прохладный светлый фон)
* **Card/Surface (Поверхности):** `bg-white` с границей `border-slate-200`
* **Primary Action (Кнопки/Фокус):** `bg-indigo-600` / `hover:bg-indigo-700`
* **Accent/Score (Индикатор правдоподобности):**
* Высокий (>=75%): `text-emerald-600` / `bg-emerald-50`
* Средний (50-74%): `text-amber-600` / `bg-amber-50`
* Низкий (<50%): `text-rose-600` / `bg-rose-50`



### Спецификация компонентов UI

#### 1. Контейнер селектора ситуаций (Grid Layout)

```html
<div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
  <!-- Карточка ситуации -->
  <button class="p-4 rounded-xl border border-slate-200 bg-white text-left transition-all hover:border-indigo-500 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
    <div class="font-semibold text-slate-800">Опоздал на работу</div>
    <div class="text-sm text-slate-500 mt-1">Для жестких начальников и утренних пробок</div>
  </button>
</div>

```

#### 2. Блок отображения результата (Excuse Output Slot)

```html
<div class="mt-8 p-6 rounded-2xl border-2 border-dashed border-slate-200 bg-white max-w-2xl mx-auto space-y-4">
  <div class="flex items-center justify-between">
    <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Сгенерированный алиби-текст</span>
    <!-- Индикатор правдоподобности -->
    <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-sm font-medium">
      <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
      <span>87% правдоподобности</span>
    </div>
  </div>
  
  <p class="text-lg text-slate-700 leading-relaxed font-serif italic">
    «Произошел редкий сбой синхронизации системы умного дома, из-за которого будильник перешел в режим часового пояса Токио. Я проснулся вовремя, но концептуально в будущем».
  </p>
  
  <!-- Панель действий -->
  <div class="flex justify-end pt-2">
    <button class="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
      <span>Скопировать отмазку</span>
    </button>
  </div>
</div>

```

---

## 5. Переменные окружения (`.env`)

Для локальной разработки и деплоя необходим файл конфигурации в корне бэкенда:

```env
# Имя окружения
ENV=production
# Хост и порт для FastAPI
HOST=0.0.0.0
PORT=8000

# Ключ доступа к Gemini API (Получать в Google AI Studio)
GEMINI_API_KEY=AIzaSyYourActualSecureGeminiKeyHere_Example

```