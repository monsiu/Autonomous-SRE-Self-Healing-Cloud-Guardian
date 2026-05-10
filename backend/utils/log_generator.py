import asyncio
import random
from datetime import datetime
from faker import Faker
from models.schemas import LogEntry
from utils.metrics_fetcher import fetch_real_metrics

fake = Faker()
current_anomaly_state = "normal"

def set_anomaly_state(state: str):
    global current_anomaly_state
    current_anomaly_state = state

def generate_normal_log() -> LogEntry:
    levels = ["INFO", "INFO", "INFO", "WARN", "DEBUG"]
    services = ["api-gateway", "auth-service", "user-service", "payment-service", "db-cluster"]
    states = ["active", "idle", "processing"]
    
    return LogEntry(
        timestamp=datetime.now().isoformat() + "Z",
        level=random.choice(levels),
        message=fake.sentence(nb_words=6),
        source=fake.ipv4(),
        service=random.choice(services),
        warning="",
        state=random.choice(states),
        metadata={"latency_ms": random.randint(10, 150)}
    )

def generate_ddos_log() -> LogEntry:
    attacker_ip = "192.168.1.100"  # Malicious IP address (Fake, for development)
    requests_per_sec = random.randint(8000, 15000)
    return LogEntry(
        timestamp=datetime.now().isoformat() + "Z",
        level="ERROR",
        message=f"ATTACK DETECTED: {requests_per_sec} req/s from {attacker_ip}",
        source=attacker_ip,
        service="api-gateway",
        warning="DDoS Attack in Progress",
        state="under_attack",
        metadata={
            "requests_per_sec": requests_per_sec,
            "bandwidth_mbps": random.randint(500, 1200),
            "connections_active": random.randint(5000, 12000),
            "legitimate_traffic_impact": f"{random.randint(60, 95)}% degraded"
        }
    )

def generate_cpu_surge_log() -> LogEntry:
    # Generate more dramatic CPU spikes
    cpu_usage = random.randint(92, 99)
    return LogEntry(
        timestamp=datetime.now().isoformat() + "Z",
        level="CRITICAL",
        message=f"CRITICAL: CPU usage at {cpu_usage}% - System under extreme load!",
        source="host-node-01",
        service="worker-service",
        warning="Resource Exhaustion - Immediate Action Required",
        state="critical",
        metadata={
            "cpu_usage": cpu_usage,
            "load_average": round(random.uniform(8.5, 15.0), 2),
            "processes_blocked": random.randint(15, 45),
            "response_time_ms": random.randint(3000, 8000)
        }
    )

def generate_db_bottleneck_log() -> LogEntry:
    latency = random.randint(8000, 18000)
    return LogEntry(
        timestamp=datetime.now().isoformat() + "Z",
        level="ERROR",
        message=f"DATABASE CRITICAL: Query timeout at {latency}ms - Connection pool exhausted",
        source="db-cluster-master",
        service="db-cluster",
        warning="Severe Database Performance Degradation",
        state="critical",
        metadata={
            "query_latency_ms": latency,
            "connection_pool_usage": f"{random.randint(95, 100)}%",
            "slow_queries": random.randint(45, 120),
            "deadlocks_detected": random.randint(3, 15),
            "cache_hit_rate": f"{random.randint(15, 35)}%"
        }
    )

async def generate_real_metrics_log() -> LogEntry:
    metrics = await fetch_real_metrics()
    if metrics:
        return LogEntry(
            timestamp=datetime.now().isoformat() + "Z",
            level="INFO",
            message=f"Live Metrics: CPU {metrics['cpu_load']}%, RAM {metrics['ram_usage_percent']}%",
            source="159.223.129.19",
            service="amd-node",
            warning="",
            state="monitoring",
            metadata=metrics
        )
    return generate_normal_log()

async def log_stream_generator():
    global current_anomaly_state    
    while True:
        if current_anomaly_state == "ddos":
            log = generate_ddos_log()
            await asyncio.sleep(0.05)  # Faster generation during DDoS
        elif current_anomaly_state == "cpu_surge":
            log = generate_cpu_surge_log() if random.random() > 0.3 else generate_normal_log()
            await asyncio.sleep(0.3)  # More frequent CPU surge logs
        elif current_anomaly_state == "db_bottleneck":
            log = generate_db_bottleneck_log() if random.random() > 0.2 else generate_normal_log()
            await asyncio.sleep(0.5)  # More frequent DB bottleneck logs
        else:
            log = await generate_real_metrics_log()
            await asyncio.sleep(2.0)  
        yield log