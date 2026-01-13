import os
import platform
import subprocess
import socket

def check_internal_reconnaissance():
    """Perform internal reconnaissance"""
    results = {
        'module': 'internal_reconnaissance',
        'findings': [],
        'platform': platform.system()
    }
    
    # System information
    results['findings'].append({
        'check': 'System Information',
        'status': 'collected',
        'details': {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor()
        }
    })
    
    if platform.system() == 'Linux':
        results['findings'].extend(check_linux_recon())
    elif platform.system() == 'Windows':
        results['findings'].extend(check_windows_recon())
    
    return results

def check_linux_recon():
    """Linux reconnaissance"""
    findings = []
    
    # Network interfaces
    try:
        ifconfig_output = subprocess.check_output(
            'ip addr show 2>/dev/null || ifconfig',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Network Interfaces',
            'status': 'collected',
            'details': ifconfig_output
        })
    except Exception as e:
        findings.append({
            'check': 'Network Interfaces',
            'status': 'error',
            'details': str(e)
        })
    
    # Active connections
    try:
        netstat_output = subprocess.check_output(
            'ss -tunap 2>/dev/null || netstat -tunap 2>/dev/null',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Active Connections',
            'status': 'collected',
            'details': netstat_output[:2000]  # Limit output
        })
    except Exception as e:
        findings.append({
            'check': 'Active Connections',
            'status': 'error',
            'details': str(e)
        })
    
    # Running processes
    try:
        ps_output = subprocess.check_output(
            'ps aux',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Running Processes',
            'status': 'collected',
            'details': f"Process count: {len(ps_output.split(chr(10)))}",
            'sample': ps_output.split('\n')[:20]
        })
    except Exception as e:
        findings.append({
            'check': 'Running Processes',
            'status': 'error',
            'details': str(e)
        })
    
    # Users
    try:
        with open('/etc/passwd', 'r') as f:
            users = [line.split(':')[0] for line in f.readlines()]
        
        findings.append({
            'check': 'System Users',
            'status': 'collected',
            'details': f"Found {len(users)} users",
            'items': users
        })
    except Exception as e:
        findings.append({
            'check': 'System Users',
            'status': 'error',
            'details': str(e)
        })
    
    # Mounted filesystems
    try:
        mount_output = subprocess.check_output(
            'mount',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Mounted Filesystems',
            'status': 'collected',
            'details': mount_output
        })
    except Exception as e:
        findings.append({
            'check': 'Mounted Filesystems',
            'status': 'error',
            'details': str(e)
        })
    
    return findings

def check_windows_recon():
    """Windows reconnaissance"""
    findings = []
    
    # Network configuration
    try:
        ipconfig_output = subprocess.check_output(
            'ipconfig /all',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Network Configuration',
            'status': 'collected',
            'details': ipconfig_output
        })
    except Exception as e:
        findings.append({
            'check': 'Network Configuration',
            'status': 'error',
            'details': str(e)
        })
    
    # Active connections
    try:
        netstat_output = subprocess.check_output(
            'netstat -ano',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Active Connections',
            'status': 'collected',
            'details': netstat_output[:2000]
        })
    except Exception as e:
        findings.append({
            'check': 'Active Connections',
            'status': 'error',
            'details': str(e)
        })
    
    # Running processes
    try:
        tasklist_output = subprocess.check_output(
            'tasklist /v',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Running Processes',
            'status': 'collected',
            'details': f"Process count: {len(tasklist_output.split(chr(10)))}",
            'sample': tasklist_output.split('\n')[:20]
        })
    except Exception as e:
        findings.append({
            'check': 'Running Processes',
            'status': 'error',
            'details': str(e)
        })
    
    # Local users
    try:
        users_output = subprocess.check_output(
            'net user',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Local Users',
            'status': 'collected',
            'details': users_output
        })
    except Exception as e:
        findings.append({
            'check': 'Local Users',
            'status': 'error',
            'details': str(e)
        })
    
    # Domain information
    try:
        domain_output = subprocess.check_output(
            'systeminfo | findstr /B /C:"Domain"',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Domain Information',
            'status': 'collected',
            'details': domain_output
        })
    except Exception as e:
        findings.append({
            'check': 'Domain Information',
            'status': 'error',
            'details': str(e)
        })
    
    return findings
