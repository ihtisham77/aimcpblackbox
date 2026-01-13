import os
import platform
import subprocess

def check_covering_tracks():
    """Check for log files and track covering opportunities"""
    results = {
        'module': 'covering_tracks',
        'findings': [],
        'platform': platform.system()
    }
    
    if platform.system() == 'Linux':
        results['findings'].extend(check_linux_logs())
    elif platform.system() == 'Windows':
        results['findings'].extend(check_windows_logs())
    
    return results

def check_linux_logs():
    """Linux log file checks"""
    findings = []
    
    # Check common log locations
    log_files = [
        '/var/log/auth.log',
        '/var/log/secure',
        '/var/log/syslog',
        '/var/log/messages',
        '/var/log/wtmp',
        '/var/log/btmp',
        '/var/log/lastlog',
        '~/.bash_history',
        '~/.zsh_history'
    ]
    
    accessible_logs = []
    for log_file in log_files:
        expanded = os.path.expanduser(log_file)
        if os.path.exists(expanded):
            writable = os.access(expanded, os.W_OK)
            readable = os.access(expanded, os.R_OK)
            
            accessible_logs.append({
                'file': log_file,
                'readable': readable,
                'writable': writable,
                'size': os.path.getsize(expanded) if readable else 'unknown'
            })
    
    findings.append({
        'check': 'Log Files',
        'status': 'found',
        'details': f"Found {len(accessible_logs)} log files",
        'items': accessible_logs
    })
    
    # Check logging daemons
    try:
        logging_services = subprocess.check_output(
            'systemctl list-units --type=service | grep -E "syslog|rsyslog|journald"',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Logging Services',
            'status': 'active',
            'details': logging_services
        })
    except:
        findings.append({
            'check': 'Logging Services',
            'status': 'unknown',
            'details': 'Cannot determine logging service status'
        })
    
    # Check auditd
    try:
        auditd_status = subprocess.check_output(
            'systemctl is-active auditd 2>/dev/null',
            shell=True,
            timeout=10
        ).decode().strip()
        
        findings.append({
            'check': 'Auditd',
            'status': auditd_status,
            'details': f"Auditd is {auditd_status}"
        })
    except:
        findings.append({
            'check': 'Auditd',
            'status': 'inactive',
            'details': 'Auditd is not running'
        })
    
    # Check last logins
    try:
        last_output = subprocess.check_output(
            'last -n 10',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Recent Logins',
            'status': 'found',
            'details': last_output
        })
    except Exception as e:
        findings.append({
            'check': 'Recent Logins',
            'status': 'error',
            'details': str(e)
        })
    
    # Check command history size
    history_file = os.path.expanduser('~/.bash_history')
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history_lines = len(f.readlines())
            
            findings.append({
                'check': 'Command History',
                'status': 'found',
                'details': f"Bash history contains {history_lines} commands"
            })
        except:
            findings.append({
                'check': 'Command History',
                'status': 'no_access',
                'details': 'Cannot read command history'
            })
    
    return findings

def check_windows_logs():
    """Windows log file checks"""
    findings = []
    
    # Check Event Logs
    event_logs = ['System', 'Security', 'Application']
    
    for log in event_logs:
        try:
            log_output = subprocess.check_output(
                f'wevtutil gli {log}',
                shell=True,
                timeout=10
            ).decode()
            
            findings.append({
                'check': f'Event Log: {log}',
                'status': 'active',
                'details': log_output[:500]
            })
        except Exception as e:
            findings.append({
                'check': f'Event Log: {log}',
                'status': 'error',
                'details': str(e)
            })
    
    # Check PowerShell history
    ps_history_path = os.path.expandvars(
        '%APPDATA%\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt'
    )
    
    if os.path.exists(ps_history_path):
        try:
            with open(ps_history_path, 'r') as f:
                history_lines = len(f.readlines())
            
            findings.append({
                'check': 'PowerShell History',
                'status': 'found',
                'details': f"PowerShell history contains {history_lines} commands",
                'writable': os.access(ps_history_path, os.W_OK)
            })
        except:
            findings.append({
                'check': 'PowerShell History',
                'status': 'no_access',
                'details': 'Cannot read PowerShell history'
            })
    else:
        findings.append({
            'check': 'PowerShell History',
            'status': 'none',
            'details': 'No PowerShell history file found'
        })
    
    # Check recent files
    try:
        recent_path = os.path.expandvars('%APPDATA%\\Microsoft\\Windows\\Recent')
        if os.path.exists(recent_path):
            recent_count = len(os.listdir(recent_path))
            
            findings.append({
                'check': 'Recent Files',
                'status': 'found',
                'details': f"Found {recent_count} recent file entries",
                'writable': os.access(recent_path, os.W_OK)
            })
    except Exception as e:
        findings.append({
            'check': 'Recent Files',
            'status': 'error',
            'details': str(e)
        })
    
    # Check Prefetch
    prefetch_path = 'C:\\Windows\\Prefetch'
    if os.path.exists(prefetch_path):
        try:
            prefetch_count = len([f for f in os.listdir(prefetch_path) if f.endswith('.pf')])
            
            findings.append({
                'check': 'Prefetch Files',
                'status': 'found',
                'details': f"Found {prefetch_count} prefetch files",
                'writable': os.access(prefetch_path, os.W_OK)
            })
        except:
            findings.append({
                'check': 'Prefetch Files',
                'status': 'no_access',
                'details': 'Cannot access Prefetch directory'
            })
    
    # Check Windows Defender logs
    defender_log_path = 'C:\\ProgramData\\Microsoft\\Windows Defender\\Support'
    if os.path.exists(defender_log_path):
        findings.append({
            'check': 'Windows Defender Logs',
            'status': 'found',
            'details': 'Windows Defender logs are present'
        })
    
    return findings
