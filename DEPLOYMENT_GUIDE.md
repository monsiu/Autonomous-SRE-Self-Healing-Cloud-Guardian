# 🚀 Deployment Guide: Aegis SRE Guardian

Complete guide to deploy the frontend on **Vercel** and backend on **Railway**.

---

## 📋 Prerequisites

- GitHub account (for connecting to Vercel and Railway)
- AMD droplet with SSH access
- SSH key for droplet authentication
- Node.js 18+ (for local testing)
- Python 3.11+ (for local testing)

---

## 🎯 Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Vercel    │ ◄─────► │   Railway    │ ◄─────► │ AMD Droplet │
│  (Frontend) │  HTTPS  │  (Backend)   │   SSH   │  (Metrics)  │
│   React     │   WSS   │   FastAPI    │         │node_exporter│
└─────────────┘         └──────────────┘         └─────────────┘
```

---

## Part 1: Backend Deployment (Railway)

### Step 1: Prepare Backend for Railway

#### 1.1 Create Railway Configuration Files

Create `railway.toml` in project root:

```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

#### 1.2 Create Procfile (Alternative)

Create `Procfile` in project root:

```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 1.3 Update Backend CORS Settings

Edit `backend/main.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",  # Add your Vercel domain
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2: Deploy to Railway

#### 2.1 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway will auto-detect Python and start building

#### 2.2 Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
# API Configuration
PROJECT_NAME=Aegis - SRE Guardian
VERSION=1.0.0
API_V1_STR=/api/v1

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=$PORT
FRONTEND_URL=https://your-app.vercel.app

# AMD Droplet Configuration
AMD_DROPLET_IP=your.droplet.ip.address
AMD_DROPLET_PORT=9100

# SSH Configuration
AMD_SSH_USER=root
AMD_SSH_KEY_PATH=/app/ssh_key
AMD_SSH_PASSWORD=your_password_if_needed

# Monitoring
CPU_THRESHOLD_PERCENT=70.0
RAM_THRESHOLD_PERCENT=85.0
DISK_THRESHOLD_PERCENT=80.0
METRICS_CHECK_INTERVAL=5
ENABLE_REAL_METRICS_MONITORING=true
ALERT_COOLDOWN_SECONDS=30

# Vector Store
VECTORSTORE_DIR=./vectorstore
VECTOR_DB_COLLECTION=incidents
VECTOR_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Logging
LOG_LEVEL=INFO

# Post-mortem
POSTMORTEM_DIR=./post_mortems
POSTMORTEM_INCLUDE_METRICS=true
POSTMORTEM_INCLUDE_LOGS=true

# Agent Configuration
AGENT_TIMEOUT=60
AGENT_MAX_RETRIES=3
```

#### 2.3 Add SSH Key (Important!)

Railway doesn't support file uploads directly, so you have two options:

**Option A: Use SSH Password Authentication**
- Set `AMD_SSH_PASSWORD` in environment variables
- Less secure but simpler

**Option B: Base64 Encode SSH Key**

1. On your local machine:
```bash
# Encode your SSH key
cat ~/.ssh/id_rsa | base64 -w 0 > ssh_key_base64.txt
```

2. Add to Railway environment variables:
```bash
SSH_KEY_BASE64=<paste the base64 content>
```

3. Update `backend/ml/remediation.py` to decode the key:
```python
import base64
import os

# Add this function
def get_ssh_key():
    if os.getenv("SSH_KEY_BASE64"):
        key_content = base64.b64decode(os.getenv("SSH_KEY_BASE64"))
        key_path = "/tmp/ssh_key"
        with open(key_path, "wb") as f:
            f.write(key_content)
        os.chmod(key_path, 0o600)
        return key_path
    return os.getenv("AMD_SSH_KEY_PATH")
```

#### 2.4 Configure Networking

1. Railway automatically assigns a public URL
2. Note your Railway URL: `https://your-app.up.railway.app`
3. Ensure your AMD droplet allows incoming SSH from Railway's IP

### Step 3: Verify Backend Deployment

1. Visit `https://your-app.up.railway.app/`
2. Check health: `https://your-app.up.railway.app/api/v1/health`
3. Test metrics: `https://your-app.up.railway.app/api/v1/incidents/metrics`

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend for Vercel

#### 1.1 Create Vercel Configuration

