import logging
import asyncio
from datetime import datetime
from api.endpoints.agents_ws import notify_agent_state
from models.schemas import LogEntry, IncidentDiagnosis
from ml.vector_store import vector_store
from ml.llm_engine import llm_engine
from ml.remediation import remediation_engine

logger = logging.getLogger(__name__)

# Seed sample incidents on startup
try:
    vector_store.seed_sample_incidents()
except Exception as e:
    logger.warning(f"Could not seed incidents: {e}")

async def run_monitor_agent(log: LogEntry):
    """
    Monitor Agent: Watches logs and detects anomalies
    Triggers diagnosis pipeline when thresholds breach
    """
    # Store log in vector database
    log_id = f"log_{datetime.now().timestamp()}"
    log_text = f"{log.level} {log.service} {log.message}"
    
    try:
        vector_store.add_log(
            log_id=log_id,
            log_text=log_text,
            metadata=log.dict()
        )
    except Exception as e:
        logger.error(f"Error storing log: {e}")
    
    # Anomaly detection based on log level and patterns
    if log.level in ["ERROR", "CRITICAL"]:
        await notify_agent_state(
            agent_name="Monitor Agent",
            status="alert",
            message=f"🚨 Anomaly detected! Log Level: {log.level}",
            details={
                "log_service": log.service,
                "reason": log.message,
                "source": log.source,
                "threshold_breached": True
            }
        )
        await run_diagnosis_agent(log)

async def run_diagnosis_agent(anomaly_log: LogEntry):
    """
    Diagnosis Agent: Queries ChromaDB, cross-references runbooks,
    uses LLM to reason over context and output structured diagnosis
    """
    await notify_agent_state(
        agent_name="Diagnosis Agent",
        status="thinking",
        message="🔍 Querying ChromaDB for similar past incidents...",
        details={"anomaly_source": anomaly_log.source}
    )
    
    await asyncio.sleep(1)
    
    # Query similar incidents from vector store
    query_text = f"{anomaly_log.level} {anomaly_log.service} {anomaly_log.message}"
    similar_incidents = vector_store.query_similar_incidents(query_text, n_results=5)
    
    await notify_agent_state(
        agent_name="Diagnosis Agent",
        status="thinking",
        message=f"📊 Found {len(similar_incidents)} similar incidents. Analyzing with LLM...",
        details={
            "similar_count": len(similar_incidents),
            "similar_incidents": [
                {
                    "id": inc.get("id", "unknown"),
                    "type": inc.get("metadata", {}).get("incident_type", "unknown"),
                    "severity": inc.get("metadata", {}).get("severity", "unknown"),
                    "match_score": round(inc.get("score", 0), 3),
                    "description": inc.get("text", "")[:100]
                }
                for inc in similar_incidents[:5]  # Top 5 with more details
            ],
            "query": query_text[:100]
        }
    )
    
    await asyncio.sleep(1)
    
    # Use LLM to diagnose (currently rule-based fallback)
    diagnosis_result = llm_engine.diagnose_incident(
        anomaly_log=anomaly_log.dict(),
        similar_incidents=similar_incidents,
        runbook_context="SRE Runbooks v2.1"
    )
    
    diagnosis = IncidentDiagnosis(
        incident_type=diagnosis_result["incident_type"],
        severity=diagnosis_result["severity"],
        confidence=diagnosis_result["confidence"],
        action=diagnosis_result["action"],
        reasoning=diagnosis_result["reasoning"]
    )
    
    await notify_agent_state(
        agent_name="Diagnosis Agent",
        status="resolved",
        message=f"✅ Incident diagnosed: {diagnosis.incident_type}",
        details={
            "incident_type": diagnosis.incident_type,
            "confidence": diagnosis.confidence,
            "severity": diagnosis.severity,
            "suggested_action": diagnosis.action,
            "reasoning": diagnosis.reasoning,
            "similar_incidents_analyzed": len(similar_incidents),
            "diagnosis_method": "Rule-based pattern matching + similarity search",
            "confidence_breakdown": {
                "pattern_match": round(diagnosis.confidence * 0.6, 2),
                "similarity_score": round(diagnosis.confidence * 0.4, 2),
                "final_confidence": diagnosis.confidence
            },
            "top_similar_incidents": [
                {
                    "type": inc.get("metadata", {}).get("incident_type", "unknown"),
                    "match_score": round(inc.get("score", 0), 3)
                }
                for inc in similar_incidents[:3]
            ]
        }
    )
    
    # Store diagnosed incident in vector store
    incident_id = f"inc_{datetime.now().timestamp()}"
    incident_text = f"{diagnosis.incident_type} {diagnosis.severity} {diagnosis.reasoning}"
    try:
        vector_store.add_incident(
            incident_id=incident_id,
            incident_text=incident_text,
            metadata={
                "incident_type": diagnosis.incident_type,
                "severity": diagnosis.severity,
                "confidence": diagnosis.confidence,
                "action": diagnosis.action,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error storing incident: {e}")
    
    # Trigger remediation
    await run_remediation_agent(diagnosis, anomaly_log)

async def run_remediation_agent(diagnosis: IncidentDiagnosis, original_log: LogEntry):
    """
    Remediation Agent: Selects and executes remediation script,
    generates post-mortem PDF report
    """
    await notify_agent_state(
        agent_name="Remediation Agent",
        status="acting",
        message=f"⚡ Executing remediation: {diagnosis.action}",
        details={
            "target": diagnosis.incident_type,
            "action": diagnosis.action
        }
    )
    
    # Prepare incident data for remediation
    incident_data = {
        "incident_type": diagnosis.incident_type,
        "severity": diagnosis.severity,
        "confidence": diagnosis.confidence,
        "action": diagnosis.action,
        "reasoning": diagnosis.reasoning,
        "timestamp": original_log.timestamp,
        "service": original_log.service,
        "source": original_log.source,
        "message": original_log.message,
        "metadata": original_log.metadata
    }
    
    # Execute remediation
    result = await remediation_engine.execute_remediation(
        action=diagnosis.action,
        incident_data=incident_data
    )
    
    await notify_agent_state(
        agent_name="Remediation Agent",
        status="completed",
        message=f"✅ Remediation completed: {result['action_taken']}",
        details={
            "status": result["status"],
            "action_taken": result["action_taken"],
            "details": result.get("details", {}),
            "post_mortem": result.get("post_mortem_url", "")
        }
    )
    
    logger.info(f"Full agent pipeline completed for {diagnosis.incident_type}")
