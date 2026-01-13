#!/usr/bin/env python3
"""
C2 Server - Command and Control for Security Assessment
Main entry point for the operator
"""

import sys
import argparse
from c2_operator.server import start_server
from c2_operator.agent_generator import AgentGenerator

def main():
    parser = argparse.ArgumentParser(
        description='C2 Server - Command and Control for Security Assessment'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start the C2 server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    server_parser.add_argument('--port', type=int, default=5000, help='Server port (default: 5000)')
    
    # Generate agent command
    generate_parser = subparsers.add_parser('generate', help='Generate an agent')
    generate_parser.add_argument('platform', choices=['linux', 'windows'], help='Target platform')
    generate_parser.add_argument('--c2-server', required=True, help='C2 server URL (e.g., http://192.168.1.100:5000)')
    
    args = parser.parse_args()
    
    if args.command == 'server':
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                    C2 Operator Server                         ║
║           Security Assessment Command & Control               ║
╚═══════════════════════════════════════════════════════════════╝
        """)
        start_server(args.host, args.port)
    
    elif args.command == 'generate':
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                    Agent Generator                            ║
╚═══════════════════════════════════════════════════════════════╝
        """)
        generator = AgentGenerator()
        result = generator.generate_agent(args.platform, args.c2_server)
        
        print(f"\n[+] Agent generated successfully!")
        print(f"[+] Platform: {result['platform']}")
        print(f"[+] Agent file: {result['agent_path']}")
        print(f"[+] Modules: {result['modules_path']}")
        print(f"[+] Requirements: {result['requirements_path']}")
        print(f"\n{result['instructions']}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