Create `vercel.json` in `frontend/` directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

#### 1.2 Update Environment Variables Template

Create `frontend/.env.production`:

```bash
# Production Backend API (Railway)
VITE_API_BASE_URL=https://your-app.up.railway.app
VITE_API_V1_URL=https://your-app.up.railway.app/api/v1

# WebSocket URLs (use wss:// for secure WebSocket)
VITE_WS_LOGS_URL=wss://your-app.up.railway.app/api/v1/logs
VITE_WS_AGENTS_URL=wss://your-app.up.railway.app/api/v1/agents

# WebSocket Settings
VITE_WS_RECONNECT_INTERVAL=3000
VITE_WS_MAX_RECONNECT_ATTEMPTS=10

# Application
VITE_APP_NAME=Aegis - SRE Guardian
VITE_APP_VERSION=1.0.0
VITE_ENABLE_REAL_METRICS=true
VITE_ENABLE_NOTIFICATIONS=true

# Refresh Intervals
VITE_METRICS_REFRESH_INTERVAL=5000
VITE_HISTORY_REFRESH_INTERVAL=10000
VITE_HEALTH_CHECK_INTERVAL=30000

# UI Configuration
VITE_MAX_LOG_ENTRIES=100
VITE_MAX_TIMELINE_ITEMS=50
VITE_CHART_DATA_POINTS=20
```

### Step 2: Deploy to Vercel

#### 2.1 Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click **"Add New Project"**
4. Import your GitHub repository
5. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

#### 2.2 Configure Environment Variables

In Vercel project settings → **Environment Variables**, add all variables from `.env.production`:

```
VITE_API_BASE_URL = https://your-app.up.railway.app
VITE_API_V1_URL = https://your-app.up.railway.app/api/v1
VITE_WS_LOGS_URL = wss://your-app.up.railway.app/api/v1/logs
VITE_WS_AGENTS_URL = wss://your-app.up.railway.app/api/v1/agents
... (add all other VITE_ variables)
```

#### 2.3 Deploy

1. Click **"Deploy"**
2. Vercel will build and deploy automatically
3. Note your Vercel URL: `https://your-app.vercel.app`

### Step 3: Update Backend CORS

Go back to Railway and update `FRONTEND_URL`:

```bash
FRONTEND_URL=https://your-app.vercel.app
```

Also update `backend/main.py` CORS origins to include your Vercel domain.

---

## Part 3: AMD Droplet Setup

### Step 1: Install Node Exporter

SSH into your droplet and run:

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

### Step 2: Configure Firewall

Allow Railway to access node_exporter:

```bash
# Allow port 9100 (node_exporter)
sudo ufw allow 9100/tcp

# Allow SSH from Railway (if using SSH remediation)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### Step 3: Verify

```bash
# Check node_exporter status
sudo systemctl status node_exporter

# Test metrics endpoint
curl http://localhost:9100/metrics | head -n 20
```

---

## Part 4: Final Integration & Testing

### Step 1: Update All URLs

1. **Railway Backend**: Update `FRONTEND_URL` to your Vercel URL
2. **Vercel Frontend**: Update all `VITE_API_*` and `VITE_WS_*` to Railway URL
3. **Backend CORS**: Add Vercel domain to allowed origins

### Step 2: Test the Full Stack

#### 2.1 Test Backend Health

```bash
curl https://your-app.up.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-10T...",
  "droplet_connection": "connected"
}
```

#### 2.2 Test Frontend

1. Visit `https://your-app.vercel.app`
2. Check browser console for errors
3. Verify WebSocket connections (should show "Connected" in UI)
4. Check if metrics are loading

#### 2.3 Test End-to-End Incident Flow

1. Trigger an incident:
```bash
# From your local machine
curl -X POST https://your-app.up.railway.app/api/v1/incidents/trigger \
  -H "Content-Type: application/json" \
  -d '{"incident_type": "cpu_surge"}'
```

2. Watch the dashboard for:
   - Agent thinking animation
   - Log stream updates
   - Incident timeline entry
   - Remediation execution

---

## Part 5: Monitoring & Maintenance

### Railway Monitoring

1. **Logs**: Railway Dashboard → Deployments → View Logs
2. **Metrics**: Check CPU, Memory, Network usage
3. **Alerts**: Set up notifications for deployment failures

