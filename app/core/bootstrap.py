import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.database import SessionLocal
from app.models.role import Role
from app.models.user import User

logger = logging.getLogger("car_rental.bootstrap")


def ensure_admin_exists() -> None:
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing is not None:
            logger.info("Bootstrap admin already exists: %s", settings.ADMIN_EMAIL)
            return

        role = db.query(Role).filter(Role.name == "admin").first()
        if role is None:
            logger.error("Role 'admin' not found. Apply migrations/seed first.")
            return

        admin = User(
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            full_name=settings.ADMIN_FULL_NAME,
            phone=None,
            role_id=role.id,
        )
        db.add(admin)
        db.commit()
        logger.info("Bootstrap admin created: %s", settings.ADMIN_EMAIL)
    except Exception:
        db.rollback()
        logger.exception("Failed to create bootstrap admin")
    finally:
        db.close()