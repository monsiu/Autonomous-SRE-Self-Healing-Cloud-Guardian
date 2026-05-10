#!/usr/bin/env python3
"""
Script to trigger REAL incidents on the AMD droplet by starting stress tests.
This will cause actual CPU/memory spikes that the system can detect and remediate.
"""

import paramiko
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

AMD_DROPLET_IP = os.getenv('AMD_DROPLET_IP')
AMD_SSH_USER = os.getenv('AMD_SSH_USER', 'root')
AMD_SSH_KEY_PATH = os.getenv('AMD_SSH_KEY_PATH')
AMD_SSH_KEY_PASSPHRASE = os.getenv('AMD_SSH_KEY_PASSPHRASE')
AMD_SSH_PASSWORD = os.getenv('AMD_SSH_PASSWORD')

def execute_ssh_command(command: str, description: str = ""):
    """Execute a command on the droplet via SSH"""
    if not AMD_DROPLET_IP or AMD_DROPLET_IP == "YOUR_DROPLET_IP_HERE":
        print("❌ Error: AMD_DROPLET_IP not configured in backend/.env")
        sys.exit(1)
    
    try:
        print(f"\n🔗 Connecting to {AMD_DROPLET_IP}...")
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
            print("❌ Error: No SSH credentials configured")
            print("   Set AMD_SSH_KEY_PATH or AMD_SSH_PASSWORD in backend/.env")
            sys.exit(1)
        
        print(f"✅ Connected successfully")
        
        if description:
            print(f"\n🚀 {description}")
        print(f"   Command: {command}")
        
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        
        stdout_text = stdout.read().decode('utf-8')
        stderr_text = stderr.read().decode('utf-8')
        
        if exit_code == 0:
            print(f"✅ Command executed successfully")
            if stdout_text:
                print(f"   Output: {stdout_text.strip()}")
        else:
            print(f"⚠️  Command exited with code {exit_code}")
            if stderr_text:
                print(f"   Error: {stderr_text.strip()}")
        
        ssh.close()
        return exit_code == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_stress_installed():
    """Check if stress-ng is installed on the droplet"""
    print("\n📋 Checking if stress-ng is installed...")
    result = execute_ssh_command("which stress-ng", "")
    
    if not result:
        print("\n⚠️  stress-ng not found. Installing...")
        install_cmd = "apt-get update && apt-get install -y stress-ng"
        execute_ssh_command(install_cmd, "Installing stress-ng")
    else:
        print("✅ stress-ng is already installed")

def trigger_cpu_incident(duration: int = 120):
    """Trigger a CPU spike incident"""
    print(f"\n{'='*60}")
    print(f"🔥 TRIGGERING CPU INCIDENT")
    print(f"{'='*60}")
    
    # Kill any existing stress processes first
    execute_ssh_command("pkill -9 stress-ng || true", "Cleaning up existing stress processes")
    
    # Start CPU stress test in background
    # Using 4 CPU workers for 120 seconds (2 minutes)
    cmd = f"nohup stress-ng --cpu 4 --timeout {duration}s > /dev/null 2>&1 &"
    success = execute_ssh_command(cmd, f"Starting CPU stress test ({duration}s)")
    
    if success:
        print(f"\n✅ CPU incident triggered successfully!")
        print(f"   Duration: {duration} seconds")
        print(f"   Workers: 4 CPU cores")
        print(f"\n💡 What to do next:")
        print(f"   1. Open the frontend UI (http://localhost:5173)")
        print(f"   2. Watch the System Health Score drop as CPU spikes")
        print(f"   3. Click 'Start Incident' to generate anomalous logs")
        print(f"   4. Wait for the agent to detect and diagnose")
        print(f"   5. Click 'Remediate' to kill the stress processes")
        print(f"   6. Watch CPU drop and health score improve!")
    else:
        print(f"\n❌ Failed to trigger CPU incident")

