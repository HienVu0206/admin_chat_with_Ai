from pydantic import BaseModel, ConfigDict
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: int

class RoleUpdateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool
    # Bật tính năng này để Pydantic tự động map dữ liệu từ SQLAlchemy Object sang JSON
    model_config = ConfigDict(from_attributes=True)