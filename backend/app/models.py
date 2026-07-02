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
