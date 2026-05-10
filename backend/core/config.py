import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # API Configuration
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Aegis - SRE - Guardian")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # Server Configuration
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Frontend URL (for CORS)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # AMD Droplet Configuration
    AMD_DROPLET_IP: Optional[str] = os.getenv("AMD_DROPLET_IP")
    AMD_DROPLET_PORT: int = int(os.getenv("AMD_DROPLET_PORT", "9100"))
    AMD_SSH_USER: str = os.getenv("AMD_SSH_USER", "root")
    AMD_SSH_KEY_PATH: Optional[str] = os.getenv("AMD_SSH_KEY_PATH")
    AMD_SSH_KEY_PASSPHRASE: Optional[str] = os.getenv("AMD_SSH_KEY_PASSPHRASE")
    AMD_SSH_PASSWORD: Optional[str] = os.getenv("AMD_SSH_PASSWORD")
    
    @property
    def PROMETHEUS_URL(self) -> str:
        """Construct Prometheus URL from droplet IP and port"""
        if self.AMD_DROPLET_IP and self.AMD_DROPLET_IP != "YOUR_DROPLET_IP_HERE":
            return f"http://{self.AMD_DROPLET_IP}:{self.AMD_DROPLET_PORT}/metrics"
        return ""
    
    # Monitoring Thresholds
    CPU_THRESHOLD_PERCENT: float = float(os.getenv("CPU_THRESHOLD_PERCENT", "70.0"))
    RAM_THRESHOLD_PERCENT: float = float(os.getenv("RAM_THRESHOLD_PERCENT", "85.0"))
    METRICS_CHECK_INTERVAL: int = int(os.getenv("METRICS_CHECK_INTERVAL", "5"))
    
    # Vector Store Configuration
    VECTORSTORE_DIR: str = os.getenv("VECTORSTORE_DIR", "./vectorstore")
    VECTOR_DB_COLLECTION: str = os.getenv("VECTOR_DB_COLLECTION", "incidents")
    
    # LLM Configuration
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "llama-3.1-8b")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Post-mortem Configuration
    POSTMORTEM_DIR: str = os.getenv("POSTMORTEM_DIR", "./post_mortems")
    POSTMORTEM_TEMPLATE: str = os.getenv("POSTMORTEM_TEMPLATE", "default")
    
    # Agent Configuration
    ENABLE_REAL_METRICS_MONITORING: bool = os.getenv("ENABLE_REAL_METRICS_MONITORING", "false").lower() == "true"
    ALERT_COOLDOWN_SECONDS: int = int(os.getenv("ALERT_COOLDOWN_SECONDS", "30"))

settings = Settings()
