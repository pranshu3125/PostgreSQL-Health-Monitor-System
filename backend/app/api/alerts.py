from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.alert import Alert, AlertRule, AlertStatus
from app.schemas.alert import AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, AlertResponse, AlertUpdate
from app.core.security import get_current_user, require_role
from app.services.notifications import send_alert_notification

router = APIRouter()


@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(AlertRule).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@router.post("/rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    rule: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    db_rule = AlertRule(
        name=rule.name,
        description=rule.description,
        metric_name=rule.metric_name,
        condition=rule.condition,
        threshold=rule.threshold,
        severity=rule.severity,
        created_by=current_user.id
    )
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.patch("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_update: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    await db.delete(rule)
    await db.commit()
    return {"message": "Alert rule deleted"}


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[AlertStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Alert).offset(skip).limit(limit)
    if status:
        query = query.where(Alert.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert_update.status == AlertStatus.RESOLVED and alert.status != AlertStatus.RESOLVED:
        alert.resolved_at = datetime.utcnow()
    
    alert.status = alert_update.status
    await db.commit()
    await db.refresh(alert)
    
    if alert.status == AlertStatus.RESOLVED:
        await send_alert_notification(alert, "resolved")
    
    return alert


@router.get("/stats/summary")
async def get_alert_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_result = await db.execute(select(Alert))
    total = len(total_result.scalars().all())
    
    active_result = await db.execute(select(Alert).where(Alert.status == AlertStatus.ACTIVE))
    active = len(active_result.scalars().all())
    
    acknowledged_result = await db.execute(select(Alert).where(Alert.status == AlertStatus.ACKNOWLEDGED))
    acknowledged = len(acknowledged_result.scalars().all())
    
    resolved_result = await db.execute(select(Alert).where(Alert.status == AlertStatus.RESOLVED))
    resolved = len(resolved_result.scalars().all())
    
    return {
        "total": total,
        "active": active,
        "acknowledged": acknowledged,
        "resolved": resolved
    }
