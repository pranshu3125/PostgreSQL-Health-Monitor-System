from pydantic import BaseModel
from typing import Optional


class DatabaseBase(BaseModel):
    name: str
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    description: Optional[str] = None


class DatabaseCreate(DatabaseBase):
    pass


class DatabaseUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DatabaseResponse(DatabaseBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class DatabaseTestResult(BaseModel):
    success: bool
    message: str
    version: Optional[str] = None
