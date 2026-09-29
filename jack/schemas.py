from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance",
]

Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=500)
    goal: Goal
    intensity: Intensity

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, value: str) -> str:
        if not value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("User ID may contain letters, numbers, hyphens and underscores only.")
        return value


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    feedback: str = Field(min_length=3, max_length=2000)


class PlanResponse(BaseModel):
    user_id: str
    name: str
    age: int
    weight: float
    goal: str
    intensity: str
    workout_plan: str
    nutrition_tip: str
    feedback: str | None = None
    updated: bool = False
