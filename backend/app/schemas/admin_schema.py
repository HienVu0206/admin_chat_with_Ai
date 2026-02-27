from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from datetime import datetime
from typing import Optional, List

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str

class ChangeRoleRequest(BaseModel):
    new_role_id: int

# Schema trả về một dòng lịch sử Log
class AuditLogResponse(BaseModel):
    id: int
    admin_name: str
    action: str
    target_id: Optional[int]
    details: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)

# Schema hiển thị User trong danh sách quản trị
class UserAdminResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    status: str
    role_id: int
    role_name: str # Trả về tên role để FE hiển thị text
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Schema tạo/sửa Role
class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str]