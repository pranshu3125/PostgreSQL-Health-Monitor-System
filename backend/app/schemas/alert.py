from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.alert import AlertSeverity, AlertStatus


class AlertRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    metric_name: str
    condition: str
    threshold: float
    severity: AlertSeverity = AlertSeverity.MEDIUM


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metric_name: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    severity: Optional[AlertSeverity] = None
    is_active: Optional[bool] = None


class AlertRuleResponse(AlertRuleBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    rule_id: Optional[int] = None
    metric_name: str
    metric_value: float
    threshold: float
    severity: AlertSeverity = AlertSeverity.MEDIUM
    message: Optional[str] = None


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None


class AlertResponse(AlertBase):
    id: int
    status: AlertStatus
    triggered_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
