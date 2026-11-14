"""Onboarding-Service — Fortschritt und Setup-Checkliste."""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.einheit import Einheit
from app.models.mieter import Mieter
from app.models.mietvertraege import Mietvertrag
from app.models.objekt import Objekt
from app.models.onboarding import OnboardingProgress
from app.models.subscription import Subscription
from app.models.user import User

# Feste Onboarding-Schritte in der vom User gewünschten Reihenfolge.
ONBOARDING_STEPS: list[tuple[str, str]] = [
    ("profile_completed", "Profil vervollständigt"),
    ("first_objekt", "Erstes Objekt"),
    ("first_einheit", "Erste Einheit"),
    ("first_mieter", "Erster Mieter"),
    ("first_vertrag", "Erster Vertrag"),
    ("abo_confirmed", "Abo bestätigt"),
]


async def _get_or_create_progress_rows(
    db: AsyncSession,
    user_id: int,
) -> dict[str, OnboardingProgress]:
    """Lädt alle Onboarding-Zeilen eines Users oder legt fehlende an."""
    result = await db.execute(
        select(OnboardingProgress).where(OnboardingProgress.user_id == user_id)
    )
    rows: dict[str, OnboardingProgress] = {
        row.step: row for row in result.scalars().all()
    }

    for step, _label in ONBOARDING_STEPS:
        if step not in rows:
            row = OnboardingProgress(user_id=user_id, step=step, is_done=False)
            db.add(row)
            rows[step] = row

    await db.flush()
    return rows


async def get_progress(
    db: AsyncSession,
    user_id: int,
) -> dict[str, any]:
    """Ermittelt den Onboarding-Fortschritt in Prozent und die Checkliste."""
    rows = await _get_or_create_progress_rows(db, user_id)

    # Dynamische Prüfung der Kern-Meilensteine.
    has_objekt = await _has_objekt(db, user_id)
    has_einheit = await _has_einheit(db, user_id)
    has_mieter = await _has_mieter(db, user_id)
    has_vertrag = await _has_vertrag(db, user_id)
    abo_active = await _abo_active(db, user_id)
    profile_complete = await _profile_complete(db, user_id)

    dynamic_state = {
        "profile_completed": profile_complete or rows["profile_completed"].is_done,
        "first_objekt": has_objekt or rows["first_objekt"].is_done,
        "first_einheit": has_einheit or rows["first_einheit"].is_done,
        "first_mieter": has_mieter or rows["first_mieter"].is_done,
        "first_vertrag": has_vertrag or rows["first_vertrag"].is_done,
        "abo_confirmed": abo_active or rows["abo_confirmed"].is_done,
    }

    steps = []
    done_count = 0
    for step, label in ONBOARDING_STEPS:
        is_done = bool(dynamic_state.get(step, False))
        if is_done:
            done_count += 1
            if not rows[step].is_done:
                rows[step].is_done = True
                rows[step].done_at = datetime.now(UTC)

        steps.append(
            {
                "step": step,
                "label": label,
                "is_done": is_done,
                "done_at": rows[step].done_at if is_done else None,
            }
        )

    percent = min(100, max(0, round((done_count / len(ONBOARDING_STEPS)) * 100)))
    return {"progress_percent": percent, "steps": steps}


async def update_step(
    db: AsyncSession,
    user_id: int,
    step: str,
) -> OnboardingProgress:
    """Markiert einen Onboarding-Schritt als erledigt."""
    if step not in [s for s, _ in ONBOARDING_STEPS]:
        raise ValueError(f"Ungültiger Onboarding-Schritt: {step}")

    rows = await _get_or_create_progress_rows(db, user_id)
    row = rows[step]
    if not row.is_done:
        row.is_done = True
        row.done_at = datetime.now(UTC)
        await db.flush()
    return row


# ── Hilfsfunktionen für dynamische Meilensteine ──


async def _has_objekt(db: AsyncSession, user_id: int) -> bool:
    count = await db.scalar(
        select(func.count(Objekt.id)).where(
            Objekt.vermieter_id == user_id,
            Objekt.deleted_at.is_(None),
        )
    )
    return bool(count and count > 0)


async def _has_einheit(db: AsyncSession, user_id: int) -> bool:
    count = await db.scalar(
        select(func.count(Einheit.id)).where(
            Einheit.vermieter_id == user_id,
            Einheit.deleted_at.is_(None),
        )
    )
    return bool(count and count > 0)


async def _has_mieter(db: AsyncSession, user_id: int) -> bool:
    count = await db.scalar(
        select(func.count(Mieter.id)).where(
            Mieter.vermieter_id == user_id,
            Mieter.deleted_at.is_(None),
        )
    )
    return bool(count and count > 0)


async def _has_vertrag(db: AsyncSession, user_id: int) -> bool:
    count = await db.scalar(
        select(func.count(Mietvertrag.id)).where(
            Mietvertrag.vermieter_id == user_id,
            Mietvertrag.deleted_at.is_(None),
        )
    )
    return bool(count and count > 0)


async def _abo_active(db: AsyncSession, user_id: int) -> bool:
    sub = await db.scalar(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    if sub is None:
        return False
    return sub.status in ("trial", "active")


async def _profile_complete(db: AsyncSession, user_id: int) -> bool:
    user = await db.get(User, user_id)
    if user is None:
        return False
    return bool(user.full_name and user.email and user.phone)
