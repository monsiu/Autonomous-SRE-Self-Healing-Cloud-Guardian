"""
Real-time metrics monitoring that triggers agent pipeline on threshold breaches
Optional enhancement to connect real AMD metrics to agent detection
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from utils.metrics_fetcher import fetch_real_metrics
from models.schemas import LogEntry

logger = logging.getLogger(__name__)

# Thresholds for triggering incidents
CPU_THRESHOLD = 60.0  # Trigger at 60% CPU (more sensitive)
RAM_THRESHOLD = 75.0  # Trigger at 75% RAM (more sensitive)
CHECK_INTERVAL = 5  # Check every 5 seconds

class MetricsMonitor:
    def __init__(self):
        self.running = False
        self.last_cpu_alert = 0
        self.last_ram_alert = 0
        self.alert_cooldown = 30  # Don't spam alerts (30 seconds between same type)
        
    async def start_monitoring(self):
        """Start continuous monitoring of real AMD metrics"""
        self.running = True
        logger.info("🔍 Starting real-time metrics monitoring...")
        logger.info(f"   CPU Threshold: {CPU_THRESHOLD}%")
        logger.info(f"   RAM Threshold: {RAM_THRESHOLD}%")
        logger.info(f"   Check Interval: {CHECK_INTERVAL}s")
        
        while self.running:
            try:
                await self._check_metrics()
            except Exception as e:
                logger.error(f"Error in metrics monitoring: {e}")
            
            await asyncio.sleep(CHECK_INTERVAL)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("⏹️  Stopped metrics monitoring")
    
    async def _check_metrics(self):
        """Check metrics and trigger agents if thresholds breached"""
        metrics = await fetch_real_metrics()
        
        if not metrics:
            return
        
        current_time = datetime.now().timestamp()
        cpu_load = metrics.get('cpu_load', 0)
        ram_usage = metrics.get('ram_usage_percent', 0)
        
        # Check CPU threshold
        if cpu_load > CPU_THRESHOLD:
            if current_time - self.last_cpu_alert > self.alert_cooldown:
                await self._trigger_cpu_alert(cpu_load, metrics)
                self.last_cpu_alert = current_time
        
        # Check RAM threshold
        if ram_usage > RAM_THRESHOLD:
            if current_time - self.last_ram_alert > self.alert_cooldown:
                await self._trigger_ram_alert(ram_usage, metrics)
                self.last_ram_alert = current_time
    
    async def _trigger_cpu_alert(self, cpu_load: float, metrics: dict):
        """Trigger agent pipeline for CPU threshold breach"""
        logger.warning(f"🚨 CPU threshold breached: {cpu_load}% (threshold: {CPU_THRESHOLD}%)")
        
        # Import here to avoid circular dependency
        from agents.agent_manager import run_monitor_agent
        
        log = LogEntry(
            timestamp=datetime.now().isoformat(),
            level="CRITICAL",
            service="AMD-Droplet",
            message=f"CPU usage critical: {cpu_load}% (threshold: {CPU_THRESHOLD}%)",
            source="real-metrics-monitor",
            metadata={
                "cpu_load": cpu_load,
                "ram_usage": metrics.get('ram_usage_percent', 0),
                "threshold_type": "cpu",
                "threshold_value": CPU_THRESHOLD,
                "breach_amount": cpu_load - CPU_THRESHOLD
            }
        )
        
        await run_monitor_agent(log)
    
    async def _trigger_ram_alert(self, ram_usage: float, metrics: dict):
        """Trigger agent pipeline for RAM threshold breach"""
        logger.warning(f"🚨 RAM threshold breached: {ram_usage}% (threshold: {RAM_THRESHOLD}%)")
        
        # Import here to avoid circular dependency
        from agents.agent_manager import run_monitor_agent
        
        log = LogEntry(
            timestamp=datetime.now().isoformat(),
            level="CRITICAL",
            service="AMD-Droplet",
            message=f"Memory usage critical: {ram_usage}% (threshold: {RAM_THRESHOLD}%)",
            source="real-metrics-monitor",
            metadata={
                "cpu_load": metrics.get('cpu_load', 0),
                "ram_usage": ram_usage,
                "threshold_type": "ram",
                "threshold_value": RAM_THRESHOLD,
                "breach_amount": ram_usage - RAM_THRESHOLD
            }
        )
        
        await run_monitor_agent(log)

# Global instance
metrics_monitor = MetricsMonitor()
