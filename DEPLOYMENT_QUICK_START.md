# ⚡ Quick Start Deployment Guide

## 🎯 TL;DR

1. **Backend → Railway** (Python FastAPI)
2. **Frontend → Vercel** (React + Vite)
3. **Connect them** with environment variables

---

## 🚀 Step-by-Step (15 minutes)

### 1️⃣ Deploy Backend to Railway (5 min)

```bash
# 1. Go to https://railway.app
# 2. Click "New Project" → "Deploy from GitHub repo"
# 3. Select your repository
# 4. Add these environment variables:

PROJECT_NAME=Aegis SRE Guardian
API_V1_STR=/api/v1
BACKEND_HOST=0.0.0.0
FRONTEND_URL=https://YOUR-APP.vercel.app  # Update after Vercel deployment

# AMD Droplet
AMD_DROPLET_IP=your.droplet.ip.address
AMD_DROPLET_PORT=9100
AMD_SSH_USER=root
AMD_SSH_PASSWORD=your_ssh_password

# Monitoring
ENABLE_REAL_METRICS_MONITORING=true
CPU_THRESHOLD_PERCENT=70.0
RAM_THRESHOLD_PERCENT=85.0

# 5. Deploy! Note your Railway URL: https://YOUR-APP.up.railway.app
```

### 2️⃣ Deploy Frontend to Vercel (5 min)

```bash
# 1. Go to https://vercel.com
# 2. Click "Add New Project" → Import from GitHub
# 3. Configure:
#    - Root Directory: frontend
#    - Framework: Vite
# 4. Add these environment variables:

VITE_API_BASE_URL=https://YOUR-APP.up.railway.app
VITE_API_V1_URL=https://YOUR-APP.up.railway.app/api/v1
VITE_WS_LOGS_URL=wss://YOUR-APP.up.railway.app/api/v1/logs
VITE_WS_AGENTS_URL=wss://YOUR-APP.up.railway.app/api/v1/agents
VITE_ENABLE_REAL_METRICS=true

# 5. Deploy! Note your Vercel URL: https://YOUR-APP.vercel.app
```

### 3️⃣ Connect Them (5 min)

**Update Railway environment:**
```bash
FRONTEND_URL=https://YOUR-APP.vercel.app
```

**Update backend/main.py CORS:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://YOUR-APP.vercel.app",  # Add this
        "https://*.vercel.app",          # Add this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push** - both will auto-redeploy!

---

## ✅ Verify Deployment

### Test Backend
```bash
curl https://YOUR-APP.up.railway.app/api/v1/health
```

### Test Frontend
Open `https://YOUR-APP.vercel.app` in browser

### Test Full Flow
1. Visit your Vercel URL
2. Check if "Connected" shows in UI
3. Click "Trigger Incident" → "CPU Surge"
4. Watch agents work in real-time!

---

## 🔧 Common Issues

### ❌ WebSocket won't connect
- Use `wss://` not `ws://` in production
- Check CORS settings include Vercel domain
- Verify Railway app is running

### ❌ CORS errors
- Add Vercel domain to `backend/main.py` CORS origins
- Set `FRONTEND_URL` in Railway environment
- Redeploy backend

### ❌ SSH remediation fails
- Verify `AMD_SSH_PASSWORD` in Railway
- Check droplet allows SSH connections
- Test: `ssh root@your.droplet.ip`

### ❌ Metrics not loading
- Verify node_exporter running on droplet: `systemctl status node_exporter`
- Check port 9100 is accessible
- Test: `curl http://your.droplet.ip:9100/metrics`

---

## 📋 Environment Variables Checklist

### Railway (Backend) - Required
- [ ] `AMD_DROPLET_IP`
- [ ] `AMD_SSH_USER`
- [ ] `AMD_SSH_PASSWORD`
- [ ] `FRONTEND_URL`
- [ ] `ENABLE_REAL_METRICS_MONITORING=true`

### Vercel (Frontend) - Required
- [ ] `VITE_API_BASE_URL`
- [ ] `VITE_API_V1_URL`
- [ ] `VITE_WS_LOGS_URL`
- [ ] `VITE_WS_AGENTS_URL`

---

## 💰 Cost

- **Railway**: $5-20/month
- **Vercel**: Free (Hobby) or $20/month (Pro)
- **AMD Droplet**: $5-10/month

**Total**: ~$10-50/month

---

## 📚 Full Documentation

See `DEPLOYMENT_GUIDE.md` for:
- Detailed step-by-step instructions
- SSH key configuration
- Security best practices
- Troubleshooting guide
- Monitoring setup

---

## 🆘 Need Help?

1. Check Railway logs: Dashboard → Deployments → Logs
2. Check Vercel logs: Dashboard → Deployments → Function Logs
3. Check browser console for frontend errors
4. Review `DEPLOYMENT_GUIDE.md` troubleshooting section

---

**You're all set!** 🎉

Frontend: `https://YOUR-APP.vercel.app`
Backend: `https://YOUR-APP.up.railway.app`
API Docs: `https://YOUR-APP.up.railway.app/docs`
