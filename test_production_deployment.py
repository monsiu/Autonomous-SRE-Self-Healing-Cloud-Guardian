#!/usr/bin/env python3
"""
Production Deployment Test Script
Tests all components of the Autonomous SRE system
"""

import requests
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
DROPLET_IP = "165.245.140.125"
DROPLET_PORT = 9100

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    print(f"{BLUE}ℹ{RESET} {text}")

def test_amd_droplet():
    """Test connection to AMD droplet"""
    print_header("Testing AMD Droplet Connection")
    
    try:
        url = f"http://{DROPLET_IP}:{DROPLET_PORT}/metrics"
        print_info(f"Connecting to: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print_success(f"Connected to AMD droplet successfully")
            
            # Parse some metrics
            lines = response.text.split('\n')
            for line in lines[:20]:
                if 'node_memory_MemTotal_bytes' in line and not line.startswith('#'):
                    total_bytes = float(line.split()[-1])
                    total_gb = total_bytes / (1024**3)
                    print_info(f"  Total RAM: {total_gb:.2f} GB")
                elif 'node_memory_MemAvailable_bytes' in line and not line.startswith('#'):
                    avail_bytes = float(line.split()[-1])
                    avail_gb = avail_bytes / (1024**3)
                    print_info(f"  Available RAM: {avail_gb:.2f} GB")
            
            return True
        else:
            print_error(f"Failed to connect: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Connection timeout - droplet not responding")
        return False
    except requests.exceptions.ConnectionError:
        print_error("Connection refused - check droplet IP and port")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_backend_health():
    """Test backend health endpoint"""
    print_header("Testing Backend API")
    
    try:
        # Test root endpoint
        print_info("Testing root endpoint...")
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            print_success("Root endpoint responding")
            print_info(f"  Response: {response.json()}")
        else:
            print_error(f"Root endpoint failed: HTTP {response.status_code}")
            return False
        
        # Test API docs
        print_info("Testing API documentation...")
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success("API documentation available at /docs")
        else:
            print_warning("API docs not available")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Backend not running - start with: cd backend && python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_incident_trigger():
    """Test incident trigger endpoint"""
    print_header("Testing Incident Trigger")
    
    try:
        print_info("Triggering DDoS incident...")
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/api/incidents/trigger",
            json={"incident_type": "ddos"},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Incident triggered successfully")
            print_info(f"  Response: {response.json()}")
            
            print_info("Waiting for agent pipeline to complete (5 seconds)...")
            time.sleep(5)
            
            return True
        else:
            print_error(f"Failed to trigger incident: HTTP {response.status_code}")
            print_error(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error triggering incident: {e}")
        return False

def test_incident_history():
    """Test incident history endpoint"""
    print_header("Testing Incident History")
    
    try:
        print_info("Fetching incident history...")
        
        response = requests.get(f"{BACKEND_URL}/api/v1/api/incidents/history", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            incidents = data.get('incidents', [])
            
            print_success(f"Retrieved incident history: {total} total incidents")
            
            if incidents:
                print_info(f"  Last 5 incidents:")
                for inc in incidents[:5]:
                    print_info(f"    - {inc.get('type', 'unknown')} ({inc.get('severity', 'unknown')}) at {inc.get('timestamp', 'unknown')}")
            
            return True
        else:
            print_error(f"Failed to fetch history: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error fetching history: {e}")
        return False

def test_remediation_history():
    """Test remediation history endpoint"""
    print_header("Testing Remediation History")
    
    try:
        print_info("Fetching remediation history...")
        
        response = requests.get(f"{BACKEND_URL}/api/v1/api/incidents/remediations", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            remediations = data.get('remediations', [])
            
            print_success(f"Retrieved remediation history: {total} total PDFs")
            
            if remediations:
                print_info(f"  Last 5 remediations:")
                for rem in remediations[:5]:
                    print_info(f"    - {rem.get('filename', 'unknown')}")
            
            return True
        else:
            print_error(f"Failed to fetch remediations: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error fetching remediations: {e}")
        return False

def test_frontend():
    """Test frontend availability"""
    print_header("Testing Frontend Dashboard")
    
    try:
        print_info("Checking frontend at http://localhost:5173...")
        
        response = requests.get("http://localhost:5173", timeout=5)
        
        if response.status_code == 200:
            print_success("Frontend is running")
            print_info("  Dashboard available at: http://localhost:5173")
            return True
        else:
            print_error(f"Frontend returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_warning("Frontend not running - start with: cd frontend && npm run dev")
        return False
    except Exception as e:
        print_error(f"Error checking frontend: {e}")
        return False

def main():
    """Run all tests"""
    print_header("🛡️  Autonomous SRE - Production Deployment Test")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "AMD Droplet": test_amd_droplet(),
        "Backend API": test_backend_health(),
        "Incident Trigger": test_incident_trigger(),
        "Incident History": test_incident_history(),
        "Remediation History": test_remediation_history(),
        "Frontend Dashboard": test_frontend(),
    }
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}✓ All tests passed ({passed}/{total}){RESET}")
        print(f"{GREEN}🚀 System is PRODUCTION READY!{RESET}")
        sys.exit(0)
    else:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed{RESET}")
        print(f"{YELLOW}Some components need attention{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
