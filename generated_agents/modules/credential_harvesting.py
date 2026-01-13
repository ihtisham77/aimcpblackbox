import os
import platform
import subprocess
import glob

def check_credential_harvesting():
    """Check for credential harvesting opportunities"""
    results = {
        'module': 'credential_harvesting',
        'findings': [],
        'platform': platform.system()
    }
    
    if platform.system() == 'Linux':
        results['findings'].extend(check_linux_credentials())
    elif platform.system() == 'Windows':
        results['findings'].extend(check_windows_credentials())
    
    return results

def check_linux_credentials():
    """Linux credential checks"""
    findings = []
    
    # Check for SSH keys
    ssh_paths = [
        '~/.ssh/id_rsa',
        '~/.ssh/id_dsa',
        '~/.ssh/id_ecdsa',
        '~/.ssh/id_ed25519'
    ]
    
    found_keys = []
    for key_path in ssh_paths:
        expanded = os.path.expanduser(key_path)
        if os.path.exists(expanded):
            found_keys.append(key_path)
    
    findings.append({
        'check': 'SSH Private Keys',
        'status': 'found' if found_keys else 'none',
        'details': f"Found {len(found_keys)} SSH keys" if found_keys else "No SSH keys found",
        'items': found_keys
    })
    
    # Check bash history
    history_path = os.path.expanduser('~/.bash_history')
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r') as f:
                history = f.readlines()
                
            # Look for potential credentials in history
            sensitive_commands = [line for line in history if any(
                keyword in line.lower() for keyword in ['password', 'passwd', 'pwd', 'token', 'api', 'secret']
            )]
            
            findings.append({
                'check': 'Bash History',
                'status': 'found',
                'details': f"Found {len(sensitive_commands)} potentially sensitive commands",
                'items': sensitive_commands[:10]
            })
        except:
            findings.append({
                'check': 'Bash History',
                'status': 'no_access',
                'details': 'Cannot read bash history'
            })
    
    # Check for config files with potential credentials
    config_patterns = [
        '~/.aws/credentials',
        '~/.docker/config.json',
        '~/.gitconfig',
        '~/.netrc'
    ]
    
    found_configs = []
    for pattern in config_patterns:
        expanded = os.path.expanduser(pattern)
        if os.path.exists(expanded):
            found_configs.append(pattern)
    
    findings.append({
        'check': 'Configuration Files',
        'status': 'found' if found_configs else 'none',
        'details': f"Found {len(found_configs)} config files",
        'items': found_configs
    })
    
    # Check environment variables
    sensitive_env_vars = []
    for key, value in os.environ.items():
        if any(keyword in key.lower() for keyword in ['password', 'token', 'secret', 'api', 'key']):
            sensitive_env_vars.append(key)
    
    findings.append({
        'check': 'Environment Variables',
        'status': 'found' if sensitive_env_vars else 'none',
        'details': f"Found {len(sensitive_env_vars)} potentially sensitive env vars",
        'items': sensitive_env_vars
    })
    
    return findings

def check_windows_credentials():
    """Windows credential checks"""
    findings = []
    
    # Check saved credentials
    try:
        creds_output = subprocess.check_output(
            'cmdkey /list',
            shell=True,
            timeout=10
        ).decode()
        
        cred_lines = [line for line in creds_output.split('\n') if 'Target:' in line]
        findings.append({
            'check': 'Saved Credentials',
            'status': 'found' if cred_lines else 'none',
            'details': f"Found {len(cred_lines)} saved credentials",
            'items': cred_lines
        })
    except Exception as e:
        findings.append({
            'check': 'Saved Credentials',
            'status': 'error',
            'details': str(e)
        })
    
    # Check for unattended install files
    unattend_paths = [
        'C:\\Windows\\Panther\\Unattend.xml',
        'C:\\Windows\\Panther\\Unattended.xml',
        'C:\\Windows\\System32\\sysprep\\unattend.xml',
        'C:\\Windows\\System32\\sysprep\\Panther\\unattend.xml'
    ]
    
    found_unattend = []
    for path in unattend_paths:
        if os.path.exists(path):
            found_unattend.append(path)
    
    findings.append({
        'check': 'Unattended Install Files',
        'status': 'found' if found_unattend else 'none',
        'details': f"Found {len(found_unattend)} unattended install files",
        'items': found_unattend
    })
    
    # Check registry for autologon
    try:
        autologon_output = subprocess.check_output(
            'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v DefaultPassword',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'AutoLogon Password',
            'status': 'vulnerable',
            'details': 'AutoLogon password found in registry - HIGH RISK'
        })
    except:
        findings.append({
            'check': 'AutoLogon Password',
            'status': 'secure',
            'details': 'No AutoLogon password in registry'
        })
    
    # Check for WiFi passwords
    try:
        wifi_output = subprocess.check_output(
            'netsh wlan show profiles',
            shell=True,
            timeout=10
        ).decode()
        
        profiles = [line.split(':')[1].strip() for line in wifi_output.split('\n') if 'All User Profile' in line]
        findings.append({
            'check': 'WiFi Profiles',
            'status': 'found' if profiles else 'none',
            'details': f"Found {len(profiles)} WiFi profiles",
            'items': profiles[:10]
        })
    except Exception as e:
        findings.append({
            'check': 'WiFi Profiles',
            'status': 'error',
            'details': str(e)
        })
    
    return findings
