from sqlalchemy import func, select

from app.core.security import hash_password
from app.db.models import User, UserRole
from app.db.session import SessionLocal


DEMO_USERS = (
    {
        "name": "Profesor Demo",
        "email": "prof@demo.com",
        "password": "prof123",
        "role": UserRole.TEACHER,
    },
    {
        "name": "Estudiante Demo",
        "email": "est@demo.com",
        "password": "est123",
        "role": UserRole.STUDENT,
    },
)


def seed_demo_users() -> None:
    with SessionLocal() as db:
        for item in DEMO_USERS:
            exists = db.scalar(
                select(User).where(func.lower(User.email) == item["email"])
            )
            if exists:
                continue
            db.add(
                User(
                    name=item["name"],
                    email=item["email"],
                    password_hash=hash_password(item["password"]),
                    role=item["role"],
                )
            )
        db.commit()


if __name__ == "__main__":
    seed_demo_users()
