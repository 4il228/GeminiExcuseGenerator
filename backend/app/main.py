import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from dotenv import load_dotenv

from .models import ExcuseRequest, ExcuseResponse, SituationEnum

load_dotenv()

app = FastAPI(title="Excuse Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

SITUATION_MAP = {
    SituationEnum.LATE_WORK: "опоздание на рабочее место в будний день",
    SituationEnum.MISSED_HOMEWORK: "невыполнение домашнего задания к дедлайну",
    SituationEnum.FORGOT_BIRTHDAY: "забытый день рождения близкого человека или коллеги",
    SituationEnum.DOG_ATE_CODE: "непредвиденный технический сбой/потеря исходного кода"
}

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY не задан в переменной окружения")

genai.configure(api_key=API_KEY)

SYSTEM_INSTRUCTION = (
    "Ты — человек, который придумывает правдоподобные оправдания. Пиши как живой человек, не как робот. "
    "Используй разговорные слова, естественные конструкции, конкретные детали. "
    "Отмазка должна звучать так, будто её реально сказал живой человек — с деталями, эмоциями, характером. "
    "Пиши от первого лица, как будто ты realmente оправдываешься перед начальником, учителем или другом. "
    "Ни в коем случае не шути. Отмазка должна быть абсолютно серьёзной и звучать как настоящая причина. "
    "Она должна быть настолько правдоподобной, что человек, которому её говорят, поверит и не будет задавать лишних вопросов. "
    "Длина отмазки: 2-4 предложения. Не больше."
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.post(
    "/api/v1/generate", 
    response_model=ExcuseResponse, 
    status_code=status.HTTP_200_OK,
    summary="Безопасная генерация отмазки"
)
async def generate_excuse(payload: ExcuseRequest):
    description = SITUATION_MAP.get(payload.situation_id)
    if not description:
        raise HTTPException(status_code=400, detail="Invalid situation mapping")
    
    user_prompt = (
        f"Человек опоздал/забыл/не сделал вот из-за этой ситуации: {description}. "
        f"Придумай максимально правдоподобное оправдание, которое он мог бы сказать вслух. "
        f"Отмазка должна быть серьёзной, убедительной и звучать как настоящая причина — чтобы в неё поверили с первого раза."
    )

    try:
        model = genai.GenerativeModel(
            'gemini-3.5-flash',
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=GenerationConfig(
                temperature=0.85,
                response_mime_type="application/json",
                response_schema=ExcuseResponse
            )
        )
        
        response = model.generate_content(user_prompt)
        
        return ExcuseResponse.model_validate_json(response.text)
        
    except Exception as e:
        print(f"GEMINI ERROR: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Ошибка генерации на стороне AI-провайдера"
        )
