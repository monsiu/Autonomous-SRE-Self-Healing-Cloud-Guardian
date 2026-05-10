from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.log_generator import set_anomaly_state
from utils.metrics_fetcher import fetch_real_metrics
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

class IncidentRequest(BaseModel):
    incident_type: str 

async def _stress_droplet(incident_type: str):
    """Actually stress the droplet based on incident type"""
    try:
        import paramiko
        from core.config import settings
        import os
        
        if not settings.AMD_DROPLET_IP or settings.AMD_DROPLET_IP == "YOUR_DROPLET_IP_HERE":
            logger.warning("AMD_DROPLET_IP not configured - incident will only affect logs, not real metrics")
            return False
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to droplet
        if settings.AMD_SSH_KEY_PATH and os.path.exists(settings.AMD_SSH_KEY_PATH):
            ssh.connect(
                hostname=settings.AMD_DROPLET_IP,
                username=settings.AMD_SSH_USER,
                key_filename=settings.AMD_SSH_KEY_PATH,
                passphrase=settings.AMD_SSH_KEY_PASSPHRASE if hasattr(settings, 'AMD_SSH_KEY_PASSPHRASE') and settings.AMD_SSH_KEY_PASSPHRASE else None,
                timeout=10
            )
        elif settings.AMD_SSH_PASSWORD:
            ssh.connect(
                hostname=settings.AMD_DROPLET_IP,
                username=settings.AMD_SSH_USER,
                password=settings.AMD_SSH_PASSWORD,
                timeout=10
            )
        else:
            logger.error("No SSH credentials configured")
            return False
        
        # Choose stress command based on incident type
        if incident_type == "cpu_surge":
            # Stress CPU with 4 workers
            command = "nohup stress-ng --cpu 4 --timeout 300s > /dev/null 2>&1 &"
            logger.info("Starting CPU stress on droplet (4 workers, 5 min timeout)")
        elif incident_type == "db_bottleneck":
            # Stress CPU and I/O
            command = "nohup stress-ng --cpu 2 --io 2 --timeout 300s > /dev/null 2>&1 &"
            logger.info("Starting CPU+I/O stress on droplet (2+2 workers, 5 min timeout)")
        elif incident_type == "ddos":
            # Stress CPU and network
            command = "nohup stress-ng --cpu 3 --timeout 300s > /dev/null 2>&1 &"
            logger.info("Starting CPU stress on droplet (3 workers, 5 min timeout)")
        else:
            logger.info(f"No stress command for incident type: {incident_type}")
            ssh.close()
            return False
        
        # Execute stress command
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        
        ssh.close()
        
        if exit_code == 0:
            logger.info(f"✅ Successfully started stress on droplet for {incident_type}")
            return True
        else:
            logger.error(f"Failed to start stress: {stderr.read().decode()}")
            return False
            
    except ImportError:
        logger.warning("paramiko not installed - cannot stress droplet")
        return False
    except Exception as e:
        logger.error(f"Error stressing droplet: {e}")
        return False

@router.post("/trigger")
async def trigger_incident(request: IncidentRequest):
    valid_states = ["normal", "ddos", "cpu_surge", "db_bottleneck"]
    if request.incident_type not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid incident type. Must be one of: {valid_states}")
    
    # Set log generation state
    set_anomaly_state(request.incident_type)
    logger.info(f"Incident state changed to: {request.incident_type}")
    
    # Actually stress the droplet
    if request.incident_type != "normal":
        stress_result = await _stress_droplet(request.incident_type)
        if stress_result:
            return {
                "message": f"Incident triggered successfully - droplet is now under stress",
                "current_state": request.incident_type,
                "droplet_stressed": True
            }
        else:
            return {
                "message": f"Incident triggered (logs only - droplet stress failed)",
                "current_state": request.incident_type,
                "droplet_stressed": False
            }
    
    return {"message": f"Incident triggered successfully", "current_state": request.incident_type}

