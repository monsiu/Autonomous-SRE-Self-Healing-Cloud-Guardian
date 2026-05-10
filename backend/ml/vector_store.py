import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class SimpleVectorStore:
    """
    Simplified vector store using in-memory storage
    For production, replace with ChromaDB when C++ build tools are available
    """
    def __init__(self, persist_directory: str = "./vectorstore"):
        self.persist_directory = persist_directory
        self.incidents = []
        self.logs = []
        os.makedirs(persist_directory, exist_ok=True)
        self.load_from_disk()
        logger.info("SimpleVectorStore initialized")
    
    def add_log(self, log_id: str, log_text: str, metadata: Dict):
        try:
            self.logs.append({
                "id": log_id,
                "text": log_text,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            })
            # Keep only last 1000 logs in memory
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]
        except Exception as e:
            logger.error(f"Error adding log: {e}")

    
    def add_incident(self, incident_id: str, incident_text: str, metadata: Dict):
        try:
            self.incidents.append({
                "id": incident_id,
                "text": incident_text,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            })
            self.save_to_disk()
            logger.info(f"Added incident {incident_id} to vector store")
        except Exception as e:
            logger.error(f"Error adding incident: {e}")
    
    def query_similar_incidents(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Simple keyword-based similarity search
        For production, replace with semantic embeddings
        """
        try:
            query_lower = query_text.lower()
            scored_incidents = []
            
            for incident in self.incidents:
                # Simple keyword matching score
                text_lower = incident["text"].lower()
                score = sum(1 for word in query_lower.split() if word in text_lower)
                
                if score > 0:
                    scored_incidents.append({
                        'document': incident["text"],
                        'metadata': incident["metadata"],
                        'score': score
                    })
            
            # Sort by score and return top n
            scored_incidents.sort(key=lambda x: x['score'], reverse=True)
            return scored_incidents[:n_results]
        except Exception as e:
            logger.error(f"Error querying incidents: {e}")
            return []
    
    def save_to_disk(self):
        try:
            filepath = os.path.join(self.persist_directory, "incidents.json")
            with open(filepath, 'w') as f:
                json.dump(self.incidents, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving to disk: {e}")
    
    def load_from_disk(self):
        try:
            filepath = os.path.join(self.persist_directory, "incidents.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.incidents = json.load(f)
                logger.info(f"Loaded {len(self.incidents)} incidents from disk")
        except Exception as e:
            logger.error(f"Error loading from disk: {e}")
    
    def seed_sample_incidents(self):
        sample_incidents = [
            {
                "id": "inc_001",
                "text": "DDoS attack detected from IP range 192.168.1.0/24. Rate limit exceeded with 8000 requests per second. Blocked malicious IPs and normalized traffic.",
                "metadata": {
                    "incident_type": "ddos",
                    "severity": "high",
                    "action_taken": "block_ip_range",
                    "resolution_time_sec": 45,
                    "timestamp": "2024-04-15T10:30:00Z"
                }
            },
            {
                "id": "inc_002",
                "text": "CPU usage exceeded 95% threshold on worker-service. Resource exhaustion detected. Scaled up container instances from 3 to 6.",
                "metadata": {
                    "incident_type": "cpu_surge",
                    "severity": "critical",
                    "action_taken": "scale_up_containers",
                    "resolution_time_sec": 120,
                    "timestamp": "2024-04-16T14:20:00Z"
                }
            },
            {
                "id": "inc_003",
                "text": "Database query timeout. Connection pool exhausted with latency spike to 8000ms. Optimized slow queries and cleared cache.",
                "metadata": {
                    "incident_type": "db_bottleneck",
                    "severity": "high",
                    "action_taken": "optimize_queries_clear_cache",
                    "resolution_time_sec": 180,
                    "timestamp": "2024-04-17T09:15:00Z"
                }
            },
            {
                "id": "inc_004",
                "text": "High traffic volume from single IP 10.0.0.50. Rate limit breach with 6500 req/sec. Applied rate limiting and blocked source.",
                "metadata": {
                    "incident_type": "ddos",
                    "severity": "medium",
                    "action_taken": "block_ip_range",
                    "resolution_time_sec": 30,
                    "timestamp": "2024-04-18T16:45:00Z"
                }
            },
            {
                "id": "inc_005",
                "text": "CPU throttling on host-node-01 at 98% usage. Worker service degraded performance. Auto-scaled horizontally and load balanced.",
                "metadata": {
                    "incident_type": "cpu_surge",
                    "severity": "critical",
                    "action_taken": "scale_up_containers",
                    "resolution_time_sec": 90,
                    "timestamp": "2024-04-19T11:30:00Z"
                }
            }
        ]
        
        for incident in sample_incidents:
            try:
                self.add_incident(
                    incident_id=incident["id"],
                    incident_text=incident["text"],
                    metadata=incident["metadata"]
                )
            except Exception as e:
                logger.warning(f"Could not seed incident {incident['id']}: {e}")
        
        logger.info(f"Seeded {len(sample_incidents)} sample incidents")

vector_store = SimpleVectorStore()