def trigger_memory_incident(duration: int = 120):
    """Trigger a memory spike incident"""
    print(f"\n{'='*60}")
    print(f"🔥 TRIGGERING MEMORY INCIDENT")
    print(f"{'='*60}")
    
    # Kill any existing stress processes first
    execute_ssh_command("pkill -9 stress-ng || true", "Cleaning up existing stress processes")
    
    # Start memory stress test in background
    # Using 2 workers, each allocating 512MB
    cmd = f"nohup stress-ng --vm 2 --vm-bytes 512M --timeout {duration}s > /dev/null 2>&1 &"
    success = execute_ssh_command(cmd, f"Starting memory stress test ({duration}s)")
    
    if success:
        print(f"\n✅ Memory incident triggered successfully!")
        print(f"   Duration: {duration} seconds")
        print(f"   Workers: 2 VM workers (512MB each)")
    else:
        print(f"\n❌ Failed to trigger memory incident")

def trigger_combined_incident(duration: int = 120):
    """Trigger both CPU and memory spike"""
    print(f"\n{'='*60}")
    print(f"🔥 TRIGGERING COMBINED CPU + MEMORY INCIDENT")
    print(f"{'='*60}")
    
    # Kill any existing stress processes first
    execute_ssh_command("pkill -9 stress-ng || true", "Cleaning up existing stress processes")
    
    # Start combined stress test
    cmd = f"nohup stress-ng --cpu 4 --vm 2 --vm-bytes 512M --timeout {duration}s > /dev/null 2>&1 &"
    success = execute_ssh_command(cmd, f"Starting combined stress test ({duration}s)")
    
    if success:
        print(f"\n✅ Combined incident triggered successfully!")
        print(f"   Duration: {duration} seconds")
        print(f"   CPU Workers: 4 cores")
        print(f"   Memory Workers: 2 (512MB each)")
    else:
        print(f"\n❌ Failed to trigger combined incident")

def stop_all_incidents():
    """Stop all running stress tests"""
    print(f"\n{'='*60}")
    print(f"🛑 STOPPING ALL INCIDENTS")
    print(f"{'='*60}")
    
    success = execute_ssh_command("pkill -9 stress-ng || pkill -9 stress", "Killing all stress processes")
    
    if success:
        print(f"\n✅ All stress processes stopped")
        print(f"   CPU and memory should return to normal levels")
    else:
        print(f"\n⚠️  No stress processes found (or already stopped)")

def check_status():
    """Check if stress tests are currently running"""
    print(f"\n{'='*60}")
    print(f"📊 CHECKING INCIDENT STATUS")
    print(f"{'='*60}")
    
    execute_ssh_command("ps aux | grep stress-ng | grep -v grep || echo 'No stress processes running'", "")

def main():
    if len(sys.argv) < 2:
        print(f"""
{'='*60}
🔥 Real Incident Trigger Script
{'='*60}

Usage: python trigger_real_incident.py <command> [duration]

Commands:
  cpu              Trigger CPU spike incident (default: 120s)
  memory           Trigger memory spike incident (default: 120s)
  combined         Trigger both CPU and memory spike (default: 120s)
  stop             Stop all running incidents
  status           Check if incidents are running
  install          Install stress-ng on the droplet

Examples:
  python trigger_real_incident.py cpu          # 2-minute CPU spike
  python trigger_real_incident.py cpu 60       # 1-minute CPU spike
  python trigger_real_incident.py combined     # Combined incident
  python trigger_real_incident.py stop         # Stop all incidents
  python trigger_real_incident.py status       # Check status

Configuration:
  Edit backend/.env to set:
  - AMD_DROPLET_IP (required)
  - AMD_SSH_KEY_PATH or AMD_SSH_PASSWORD (required)
  - AMD_SSH_USER (default: root)

{'='*60}
""")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    if command == "cpu":
        check_stress_installed()
        trigger_cpu_incident(duration)
    elif command == "memory":
        check_stress_installed()
        trigger_memory_incident(duration)
    elif command == "combined":
        check_stress_installed()
        trigger_combined_incident(duration)
    elif command == "stop":
        stop_all_incidents()
    elif command == "status":
        check_status()
    elif command == "install":
        check_stress_installed()
    else:
        print(f"❌ Unknown command: {command}")
        print(f"   Use: cpu, memory, combined, stop, status, or install")
        sys.exit(1)

if __name__ == "__main__":
    main()
