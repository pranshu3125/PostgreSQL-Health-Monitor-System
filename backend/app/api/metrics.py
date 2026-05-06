from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta
import httpx
import asyncio

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter()


@router.get("/current")
async def get_current_metrics(
    current_user: User = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.PUSHGATEWAY_URL}/metrics")
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.text,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            pass
    
    return {
        "status": "no_data",
        "message": "No metrics available",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/query")
async def query_metrics(
    metric: str,
    current_user: User = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.PUSHGATEWAY_URL}/api/v1/query",
                params={"metric": metric}
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/labels/{label_name}")
async def get_metric_labels(
    label_name: str,
    current_user: User = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.PUSHGATEWAY_URL}/labels/{label_name}")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}


@router.get("/groups")
async def get_metric_groups(
    current_user: User = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.PUSHGATEWAY_URL}/api/v1/group")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}


@router.delete("/groups/{group}")
async def delete_metric_group(
    group: str,
    current_user: User = Depends(get_current_user)
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{settings.PUSHGATEWAY_URL}/api/v1/group/{group}")
            return {"status": "success", "message": f"Group {group} deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


METRICS_INFO = {
    "postgres_db_idle_connection": "Number of idle connections in PostgreSQL",
    "postgres_db_name_sizes": "Size of each database in the PostgreSQL instance",
    "postgres_top_db_inuse": "Most active databases in use",
    "postgres_db_query_latency": "Latency of specific queries",
    "postgres_connections_per_db": "Number of connections per database"
}


@router.get("/definitions")
async def get_metrics_definitions(
    current_user: User = Depends(get_current_user)
):
    return {
        "metrics": METRICS_INFO,
        "timestamp": datetime.utcnow().isoformat()
    }
