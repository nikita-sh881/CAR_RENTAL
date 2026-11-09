from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    items, total = UserRepository(db).list(offset=(page - 1) * page_size, limit=page_size)
    return {
        "items": [UserOut.model_validate(u) for u in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }