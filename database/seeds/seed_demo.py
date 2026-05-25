"""Seed demo accounts so the platform is usable immediately after first boot.

Run from the repo root:
    PYTHONPATH=. python database/seeds/seed_demo.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make backend + ai_engine importable when run from repo root
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.core.security import hash_password  # noqa: E402
from app.db import init_db  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


DEMO_USERS = [
    ("admin@careerforge.ai", "Admin@12345", "Admin User", UserRole.ADMIN),
    ("recruiter@careerforge.ai", "Recruit@12345", "Demo Recruiter", UserRole.RECRUITER),
    ("candidate@careerforge.ai", "Candi@12345", "Demo Candidate", UserRole.USER),
]


async def main() -> None:
    await init_db()
    for email, password, name, role in DEMO_USERS:
        existing = await User.find_one(User.email == email)
        if existing:
            print(f"[skip] {email} already exists")
            continue
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=name,
            role=role,
        )
        await user.insert()
        print(f"[ok]   {email} (role={role.value})")


if __name__ == "__main__":
    asyncio.run(main())
