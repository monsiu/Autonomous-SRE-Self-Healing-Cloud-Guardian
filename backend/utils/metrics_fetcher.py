import httpx
import logging
from typing import Dict, Optional
from core.config import settings

logger = logging.getLogger(__name__)

last_cpu_idle = 0.0
last_cpu_total = 0.0

async def fetch_real_metrics() -> Optional[Dict[str, float]]:
    global last_cpu_idle, last_cpu_total
    
    # Check if Prometheus URL is configured
    if not settings.PROMETHEUS_URL:
        logger.warning("AMD Droplet IP not configured. Set AMD_DROPLET_IP in .env file")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(settings.PROMETHEUS_URL)
            response.raise_for_status()
            lines = response.text.splitlines()
            
            mem_total = 0.0
            mem_avail = 0.0
            
            current_idle = 0.0
            current_total = 0.0
            
            for line in lines:
                if line.startswith("node_memory_MemTotal_bytes "):
                    mem_total = float(line.split()[1])
                elif line.startswith("node_memory_MemAvailable_bytes "):
                    mem_avail = float(line.split()[1])
                elif line.startswith("node_cpu_seconds_total{"):
                    parts = line.split()
                    val = float(parts[1])
                    current_total += val
                    if 'mode="idle"' in parts[0]:
                        current_idle += val
            
            ram_usage_percent = 0.0
            if mem_total > 0:
                ram_usage_percent = ((mem_total - mem_avail) / mem_total) * 100.0
                
            cpu_usage_percent = 0.0
            if last_cpu_total > 0:
                delta_idle = current_idle - last_cpu_idle
                delta_total = current_total - last_cpu_total
                if delta_total > 0:
                    cpu_usage_percent = (1.0 - (delta_idle / delta_total)) * 100.0
                    cpu_usage_percent = max(0.0, cpu_usage_percent)
                    
            last_cpu_idle = current_idle
            last_cpu_total = current_total
                
            return {
                "cpu_load": round(cpu_usage_percent, 2),
                "ram_usage_percent": round(ram_usage_percent, 2)
            }
    except Exception as e:
        logger.error(f"Failed to fetch real metrics: {e}")
        return None
