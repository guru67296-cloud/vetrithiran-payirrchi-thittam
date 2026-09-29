from ..schemas import UserInput
from .gemini_client import SAFETY_NOTE, gemini_service


def _fallback(original_plan: str, feedback: str) -> str:
    return (
        f"{original_plan}\n\n"
        f"UPDATED FROM USER FEEDBACK\n"
        f"Requested changes: {feedback}\n"
        "Adjustment: Keep the existing structure, add the requested preference where practical, "
        "and preserve at least one recovery day. Reduce volume if the current workload feels too difficult.\n"
        f"{SAFETY_NOTE}"
    )


def update_workout_plan(user: UserInput, original_plan: str, feedback: str) -> str:
    prompt = f"""
You are FitBuddy. Revise an existing 7-day general wellness workout plan using the user's feedback.

User:
- Name: {user.name}
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Intensity: {user.intensity}

Original plan:
---BEGIN PLAN---
{original_plan}
---END PLAN---

User feedback:
---BEGIN FEEDBACK---
{feedback}
---END FEEDBACK---

Return a complete revised 7-day plan, not a list of changes.
Respect the user's goal and intensity. Preserve recovery/rest.
Do not provide medical diagnosis, medication advice, extreme dieting, or dangerous exercise.
{SAFETY_NOTE}
"""
    result = gemini_service.generate(
        prompt,
        gemini_service.settings.gemini_workout_model,
    )
    return result or _fallback(original_plan, feedback)
