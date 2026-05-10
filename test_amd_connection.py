#!/usr/bin/env python3
"""
Quick test script to verify AMD droplet connectivity, metrics, and SSH access
"""
import httpx
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

AMD_DROPLET_IP = os.getenv('AMD_DROPLET_IP', '165.245.140.125')
AMD_DROPLET_PORT = os.getenv('AMD_DROPLET_PORT', '9100')
AMD_SSH_USER = os.getenv('AMD_SSH_USER', 'root')
AMD_SSH_KEY_PATH = os.getenv('AMD_SSH_KEY_PATH')
AMD_SSH_KEY_PASSPHRASE = os.getenv('AMD_SSH_KEY_PASSPHRASE')
AMD_SSH_PASSWORD = os.getenv('AMD_SSH_PASSWORD')

PROMETHEUS_URL = f"http://{AMD_DROPLET_IP}:{AMD_DROPLET_PORT}/metrics"

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

async def test_connection():
    print("🔍 Testing AMD Droplet Connection...")
    print(f"Target: {PROMETHEUS_URL}\n")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(PROMETHEUS_URL)
            response.raise_for_status()
            
            print("✅ Connection successful!")
            print(f"Status Code: {response.status_code}")
            print(f"Response size: {len(response.text)} bytes\n")
            
            # Parse some key metrics
            lines = response.text.splitlines()
            metrics = {}
            
            for line in lines:
                if line.startswith("node_memory_MemTotal_bytes "):
                    metrics['mem_total_gb'] = float(line.split()[1]) / (1024**3)
                elif line.startswith("node_memory_MemAvailable_bytes "):
                    metrics['mem_avail_gb'] = float(line.split()[1]) / (1024**3)
                elif line.startswith("node_load1 "):
                    metrics['load_1min'] = float(line.split()[1])
                elif line.startswith("node_load5 "):
                    metrics['load_5min'] = float(line.split()[1])
            
            print("📊 Current Metrics:")
            print(f"  Total RAM: {metrics.get('mem_total_gb', 0):.2f} GB")
            print(f"  Available RAM: {metrics.get('mem_avail_gb', 0):.2f} GB")
            print(f"  RAM Usage: {((metrics.get('mem_total_gb', 0) - metrics.get('mem_avail_gb', 0)) / metrics.get('mem_total_gb', 1) * 100):.1f}%")
            print(f"  Load (1min): {metrics.get('load_1min', 0):.2f}")
            print(f"  Load (5min): {metrics.get('load_5min', 0):.2f}")
            
            return True
            
    except httpx.TimeoutException:
        print("❌ Connection timeout - check if droplet is running")
        print("   Try: ssh to droplet and verify node_exporter is running")
        return False
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ssh_connection():
    """Test SSH connection to the droplet"""
    print("\n" + "="*60)
    print("🔐 Testing SSH Connection...")
    print("="*60)
    
    if not PARAMIKO_AVAILABLE:
        print("⚠️  paramiko not installed")
        print("   Install with: pip install paramiko")
        return False
    
    if not AMD_DROPLET_IP or AMD_DROPLET_IP == "YOUR_DROPLET_IP_HERE":
        print("❌ AMD_DROPLET_IP not configured in backend/.env")
        return False
    
    if not AMD_SSH_KEY_PATH and not AMD_SSH_PASSWORD:
        print("⚠️  No SSH credentials configured")
        print("   Set AMD_SSH_KEY_PATH or AMD_SSH_PASSWORD in backend/.env")
        return False
    
    try:
        print(f"\n🔗 Connecting to {AMD_SSH_USER}@{AMD_DROPLET_IP}...")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try SSH key first, then password
        if AMD_SSH_KEY_PATH and os.path.exists(AMD_SSH_KEY_PATH):
            print(f"   Using SSH key: {AMD_SSH_KEY_PATH}")
            ssh.connect(
                hostname=AMD_DROPLET_IP,
                username=AMD_SSH_USER,
                key_filename=AMD_SSH_KEY_PATH,
                passphrase=AMD_SSH_KEY_PASSPHRASE if AMD_SSH_KEY_PASSPHRASE else None,
                timeout=10
            )
        elif AMD_SSH_PASSWORD:
            print(f"   Using password authentication")
            ssh.connect(
                hostname=AMD_DROPLET_IP,
                username=AMD_SSH_USER,
                password=AMD_SSH_PASSWORD,
                timeout=10
            )
        else:
            print(f"❌ SSH key not found: {AMD_SSH_KEY_PATH}")
            return False
        
        print("✅ SSH connection established successfully!\n")
        
        # Test command execution
        print("🧪 Testing command execution...")
        stdin, stdout, stderr = ssh.exec_command('uname -a')
        uname = stdout.read().decode('utf-8').strip()
        print(f"   System: {uname}\n")
        
        # Check if stress-ng is installed
        print("🔍 Checking for stress-ng...")
        stdin, stdout, stderr = ssh.exec_command('which stress-ng')
        stress_path = stdout.read().decode('utf-8').strip()
        
        if stress_path:
            print(f"✅ stress-ng is installed: {stress_path}")
            
            # Check if stress-ng is currently running
            stdin, stdout, stderr = ssh.exec_command('pgrep -a stress-ng')
            processes = stdout.read().decode('utf-8').strip()
            
            if processes:
                print(f"⚠️  stress-ng is currently running:")
                for line in processes.split('\n'):
                    print(f"   {line}")
                print(f"\n💡 To stop: python trigger_real_incident.py stop")
            else:
                print(f"   No stress processes currently running")
        else:
            print(f"⚠️  stress-ng not found")
            print(f"   Install with: python trigger_real_incident.py install")
        
        ssh.close()
        return True
        
    except paramiko.AuthenticationException:
        print("❌ Authentication failed")
        print("   Check your SSH credentials in backend/.env")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("="*60)
    print("🧪 AMD Droplet Connection Test")
    print("="*60)
    print(f"Droplet IP: {AMD_DROPLET_IP}")
    print(f"Metrics Port: {AMD_DROPLET_PORT}")
    print(f"SSH User: {AMD_SSH_USER}")
    print("="*60 + "\n")
    
    # Test metrics endpoint
    metrics_ok = await test_connection()
    
    # Test SSH connection
    ssh_ok = test_ssh_connection()
    
    # Summary
    print("\n" + "="*60)
    print("📋 Test Summary")
    print("="*60)
    print(f"Metrics Endpoint: {'✅ OK' if metrics_ok else '❌ FAILED'}")
    print(f"SSH Connection:   {'✅ OK' if ssh_ok else '❌ FAILED'}")
    
    if metrics_ok and ssh_ok:
        print("\n🎉 All tests passed! You're ready to trigger real incidents.")
        print("\n💡 Next steps:")
        print("   1. Start backend: cd backend && python main.py")
        print("   2. Start frontend: cd frontend && npm run dev")
        print("   3. Trigger incident: python trigger_real_incident.py cpu")
        print("   4. Open UI and click 'Remediate' to fix it!")
    elif metrics_ok and not ssh_ok:
        print("\n⚠️  Metrics work but SSH failed")
        print("   Remediation will fall back to simulation mode")
        print("   Configure SSH in backend/.env for real remediation")
    elif not metrics_ok:
        print("\n❌ Metrics endpoint failed")
        print("   Check if node_exporter is running on the droplet")
        print("   SSH to droplet and run: systemctl status node_exporter")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
