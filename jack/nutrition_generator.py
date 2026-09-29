from ..schemas import UserInput
from .gemini_client import SAFETY_NOTE, gemini_service


def _fallback(user: UserInput) -> str:
    tips = {
        "weight loss": "Build meals around vegetables, a protein source, whole foods and water; avoid aggressive restriction.",
        "muscle gain": "Include a protein-rich food at regular meals, plus carbohydrates and fluids to support training and recovery.",
        "general wellness": "Aim for balanced meals with vegetables or fruit, protein, whole grains or other high-fiber foods, and adequate fluids.",
        "flexibility": "Stay hydrated and eat balanced meals with adequate protein and micronutrient-rich foods to support recovery.",
        "endurance": "Prioritize fluids and carbohydrate-containing whole foods around longer sessions, alongside adequate protein.",
    }
    return tips[user.goal] + " " + SAFETY_NOTE


def generate_nutrition_tip_with_flash(user: UserInput) -> str:
    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.
Give one concise, practical nutrition or recovery tip for:
- Goal: {user.goal}
- Intensity: {user.intensity}
- Age: {user.age}
- Weight: {user.weight} kg

Do not prescribe supplements or medication. Do not provide extreme calorie targets.
Avoid diagnosing disease. Keep the answer to 2–5 sentences.
{SAFETY_NOTE}
"""
    result = gemini_service.generate(
        prompt,
        gemini_service.settings.gemini_tip_model,
    )
    return result or _fallback(user)
