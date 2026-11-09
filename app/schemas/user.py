from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    phone: str | None
    role: str
    created_at: datetime

    @field_validator("role", mode="before")
    @classmethod
    def role_to_str(cls, v):
        return v.name if hasattr(v, "name") else v