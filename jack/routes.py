from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import Plan, User
from .schemas import FeedbackRequest, PlanResponse, UserInput
from .services.nutrition_generator import generate_nutrition_tip_with_flash
from .services.plan_updater import update_workout_plan
from .services.workout_generator import generate_workout_gemini


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()


def _user_from_db(db: Session, user_id: str) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))


def _plan_from_db(db: Session, user_id: str) -> Plan | None:
    return db.scalar(
        select(Plan)
        .where(Plan.user_id == user_id)
        .order_by(Plan.id.desc())
    )


def _response_context(user: User, plan: Plan) -> dict:
    return {
        "user": user,
        "plan": plan,
        "username": user.name,
        "user_id": user.user_id,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "workout_plan": plan.updated_plan or plan.original_plan,
        "original_plan": plan.original_plan,
        "nutrition_tip": plan.nutrition_tip,
        "feedback": plan.feedback,
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=422,
        )

    user = _user_from_db(db, data.user_id)
    if user is None:
        user = User(
            user_id=data.user_id,
            name=data.name,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )
        db.add(user)
        db.flush()
    else:
        user.name = data.name
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

    workout = generate_workout_gemini(data)
    tip = generate_nutrition_tip_with_flash(data)

    plan = _plan_from_db(db, data.user_id)
    if plan is None:
        plan = Plan(
            user_id=data.user_id,
            original_plan=workout,
            nutrition_tip=tip,
        )
        db.add(plan)
    else:
        plan.original_plan = workout
        plan.updated_plan = None
        plan.nutrition_tip = tip
        plan.feedback = None

    db.commit()
    db.refresh(user)
    db.refresh(plan)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context=_response_context(user, plan),
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = _user_from_db(db, user_id)
    plan = _plan_from_db(db, user_id)

    if not user or not plan:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": "User or plan was not found. Please generate a plan first."},
            status_code=404,
        )

    try:
        feedback_data = FeedbackRequest(feedback=feedback)
        user_data = UserInput(
            user_id=user.user_id,
            name=user.name,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={**_response_context(user, plan), "error": str(exc)},
            status_code=422,
        )

    revised = update_workout_plan(
        user_data,
        plan.updated_plan or plan.original_plan,
        feedback_data.feedback,
    )
    plan.updated_plan = revised
    plan.feedback = feedback_data.feedback
    db.commit()
    db.refresh(plan)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            **_response_context(user, plan),
            "success": "Your workout plan has been updated using your feedback.",
        },
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    plans = {
        plan.user_id: plan
        for plan in db.scalars(select(Plan).order_by(Plan.id.desc())).all()
    }
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users, "plans": plans},
    )


@router.get("/api/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}


@router.post("/api/workouts", response_model=PlanResponse)
def api_generate_workout(
    payload: UserInput,
    db: Session = Depends(get_db),
):
    user = _user_from_db(db, payload.user_id)
    if user is None:
        user = User(
            user_id=payload.user_id,
            name=payload.name,
            age=payload.age,
            weight=payload.weight,
            goal=payload.goal,
            intensity=payload.intensity,
        )
        db.add(user)
        db.flush()
    else:
        user.name = payload.name
        user.age = payload.age
        user.weight = payload.weight
        user.goal = payload.goal
        user.intensity = payload.intensity

    workout = generate_workout_gemini(payload)
    tip = generate_nutrition_tip_with_flash(payload)

    plan = _plan_from_db(db, payload.user_id)
    if plan is None:
        plan = Plan(
            user_id=payload.user_id,
            original_plan=workout,
            nutrition_tip=tip,
        )
        db.add(plan)
    else:
        plan.original_plan = workout
        plan.updated_plan = None
        plan.nutrition_tip = tip
        plan.feedback = None

    db.commit()

    return PlanResponse(
        user_id=user.user_id,
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
        workout_plan=plan.original_plan,
        nutrition_tip=plan.nutrition_tip,
        updated=False,
    )


@router.post("/api/workouts/{user_id}/feedback", response_model=PlanResponse)
def api_update_workout(
    user_id: str,
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):
    user = _user_from_db(db, user_id)
    plan = _plan_from_db(db, user_id)

    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found")

    user_data = UserInput(
        user_id=user.user_id,
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )
    revised = update_workout_plan(
        user_data,
        plan.updated_plan or plan.original_plan,
        payload.feedback,
    )
    plan.updated_plan = revised
    plan.feedback = payload.feedback
    db.commit()

    return PlanResponse(
        user_id=user.user_id,
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
        workout_plan=revised,
        nutrition_tip=plan.nutrition_tip,
        feedback=payload.feedback,
        updated=True,
    )


@router.get("/api/users/{user_id}")
def api_get_user(user_id: str, db: Session = Depends(get_db)):
    user = _user_from_db(db, user_id)
    plan = _plan_from_db(db, user_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found")

    return {
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
        },
        "plan": {
            "original_plan": plan.original_plan,
            "updated_plan": plan.updated_plan,
            "nutrition_tip": plan.nutrition_tip,
            "feedback": plan.feedback,
        },
    }


@router.get("/api/users")
def api_get_all_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]
