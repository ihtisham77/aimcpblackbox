# C2 Server - Security Assessment Tool

A Command and Control (C2) server designed for security assessment and penetration testing. This tool allows operators to deploy agents on target systems to perform automated security checks for common misconfigurations and vulnerabilities.

## ⚠️ Legal Disclaimer

**This tool is for educational and authorized security testing purposes only.** 

- Only use this tool on systems you own or have explicit written permission to test
- Unauthorized access to computer systems is illegal
- The authors are not responsible for misuse or damage caused by this tool
- Always comply with local laws and regulations

## Features

### Operator (C2 Server)
- Web-based dashboard for managing agents
- RESTful API for agent communication
- SQLite database for tracking agents and results
- Real-time agent status monitoring
- Command queuing and result collection

### Agents
- Cross-platform support (Linux and Windows)
- Automatic registration with C2 server
- Periodic beacon to check for commands
- Modular security assessment framework

### Security Assessment Modules

1. **Privilege Escalation** - Checks for privilege escalation opportunities
   - SUID binaries (Linux)
   - Sudo permissions (Linux)
   - Unquoted service paths (Windows)
   - AlwaysInstallElevated (Windows)

2. **Persistence** - Identifies persistence mechanisms
   - Cron jobs (Linux)
   - Systemd services (Linux)
   - Registry Run keys (Windows)
   - Scheduled tasks (Windows)

3. **Credential Harvesting** - Finds credential storage locations
   - SSH keys
   - Bash history
   - Saved credentials (Windows)
   - WiFi passwords (Windows)

4. **Internal Reconnaissance** - Gathers system information
   - Network interfaces
   - Active connections
   - Running processes
   - System users

5. **Lateral Movement** - Identifies lateral movement opportunities
   - SSH configurations
   - Network shares
   - Domain computers
   - ARP cache

6. **Data Access** - Locates sensitive data
   - Interesting files
   - Database files
   - Browser data
   - Recent files

7. **Data Exfiltration** - Checks exfiltration paths
   - Internet connectivity
   - Available tools (curl, wget, etc.)
   - Removable media
   - Cloud storage folders

8. **C2 Check** - Validates C2 communication capabilities
   - Outbound port connectivity
   - Proxy settings
   - Firewall status

9. **Covering Tracks** - Identifies log files and artifacts
   - System logs
   - Command history
   - Event logs (Windows)
   - Prefetch files (Windows)

## Installation

### Requirements
- Python 3.7+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### 1. Start the C2 Server

```bash
python main.py server --host 0.0.0.0 --port 5000
```

Access the dashboard at: `http://localhost:5000`

### 2. Generate an Agent

For Linux:
```bash
python main.py generate linux --c2-server http://192.168.1.100:5000
```

For Windows:
```bash
python main.py generate windows --c2-server http://192.168.1.100:5000
```

This will create:
- Agent file in `generated_agents/`
- Copy of modules directory
- requirements.txt for the agent
- Deployment instructions

### 3. Deploy the Agent

Transfer the generated files to the target system and follow the deployment instructions provided by the generator.

**Linux Example:**
```bash
# On target system
pip3 install -r requirements.txt
python3 agent_linux_20260113_120000.py http://192.168.1.100:5000
```

**Windows Example:**
```cmd
REM On target system
pip install -r requirements.txt
python agent_windows_20260113_120000.py http://192.168.1.100:5000
```

### 4. Execute Security Assessments

From the web dashboard:
1. Select an agent from the "Active Agents" list
2. Choose a security module from the dropdown
3. Click "Execute"
4. View results in the "Recent Results" section

## Architecture

```
c2-server/
├── operator/           # C2 server components
│   ├── server.py      # Flask web server
│   ├── database.py    # SQLite database operations
│   └── agent_generator.py  # Agent generation
├── agents/            # Agent templates
│   └── agent_template.py
├── modules/           # Security assessment modules
│   ├── privilege_escalation.py
│   ├── persistence.py
│   ├── credential_harvesting.py
│   ├── internal_reconnaissance.py
│   ├── lateral_movement.py
│   ├── data_access.py
│   ├── data_exfiltration.py
│   ├── c2_check.py
│   └── covering_tracks.py
├── utils/             # Utility functions
│   ├── config.py
│   └── crypto.py
├── generated_agents/  # Generated agent files
└── main.py           # Main entry point
```

## API Endpoints

### Agent Endpoints
- `POST /api/agent/register` - Register a new agent
- `POST /api/agent/<agent_id>/beacon` - Agent beacon (get commands)
- `POST /api/agent/<agent_id>/result` - Submit command results

### Operator Endpoints
- `GET /api/agents` - List all agents
- `POST /api/command` - Queue a command for an agent
- `GET /api/results` - Get assessment results

## Security Considerations

1. **Network Security**
   - Use HTTPS in production
   - Implement authentication
   - Use encrypted communications

2. **Operational Security**
   - Change default ports
   - Use obfuscation techniques
   - Implement anti-forensics measures

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Secure database access
   - Implement access controls

## Development

### Adding New Modules

1. Create a new module in `modules/`:
```python
def check_new_module():
    results = {
        'module': 'new_module',
        'findings': [],
        'platform': platform.system()
    }
    # Add your checks here
    return results
```

2. Register in `modules/__init__.py`:
```python
from .new_module import check_new_module

MODULE_MAP = {
    # ...
    'new_module': check_new_module
}
```

3. Add to dashboard dropdown in `operator/server.py`

## Troubleshooting

### Agent Can't Connect
- Verify C2 server is running
- Check firewall rules
- Ensure correct C2 server URL
- Verify network connectivity

### Module Errors
- Check Python version compatibility
- Verify required permissions
- Review module-specific requirements

### Database Issues
- Check file permissions on `c2_server.db`
- Verify SQLite installation
- Check disk space

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This tool is provided for educational purposes. Use responsibly and legally.

## Acknowledgments

Built for security professionals and penetration testers to automate common assessment tasks.

---

**Remember: Always obtain proper authorization before testing any systems.**
