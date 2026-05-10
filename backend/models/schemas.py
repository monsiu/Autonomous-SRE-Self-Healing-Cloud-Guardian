from pydantic import BaseModel
from typing import Optional, Dict, Any

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    source: str
    service: str
    warning: str
    state: str
    metadata: Optional[Dict[str, Any]] = None

class IncidentDiagnosis(BaseModel):
    incident_type: str
    severity: str
    confidence: float
    action: str
    reasoning: str

class RemediationAction(BaseModel):
    incident_id: str
    action_taken: str
    status: str
    post_mortem_url: Optional[str] = None
