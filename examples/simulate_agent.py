#!/usr/bin/env python3
"""
Simulate an agent without actually connecting to C2 server
Useful for testing modules locally
"""

import sys
import os
import json
import uuid
import socket
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import execute_module, MODULE_MAP

class SimulatedAgent:
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.hostname = socket.gethostname()
        self.platform = platform.system()
    
    def run_module(self, module_name):
        """Run a specific security module"""
        print(f"[*] Agent ID: {self.agent_id}")
        print(f"[*] Hostname: {self.hostname}")
        print(f"[*] Platform: {self.platform}")
        print(f"[*] Executing module: {module_name}")
        print("=" * 70)
        
        if module_name not in MODULE_MAP:
            print(f"[-] Error: Module '{module_name}' not found")
            print(f"[*] Available modules: {', '.join(MODULE_MAP.keys())}")
            return None
        
        try:
            result = execute_module(module_name)
            
            print(f"\n[+] Module execution completed")
            print(f"[+] Platform: {result.get('platform', 'Unknown')}")
            print(f"[+] Findings: {len(result.get('findings', []))}")
            print("\n" + "=" * 70)
            print("Results:")
            print("=" * 70)
            print(json.dumps(result, indent=2, default=str))
            
            # Save to file
            output_file = f"result_{module_name}_{self.agent_id[:8]}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"\n[+] Results saved to: {output_file}")
            
            return result
            
        except Exception as e:
            print(f"[-] Error executing module: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_all_modules(self):
        """Run all available security modules"""
        print(f"[*] Agent ID: {self.agent_id}")
        print(f"[*] Hostname: {self.hostname}")
        print(f"[*] Platform: {self.platform}")
        print(f"[*] Running all modules...")
        print("=" * 70)
        
        all_results = {}
        
        for module_name in MODULE_MAP.keys():
            print(f"\n[*] Executing: {module_name}")
            print("-" * 70)
            
            try:
                result = execute_module(module_name)
                all_results[module_name] = result
                print(f"[+] {module_name}: {len(result.get('findings', []))} findings")
            except Exception as e:
                print(f"[-] {module_name}: ERROR - {e}")
                all_results[module_name] = {'error': str(e)}
        
        # Save all results
        output_file = f"all_results_{self.agent_id[:8]}.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print("\n" + "=" * 70)
        print(f"[+] All results saved to: {output_file}")
        
        return all_results

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python simulate_agent.py <module_name>  - Run specific module")
        print("  python simulate_agent.py all            - Run all modules")
        print()
        print("Available modules:")
        for module in MODULE_MAP.keys():
            print(f"  - {module}")
        sys.exit(1)
    
    agent = SimulatedAgent()
    
    if sys.argv[1] == 'all':
        agent.run_all_modules()
    else:
        module_name = sys.argv[1]
        agent.run_module(module_name)

if __name__ == '__main__':
    main()
