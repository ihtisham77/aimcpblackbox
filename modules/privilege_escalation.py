import os
import platform
import subprocess

def check_privilege_escalation():
    """Check for privilege escalation opportunities"""
    results = {
        'module': 'privilege_escalation',
        'findings': [],
        'platform': platform.system()
    }
    
    if platform.system() == 'Linux':
        results['findings'].extend(check_linux_privesc())
    elif platform.system() == 'Windows':
        results['findings'].extend(check_windows_privesc())
    
    return results

def check_linux_privesc():
    """Linux privilege escalation checks"""
    findings = []
    
    # Check SUID binaries
    try:
        suid_output = subprocess.check_output(
            'find / -perm -4000 -type f 2>/dev/null',
            shell=True,
            timeout=30
        ).decode()
        
        suid_binaries = suid_output.strip().split('\n')
        findings.append({
            'check': 'SUID Binaries',
            'status': 'found',
            'details': f"Found {len(suid_binaries)} SUID binaries",
            'items': suid_binaries[:20]  # Limit to first 20
        })
    except Exception as e:
        findings.append({
            'check': 'SUID Binaries',
            'status': 'error',
            'details': str(e)
        })
    
    # Check sudo permissions
    try:
        sudo_output = subprocess.check_output(
            'sudo -l 2>/dev/null',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Sudo Permissions',
            'status': 'found',
            'details': sudo_output
        })
    except:
        findings.append({
            'check': 'Sudo Permissions',
            'status': 'no_access',
            'details': 'Cannot check sudo permissions'
        })
    
    # Check writable /etc/passwd
    try:
        if os.access('/etc/passwd', os.W_OK):
            findings.append({
                'check': '/etc/passwd Writable',
                'status': 'vulnerable',
                'details': '/etc/passwd is writable - HIGH RISK'
            })
        else:
            findings.append({
                'check': '/etc/passwd Writable',
                'status': 'secure',
                'details': '/etc/passwd is not writable'
            })
    except Exception as e:
        findings.append({
            'check': '/etc/passwd Writable',
            'status': 'error',
            'details': str(e)
        })
    
    # Check for world-writable directories in PATH
    try:
        path_dirs = os.environ.get('PATH', '').split(':')
        writable_paths = []
        
        for path_dir in path_dirs:
            if os.path.exists(path_dir) and os.access(path_dir, os.W_OK):
                writable_paths.append(path_dir)
        
        if writable_paths:
            findings.append({
                'check': 'Writable PATH Directories',
                'status': 'vulnerable',
                'details': f"Found {len(writable_paths)} writable directories in PATH",
                'items': writable_paths
            })
        else:
            findings.append({
                'check': 'Writable PATH Directories',
                'status': 'secure',
                'details': 'No writable directories in PATH'
            })
    except Exception as e:
        findings.append({
            'check': 'Writable PATH Directories',
            'status': 'error',
            'details': str(e)
        })
    
    return findings

def check_windows_privesc():
    """Windows privilege escalation checks"""
    findings = []
    
    # Check if running as admin
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        
        findings.append({
            'check': 'Administrator Privileges',
            'status': 'admin' if is_admin else 'user',
            'details': f"Running as {'Administrator' if is_admin else 'Standard User'}"
        })
    except Exception as e:
        findings.append({
            'check': 'Administrator Privileges',
            'status': 'error',
            'details': str(e)
        })
    
    # Check unquoted service paths
    try:
        services_output = subprocess.check_output(
            'wmic service get name,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\\windows\\\\" | findstr /i /v """',
            shell=True,
            timeout=30
        ).decode()
        
        if services_output.strip():
            findings.append({
                'check': 'Unquoted Service Paths',
                'status': 'vulnerable',
                'details': 'Found services with unquoted paths',
                'items': services_output.strip().split('\n')[:10]
            })
        else:
            findings.append({
                'check': 'Unquoted Service Paths',
                'status': 'secure',
                'details': 'No unquoted service paths found'
            })
    except Exception as e:
        findings.append({
            'check': 'Unquoted Service Paths',
            'status': 'error',
            'details': str(e)
        })
    
    # Check AlwaysInstallElevated
    try:
        reg_output = subprocess.check_output(
            'reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated',
            shell=True,
            timeout=10
        ).decode()
        
        if 'AlwaysInstallElevated' in reg_output and '0x1' in reg_output:
            findings.append({
                'check': 'AlwaysInstallElevated',
                'status': 'vulnerable',
                'details': 'AlwaysInstallElevated is enabled - HIGH RISK'
            })
        else:
            findings.append({
                'check': 'AlwaysInstallElevated',
                'status': 'secure',
                'details': 'AlwaysInstallElevated is not enabled'
            })
    except:
        findings.append({
            'check': 'AlwaysInstallElevated',
            'status': 'secure',
            'details': 'AlwaysInstallElevated is not set'
        })
    
    return findings
