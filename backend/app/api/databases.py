from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import asyncpg

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.database import DatabaseConnection
from app.schemas.database import DatabaseCreate, DatabaseUpdate, DatabaseResponse, DatabaseTestResult
from app.core.security import get_current_user, require_role

router = APIRouter()


@router.get("", response_model=List[DatabaseResponse])
async def list_databases(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(DatabaseConnection).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{db_id}", response_model=DatabaseResponse)
async def get_database(
    db_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(DatabaseConnection).where(DatabaseConnection.id == db_id)
    )
    database = result.scalar_one_or_none()
    if not database:
        raise HTTPException(status_code=404, detail="Database not found")
    return database


@router.post("", response_model=DatabaseResponse)
async def create_database(
    database: DatabaseCreate,
    db_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    db_connection = DatabaseConnection(
        name=database.name,
        host=database.host,
        port=database.port,
        database=database.database,
        username=database.username,
        password=database.password,
        description=database.description,
        created_by=current_user.id
    )
    db_session.add(db_connection)
    await db_session.commit()
    await db_session.refresh(db_connection)
    return db_connection


@router.patch("/{db_id}", response_model=DatabaseResponse)
async def update_database(
    db_id: int,
    database_update: DatabaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    result = await db.execute(
        select(DatabaseConnection).where(DatabaseConnection.id == db_id)
    )
    database = result.scalar_one_or_none()
    if not database:
        raise HTTPException(status_code=404, detail="Database not found")
    
    update_data = database_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(database, field, value)
    
    await db.commit()
    await db.refresh(database)
    return database


@router.delete("/{db_id}")
async def delete_database(
    db_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    result = await db.execute(
        select(DatabaseConnection).where(DatabaseConnection.id == db_id)
    )
    database = result.scalar_one_or_none()
    if not database:
        raise HTTPException(status_code=404, detail="Database not found")
    
    await db.delete(database)
    await db.commit()
    return {"message": "Database connection deleted"}


@router.post("/test", response_model=DatabaseTestResult)
async def test_database_connection(
    database: DatabaseCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        conn = await asyncpg.connect(
            host=database.host,
            port=database.port,
            user=database.username,
            password=database.password,
            database=database.database,
            timeout=10
        )
        version = await conn.server_version()
        await conn.close()
        return DatabaseTestResult(
            success=True,
            message="Connection successful",
            version=f"{version[0]}.{version[1]}.{version[2]}"
        )
    except Exception as e:
        return DatabaseTestResult(
            success=False,
            message=f"Connection failed: {str(e)}"
        )
