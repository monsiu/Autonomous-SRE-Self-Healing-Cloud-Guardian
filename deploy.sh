#!/bin/bash

# Aegis SRE Guardian - Deployment Helper Script
# This script helps prepare your application for deployment

set -e

echo "🚀 Aegis SRE Guardian - Deployment Helper"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if required files exist
echo "📋 Checking required files..."

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    exit 1
fi
print_success "requirements.txt found"

if [ ! -f "frontend/package.json" ]; then
    print_error "frontend/package.json not found!"
    exit 1
fi
print_success "frontend/package.json found"

if [ ! -f "railway.toml" ]; then
    print_warning "railway.toml not found - creating it..."
    cat > railway.toml << 'EOF'
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
EOF
    print_success "railway.toml created"
fi

if [ ! -f "frontend/vercel.json" ]; then
    print_warning "frontend/vercel.json not found - creating it..."
    cat > frontend/vercel.json << 'EOF'
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
EOF
    print_success "frontend/vercel.json created"
fi

echo ""
echo "🔍 Checking environment files..."

if [ ! -f "backend/.env" ]; then
    print_warning "backend/.env not found"
    if [ -f "backend/.env.example" ]; then
        echo "   Copy backend/.env.example to backend/.env and configure it"
    fi
else
    print_success "backend/.env found"
fi

if [ ! -f "frontend/.env" ]; then
    print_warning "frontend/.env not found"
    if [ -f "frontend/.env.example" ]; then
        echo "   Copy frontend/.env.example to frontend/.env and configure it"
    fi
else
    print_success "frontend/.env found"
fi

echo ""
echo "📦 Testing local build..."

# Test backend dependencies
echo "Testing Python dependencies..."
if command -v python3 &> /dev/null; then
    python3 -c "import fastapi, uvicorn, paramiko" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Backend dependencies OK"
    else
        print_warning "Some backend dependencies missing - run: pip install -r requirements.txt"
    fi
else
    print_warning "Python3 not found - install Python 3.11+"
fi

# Test frontend dependencies
echo "Testing Node.js setup..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    print_success "Node.js $NODE_VERSION found"
    
    if [ -d "frontend/node_modules" ]; then
        print_success "Frontend dependencies installed"
    else
        print_warning "Frontend dependencies not installed - run: cd frontend && npm install"
    fi
else
    print_warning "Node.js not found - install Node.js 18+"
fi

echo ""
echo "🔐 Security checklist..."

# Check if .env files are in .gitignore
if grep -q "\.env" .gitignore 2>/dev/null; then
    print_success ".env files are in .gitignore"
else
    print_warning ".env files should be added to .gitignore"
fi

# Check for sensitive data in git
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git ls-files | grep -q "\.env$"; then
        print_error ".env files are tracked by git! Remove them with: git rm --cached backend/.env frontend/.env"
    else
        print_success "No .env files tracked by git"
    fi
fi

echo ""
echo "📝 Deployment URLs to configure:"
echo "================================"
echo ""
echo "1. Deploy backend to Railway:"
echo "   → Go to https://railway.app"
echo "   → Create new project from GitHub"
echo "   → Note your Railway URL: https://YOUR-APP.up.railway.app"
echo ""
echo "2. Deploy frontend to Vercel:"
echo "   → Go to https://vercel.com"
echo "   → Import GitHub repository"
echo "   → Set root directory to: frontend"
echo "   → Note your Vercel URL: https://YOUR-APP.vercel.app"
echo ""
echo "3. Update environment variables:"
echo "   Railway (Backend):"
echo "   - FRONTEND_URL=https://YOUR-APP.vercel.app"
echo "   - AMD_DROPLET_IP=your.droplet.ip"
echo "   - AMD_SSH_USER=root"
echo "   - AMD_SSH_PASSWORD=your_password"
echo ""
echo "   Vercel (Frontend):"
echo "   - VITE_API_BASE_URL=https://YOUR-APP.up.railway.app"
echo "   - VITE_API_V1_URL=https://YOUR-APP.up.railway.app/api/v1"
echo "   - VITE_WS_LOGS_URL=wss://YOUR-APP.up.railway.app/api/v1/logs"
echo "   - VITE_WS_AGENTS_URL=wss://YOUR-APP.up.railway.app/api/v1/agents"
echo ""
echo "4. Update CORS in backend/main.py:"
echo "   Add your Vercel domain to allow_origins list"
echo ""
echo "✅ Pre-deployment checks complete!"
echo ""
echo "📖 For detailed instructions, see: DEPLOYMENT_GUIDE.md"
echo ""
