from ..schemas import UserInput
from .gemini_client import SAFETY_NOTE, gemini_service


def _fallback(user: UserInput) -> str:
    focus = {
        "weight loss": "full-body conditioning and moderate cardio",
        "muscle gain": "strength and progressive resistance",
        "general wellness": "balanced full-body fitness",
        "flexibility": "mobility, flexibility and controlled strength",
        "endurance": "cardiovascular endurance and steady conditioning",
    }[user.goal]

    return f"""7-DAY FITBUDDY PLAN
Goal: {user.goal.title()}
Intensity: {user.intensity.title()}
Primary focus: {focus}

Day 1 – Full Body
• Warm-up: 5–10 minutes of easy walking and mobility
• Main: Squats 3×10, incline push-ups 3×8–12, glute bridges 3×12, plank 3×20–30 sec
• Cooldown: 5 minutes easy stretching

Day 2 – Cardio & Core
• Warm-up: 5 minutes
• Main: Brisk walk/cycle 20–30 minutes; dead bug 3×10/side; bird dog 3×10/side
• Cooldown: 5 minutes

Day 3 – Recovery
• 20–30 minutes easy walking
• Gentle mobility for hips, shoulders and ankles
• Prioritize sleep and hydration

Day 4 – Full Body Strength
• Warm-up: 5–10 minutes
• Main: Reverse lunges 3×8/side, rows 3×10, hip hinge 3×10, side plank 3×20 sec/side
• Cooldown: 5 minutes

Day 5 – Cardio
• 20–30 minutes at a conversational pace
• Finish with gentle stretching

Day 6 – Goal Focus
• Repeat 3–4 comfortable movements from Days 1–4
• Keep technique controlled and stop if you experience pain

Day 7 – Rest & Recovery
• Rest or take an easy walk
• Gentle mobility and recovery

Progression: Start at the lower end of the suggested range and increase gradually only when the exercises feel comfortable.
{SAFETY_NOTE}"""


def generate_workout_gemini(user: UserInput) -> str:
    prompt = f"""
You are FitBuddy, a careful fitness-planning assistant.
Create a personalized 7-day general wellness workout plan.

User:
- Name: {user.name}
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Preferred intensity: {user.intensity}

Requirements:
1. Provide Day 1 through Day 7.
2. Every training day should include warm-up, exercises with sets/reps or duration,
   rest guidance, and cooldown/recovery.
3. Include sensible rest/recovery days.
4. Tailor the plan to the stated goal and intensity without claiming medical certainty.
5. Do not prescribe medication, extreme calorie restriction, dangerous exercises,
   or diagnose medical conditions.
6. Keep the output readable in plain text.
7. Finish with a short safety note.

{SAFETY_NOTE}
"""
    result = gemini_service.generate(
        prompt,
        gemini_service.settings.gemini_workout_model,
    )
    return result or _fallback(user)