async def _kill_stress_on_droplet():
    """Kill stress processes on the droplet"""
    try:
        import paramiko
        from core.config import settings
        import os
        
        if not settings.AMD_DROPLET_IP or settings.AMD_DROPLET_IP == "YOUR_DROPLET_IP_HERE":
            logger.warning("AMD_DROPLET_IP not configured - cannot kill stress processes")
            return False
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to droplet
        if settings.AMD_SSH_KEY_PATH and os.path.exists(settings.AMD_SSH_KEY_PATH):
            ssh.connect(
                hostname=settings.AMD_DROPLET_IP,
                username=settings.AMD_SSH_USER,
                key_filename=settings.AMD_SSH_KEY_PATH,
                passphrase=settings.AMD_SSH_KEY_PASSPHRASE if hasattr(settings, 'AMD_SSH_KEY_PASSPHRASE') and settings.AMD_SSH_KEY_PASSPHRASE else None,
                timeout=10
            )
        elif settings.AMD_SSH_PASSWORD:
            ssh.connect(
                hostname=settings.AMD_DROPLET_IP,
                username=settings.AMD_SSH_USER,
                password=settings.AMD_SSH_PASSWORD,
                timeout=10
            )
        else:
            logger.error("No SSH credentials configured")
            return False
        
        # Kill all stress processes
        command = "pkill -9 stress-ng || pkill -9 stress || true"
        logger.info("Killing stress processes on droplet")
        
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        
        ssh.close()
        
        logger.info(f"✅ Stress processes killed on droplet (exit code: {exit_code})")
        return True
            
    except ImportError:
        logger.warning("paramiko not installed - cannot kill stress processes")
        return False
    except Exception as e:
        logger.error(f"Error killing stress processes: {e}")
        return False

@router.post("/stop")
async def stop_incident():
    """Stop the incident without remediation - just stops generating anomalous logs"""
    set_anomaly_state("normal")
    
    # Also kill stress processes on droplet
    killed = await _kill_stress_on_droplet()
    
    logger.info("Incident stopped. Returned to normal state (no remediation applied).")
    return {
        "message": "Incident stopped - system returned to normal log generation",
        "stress_killed": killed
    }

@router.post("/remediate")
async def remediate_incident():
    """Remediate the system - stops incident AND applies fixes"""
    set_anomaly_state("normal")
    
    # Kill stress processes on droplet
    killed = await _kill_stress_on_droplet()
    
    logger.info("System remediated. Returned to normal state with remediation applied.")
    return {
        "message": "System remediated - fixes applied and returned to normal state",
        "stress_killed": killed
    }

@router.get("/history")
async def get_incident_history():
    """Get incident history from vector store"""
    from ml.vector_store import vector_store
    
    # Get last 20 incidents
    incidents = vector_store.incidents[-20:] if len(vector_store.incidents) > 0 else []
    
    return {
        "total": len(vector_store.incidents),
        "incidents": [
            {
                "id": inc["id"],
                "type": inc["metadata"].get("incident_type", "unknown"),
                "severity": inc["metadata"].get("severity", "unknown"),
                "timestamp": inc.get("timestamp", ""),
                "action": inc["metadata"].get("action", ""),
                "description": inc["text"][:100]
            }
            for inc in reversed(incidents)
        ]
    }

@router.get("/remediations")
async def get_remediation_history():
    """Get list of generated post-mortem PDFs"""
    import os
    import glob
    from datetime import datetime
    
    pdf_dir = "./post_mortems"
    if not os.path.exists(pdf_dir):
        return {"total": 0, "remediations": []}
    
    pdfs = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    
    remediations = []
    for pdf_path in sorted(pdfs, reverse=True)[:20]:  # Last 20
        filename = os.path.basename(pdf_path)
        # Parse filename: postmortem_TYPE_TIMESTAMP.pdf
        parts = filename.replace(".pdf", "").split("_")
        if len(parts) >= 3:
            incident_type = "_".join(parts[1:-2]) if len(parts) > 3 else parts[1]
            timestamp_str = "_".join(parts[-2:])
            
            remediations.append({
                "filename": filename,
                "incident_type": incident_type,
                "timestamp": timestamp_str,
                "path": pdf_path
            })
    
    return {
        "total": len(pdfs),
        "remediations": remediations
    }

@router.get("/metrics")
async def get_real_metrics():
    """Get real-time metrics from AMD droplet"""
    metrics = await fetch_real_metrics()
    
    if metrics is None:
        return {
            "available": False,
            "message": "AMD Droplet not configured. Set AMD_DROPLET_IP in .env",
            "metrics": {
                "cpu_load": 0,
                "ram_usage_percent": 0
            }
        }
    
    return {
        "available": True,
        "metrics": metrics
    }

@router.get("/logs")
async def get_stored_logs():
    """Get stored logs from vector store"""
    from ml.vector_store import vector_store
    
    # Get last 100 logs
    logs = vector_store.logs[-100:] if len(vector_store.logs) > 0 else []
    
    return {
        "total": len(vector_store.logs),
        "logs": [
            {
                "id": log["id"],
                "timestamp": log["metadata"].get("timestamp", ""),
                "level": log["metadata"].get("level", "INFO"),
                "service": log["metadata"].get("service", "unknown"),
                "message": log["text"],
                "source": log["metadata"].get("source", ""),
                "anomaly": log["metadata"].get("anomaly", False)
            }
            for log in reversed(logs)
        ]
    }
