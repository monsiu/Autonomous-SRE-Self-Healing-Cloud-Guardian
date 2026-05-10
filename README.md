# 🛡️ Aegis - SRE Guardian

An intelligent, autonomous incident response system that monitors infrastructure in real-time, diagnoses issues using AI agents, and executes automated remediation actions via SSH on remote servers.

## Live Demo

Try the deployed demo: [Autonomous SRE Self-Healing Cloud Guardian](https://autonomous-sre-self-healing-cloud-g.vercel.app/)

## Hackathon Submission

Built for the **AMD Developer Hackathon** under **Track 1: AI Agents & Agentic Workflows**.

### Problem

Cloud incidents often require engineers to manually inspect metrics, identify root causes, decide on remediation steps, and document what happened. This project turns that workflow into an autonomous SRE assistant that can monitor infrastructure, reason through incidents, execute controlled fixes, and generate post-mortem reports.

### Solution

Aegis combines real-time infrastructure monitoring with a three-agent AI pipeline:

1. **Monitor Agent** detects abnormal system behavior from live metrics.
2. **Diagnosis Agent** analyzes the incident and compares it with historical patterns.
3. **Remediation Agent** executes safe, predefined recovery actions over SSH.

The result is an end-to-end self-healing cloud operations dashboard for detecting, diagnosing, and responding to incidents.

### AMD Developer Cloud Fit

The system is designed around cloud-hosted AMD infrastructure, using an AMD droplet as the monitored target environment. It demonstrates how AMD cloud compute can support real operational AI workloads beyond model demos, including live observability, autonomous agents, and infrastructure remediation.

### Judging Highlights

- **Application of Technology** - Multi-agent incident response system with real metrics, WebSockets, SSH remediation, vector memory, and automated reporting.
- **Business Value** - Reduces manual SRE effort, shortens incident response time, and creates consistent post-mortem documentation.
- **Originality** - Applies AI agents to autonomous cloud reliability and self-healing infrastructure workflows.
- **Completeness** - Includes a deployed frontend demo, backend API, test incident triggers, remediation flow, and local setup instructions.

## ✨ Features

- **Real-time Monitoring** - Live metrics from AMD droplet via Prometheus node_exporter
- **Autonomous Diagnosis** - Three-agent AI pipeline detects, analyzes, and resolves incidents
- **SSH Remediation** - Executes actual fixes on remote infrastructure with secure authentication
- **Live Dashboard** - Modern React frontend with real-time WebSocket updates
- **Post-Mortem Reports** - Automated PDF generation with incident analysis and remediation logs
- **Vector Store** - Historical incident database for pattern recognition and learning
- **Health Scoring** - Real-time system health metrics and scoring
- **Incident Timeline** - Visual timeline of all incidents and remediation actions

## Architecture

```
Monitor Agent → Diagnosis Agent → Remediation Agent
     ↓               ↓                    ↓
  Detect         Analyze              Execute
  Anomaly        Root Cause           SSH Commands
```

### Agent Pipeline

1. **Monitor Agent** - Watches logs and metrics, detects anomalies
2. **Diagnosis Agent** - Queries incident history, identifies root cause
3. **Remediation Agent** - Executes SSH commands to fix issues

## Tech Stack

**Backend**
- Python 3.11+ with FastAPI
- WebSockets for real-time bidirectional communication
- Paramiko for secure SSH connections
- ReportLab for automated PDF post-mortem generation
- ChromaDB for vector storage and incident similarity search
- Pydantic for data validation and schemas

**Frontend**
- React 18 + TypeScript
- Vite for fast development and builds
- Tailwind CSS for modern styling
- Recharts for data visualizations
- Custom WebSocket hooks for real-time updates

## Quick Start

### 1. Setup AMD Droplet

SSH to your droplet and install node_exporter:

```bash
cd /tmp && \
wget -q https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz && \
tar xzf node_exporter-1.7.0.linux-amd64.tar.gz && \
sudo cp node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/ && \
sudo chmod +x /usr/local/bin/node_exporter && \
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<'EOF'
[Unit]
Description=Prometheus Node Exporter
After=network.target
[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/node_exporter
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && \
sudo systemctl start node_exporter && \
sudo systemctl enable node_exporter
```

Verify: `curl http://localhost:9100/metrics | head -n 20`

### 2. Configure Connection

**Option A: SSH Tunnel (Recommended)**
```bash
# Keep this running in a terminal
ssh -L 9100:localhost:9100 root@YOUR_DROPLET_IP
```

Edit `backend/.env`:
```bash
AMD_DROPLET_IP="localhost"
AMD_SSH_USER="root"
AMD_SSH_KEY_PATH="/path/to/your/ssh/key"
```

**Option B: Direct Connection**
```bash
# Edit backend/.env
AMD_DROPLET_IP="YOUR_DROPLET_IP"
AMD_SSH_USER="root"
AMD_SSH_KEY_PATH="/path/to/your/ssh/key"
```

### 3. Install Dependencies

```bash
# Backend (Python 3.11+ required)
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

**Backend Dependencies:**
- fastapi - Web framework
- uvicorn - ASGI server
- websockets - Real-time communication
- paramiko - SSH client
- reportlab - PDF generation
- chromadb - Vector database
- pydantic - Data validation
- python-dotenv - Environment management

### 4. Launch

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open http://localhost:5173

### 5. Test Real Remediation

```bash
# Trigger CPU incident on droplet
python trigger_real_incident.py cpu

# Watch CPU spike in dashboard
# Click "Remediate" to execute SSH fix
```

## 🔌 API Endpoints

### REST Endpoints
- `GET /` - Health check and API info
- `GET /api/v1/health` - Detailed system status
- `POST /api/v1/incidents/trigger` - Manually trigger incident simulation
- `POST /api/v1/incidents/remediate` - Execute remediation for incident
- `GET /api/v1/incidents/metrics` - Fetch current droplet metrics
- `GET /api/v1/incidents/history` - Get incident history

### WebSocket Endpoints
- `WS /api/v1/logs` - Real-time log stream (system logs, agent actions)
- `WS /api/v1/agents` - Agent state updates (thinking, diagnosing, remediating)

## 🚨 Incident Types

The system can detect and remediate the following incident types:

- **cpu_surge** - High CPU utilization, resource exhaustion, runaway processes
- **memory_pressure** - High RAM usage, memory leaks, OOM conditions
- **disk_io** - High disk I/O, slow read/write operations
- **ddos** - High traffic, rate limit breaches, network flooding
- **db_bottleneck** - Query timeouts, connection pool exhaustion
- **normal** - Healthy operation baseline

Each incident type has predefined remediation strategies executed via SSH.

## Project Structure

```
backend/
├── agents/          # Agent orchestration
├── api/endpoints/   # FastAPI routes
├── core/            # Configuration
├── ml/              # Diagnosis & remediation logic
├── models/          # Pydantic schemas
├── utils/           # Logging, metrics, monitoring
└── main.py          # FastAPI app

frontend/
├── src/
│   ├── components/  # React components
│   ├── hooks/       # WebSocket hooks
│   └── types/       # TypeScript types
└── package.json
```

## How It Works

### Monitoring
- Backend polls node_exporter every 3 seconds
- Metrics streamed to frontend via WebSocket
- Anomalies trigger agent pipeline

### Diagnosis
- Vector store searches similar incidents
- Agent analyzes patterns and root cause
- Confidence scores guide remediation

### Remediation
- SSH connection to droplet
- Executes predefined safe commands
- Logs all actions and results
- Generates PDF post-mortem

### Security
- SSH key authentication (password fallback)
- Command whitelist (no user input)
- All operations logged
- Graceful degradation if SSH fails

## Configuration

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
# AMD Droplet
AMD_DROPLET_IP="your.droplet.ip"
AMD_SSH_USER="root"
AMD_SSH_KEY_PATH="/path/to/ssh/key"
AMD_SSH_PASSWORD="fallback_password"  # Optional

# API
API_V1_STR="/api/v1"
PROJECT_NAME="Autonomous SRE"
```

## 🧪 Testing

```bash
# Test droplet connection and metrics
python test_amd_connection.py

# Test production deployment readiness
python test_production_deployment.py

# Trigger test incidents on droplet
python trigger_real_incident.py cpu      # CPU surge
python trigger_real_incident.py memory   # Memory pressure
python trigger_real_incident.py disk     # Disk I/O

# Test agent pipeline
cd backend
python test_agents.py
```

## Troubleshooting

**Can't connect to droplet metrics:**
- Verify node_exporter is running: `systemctl status node_exporter`
- Check SSH tunnel is active
- Test manually: `curl http://localhost:9100/metrics`

**SSH remediation fails:**
- Verify SSH key path in `.env`
- Test SSH manually: `ssh -i /path/to/key root@droplet`
- Check logs in `backend/utils/logger.py`

**WebSocket connection issues:**
- Restart backend server
- Clear browser cache
- Check CORS settings in `backend/main.py`

## 📚 Documentation

- `backend/ml/README.md` - ML components and agent pipeline overview
- Post-mortem PDFs generated in `backend/post_mortems/`
- Vector store data in `backend/vectorstore/incidents.json`

## 🔐 Security Considerations

- SSH key authentication preferred over passwords
- Command whitelist prevents arbitrary command execution
- All SSH operations are logged
- Environment variables for sensitive credentials
- CORS configured for frontend-backend communication
- No user input directly passed to shell commands

## 🎯 Use Cases

- **DevOps Automation** - Reduce manual intervention in incident response
- **SRE Training** - Learn incident patterns and remediation strategies
- **Infrastructure Monitoring** - Real-time visibility into system health
- **Post-Mortem Analysis** - Automated documentation of incidents
- **Capacity Planning** - Historical data for resource optimization

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional incident types and remediation strategies
- Enhanced ML models for diagnosis
- Multi-server support
- Alert integrations (PagerDuty, Slack, etc.)
- Advanced metrics visualization

## 📝 License

MIT

## 🏆 Acknowledgments

Built for AMD Developer Hackathon 2025

---

**Note:** This system executes real commands on production infrastructure. Always test in a safe environment first and review remediation actions before deploying to critical systems.