### Vercel Monitoring

1. **Analytics**: Vercel Dashboard → Analytics
2. **Logs**: Vercel Dashboard → Deployments → Function Logs
3. **Performance**: Check Core Web Vitals

### Custom Monitoring

Add health check endpoints to your monitoring service:

```bash
# Backend health
https://your-app.up.railway.app/api/v1/health

# Frontend (check if it loads)
https://your-app.vercel.app
```

---

## 🔧 Troubleshooting

### Issue: WebSocket Connection Failed

**Symptoms**: "Disconnected" status in UI, no real-time updates

**Solutions**:
1. Verify Railway URL uses `wss://` (not `ws://`)
2. Check CORS settings in backend
3. Ensure Railway deployment is running
4. Check browser console for specific errors

### Issue: SSH Remediation Fails

**Symptoms**: "Remediation failed" errors in logs

**Solutions**:
1. Verify SSH credentials in Railway environment variables
2. Check if droplet allows SSH from Railway's IP
3. Test SSH connection manually from Railway:
```bash
# In Railway's terminal
ssh -i /tmp/ssh_key root@your.droplet.ip
```

### Issue: Metrics Not Loading

**Symptoms**: Dashboard shows "No data" or loading forever

**Solutions**:
1. Verify node_exporter is running on droplet
2. Check if port 9100 is accessible
3. Test metrics endpoint directly:
```bash
curl http://your.droplet.ip:9100/metrics
```

### Issue: CORS Errors

**Symptoms**: Browser console shows CORS policy errors

**Solutions**:
1. Add Vercel domain to backend CORS origins
2. Ensure `allow_credentials=True` in CORS middleware
3. Redeploy backend after CORS changes

### Issue: Build Failures

**Railway Build Fails**:
- Check `requirements.txt` for invalid packages
- Verify Python version compatibility
- Check Railway build logs for specific errors

**Vercel Build Fails**:
- Verify `package.json` dependencies
- Check if `frontend/` is set as root directory
- Ensure all environment variables are set

---

## 📊 Cost Estimates

### Railway (Backend)
- **Hobby Plan**: $5/month (500 hours)
- **Pro Plan**: $20/month (unlimited)
- Recommended: Pro Plan for production

### Vercel (Frontend)
- **Hobby Plan**: Free (personal projects)
- **Pro Plan**: $20/month (commercial use)
- Recommended: Hobby for testing, Pro for production

### AMD Droplet
- Varies by provider and specs
- Minimum: 1 vCPU, 1GB RAM (~$5-10/month)

**Total Estimated Cost**: $25-50/month

---

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **SSH Keys**: Use key authentication, not passwords
3. **Firewall**: Restrict droplet access to necessary IPs only
4. **HTTPS**: Always use HTTPS/WSS in production
5. **Secrets**: Rotate SSH keys and passwords regularly
6. **Monitoring**: Set up alerts for suspicious activity
7. **Backups**: Regular backups of vector store and post-mortems

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Test application locally
- [ ] Update all environment variables
- [ ] Configure SSH access to droplet
- [ ] Install node_exporter on droplet
- [ ] Update CORS settings

### Railway Deployment
- [ ] Create Railway project
- [ ] Configure environment variables
- [ ] Add SSH key (base64 encoded)
- [ ] Deploy and verify health endpoint
- [ ] Test metrics endpoint
- [ ] Check logs for errors

### Vercel Deployment
- [ ] Create Vercel project
- [ ] Set root directory to `frontend`
- [ ] Configure environment variables
- [ ] Deploy and verify site loads
- [ ] Test WebSocket connections
- [ ] Check browser console for errors

### Post-Deployment
- [ ] Update backend CORS with Vercel URL
- [ ] Test end-to-end incident flow
- [ ] Verify SSH remediation works
- [ ] Set up monitoring and alerts
- [ ] Document custom configurations
- [ ] Share URLs with team

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [WebSocket over HTTPS](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

---

## 🆘 Support

If you encounter issues:

1. Check Railway and Vercel logs
2. Review this guide's troubleshooting section
3. Test each component independently
4. Verify all environment variables are set correctly

---

**Deployment Complete!** 🎉

Your Aegis SRE Guardian is now live:
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-app.up.railway.app`
- API Docs: `https://your-app.up.railway.app/docs`
