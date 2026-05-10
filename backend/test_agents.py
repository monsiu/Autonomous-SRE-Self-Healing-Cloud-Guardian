"""
Test script to verify agent pipeline works
"""
import asyncio
from models.schemas import LogEntry
from agents.agent_manager import run_monitor_agent

async def test_agent_pipeline():
    print("Testing Agent Pipeline...")
    print("=" * 50)
    
    # Test 1: DDoS Attack
    print("\n1. Testing DDoS Attack Detection")
    ddos_log = LogEntry(
        timestamp="2025-05-10T10:30:00Z",
        level="ERROR",
        message="Rate limit exceeded. Too many requests.",
        source="192.168.1.100",
        service="api-gateway",
        warning="High Traffic Volume",
        state="blocked",
        metadata={"requests_per_sec": 8000}
    )
    await run_monitor_agent(ddos_log)
    await asyncio.sleep(2)
    
    # Test 2: CPU Surge
    print("\n2. Testing CPU Surge Detection")
    cpu_log = LogEntry(
        timestamp="2025-05-10T10:35:00Z",
        level="CRITICAL",
        message="CPU usage exceeds 95% threshold",
        source="host-node-01",
        service="worker-service",
        warning="Resource Exhaustion",
        state="throttling",
        metadata={"cpu_usage": 98}
    )
    await run_monitor_agent(cpu_log)
    await asyncio.sleep(2)
    
    # Test 3: DB Bottleneck
    print("\n3. Testing DB Bottleneck Detection")
    db_log = LogEntry(
        timestamp="2025-05-10T10:40:00Z",
        level="ERROR",
        message="Database query timeout. Connection pool exhausted.",
        source="db-cluster-master",
        service="db-cluster",
        warning="Query Latency Spike",
        state="degraded",
        metadata={"query_latency_ms": 8000}
    )
    await run_monitor_agent(db_log)
    await asyncio.sleep(2)
    
    print("\n" + "=" * 50)
    print("Agent Pipeline Test Complete!")
    print("Check ./post_mortems/ for generated PDF reports")

if __name__ == "__main__":
    asyncio.run(test_agent_pipeline())
