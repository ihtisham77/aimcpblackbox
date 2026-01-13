import os
import platform
import subprocess

def check_c2():
    """Check for C2 communication capabilities"""
    results = {
        'module': 'c2_check',
        'findings': [],
        'platform': platform.system()
    }
    
    findings = []
    
    # Check outbound connectivity
    test_ports = [80, 443, 8080, 53]
    
    for port in test_ports:
        try:
            if platform.system() == 'Windows':
                test_output = subprocess.check_output(
                    f'powershell -Command "Test-NetConnection -ComputerName 8.8.8.8 -Port {port} -InformationLevel Quiet"',
                    shell=True,
                    timeout=5
                ).decode()
                
                status = 'open' if 'True' in test_output else 'closed'
            else:
                # Use nc or timeout with bash
                test_output = subprocess.check_output(
                    f'timeout 2 bash -c "echo > /dev/tcp/8.8.8.8/{port}" 2>&1',
                    shell=True,
                    timeout=5
                ).decode()
                
                status = 'open'
        except:
            status = 'closed'
        
        findings.append({
            'check': f'Outbound Port {port}',
            'status': status,
            'details': f"Port {port} is {status} for outbound connections"
        })
    
    # Check for proxy settings
    if platform.system() == 'Linux':
        proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
        proxy_settings = []
        
        for var in proxy_vars:
            if var in os.environ:
                proxy_settings.append(f"{var}={os.environ[var]}")
        
        findings.append({
            'check': 'Proxy Settings',
            'status': 'found' if proxy_settings else 'none',
            'details': 'Proxy configured' if proxy_settings else 'No proxy configured',
            'items': proxy_settings
        })
    
    elif platform.system() == 'Windows':
        try:
            proxy_output = subprocess.check_output(
                'reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable',
                shell=True,
                timeout=10
            ).decode()
            
            proxy_enabled = '0x1' in proxy_output
            
            findings.append({
                'check': 'Proxy Settings',
                'status': 'enabled' if proxy_enabled else 'disabled',
                'details': 'Proxy is enabled' if proxy_enabled else 'No proxy configured'
            })
        except:
            findings.append({
                'check': 'Proxy Settings',
                'status': 'none',
                'details': 'No proxy configured'
            })
    
    # Check firewall status
    if platform.system() == 'Linux':
        try:
            fw_output = subprocess.check_output(
                'sudo iptables -L -n 2>/dev/null || iptables -L -n 2>/dev/null',
                shell=True,
                timeout=10
            ).decode()
            
            findings.append({
                'check': 'Firewall Status',
                'status': 'active',
                'details': 'Firewall rules detected'
            })
        except:
            findings.append({
                'check': 'Firewall Status',
                'status': 'unknown',
                'details': 'Cannot determine firewall status'
            })
    
    elif platform.system() == 'Windows':
        try:
            fw_output = subprocess.check_output(
                'netsh advfirewall show allprofiles state',
                shell=True,
                timeout=10
            ).decode()
            
            findings.append({
                'check': 'Firewall Status',
                'status': 'active' if 'ON' in fw_output else 'inactive',
                'details': fw_output
            })
        except Exception as e:
            findings.append({
                'check': 'Firewall Status',
                'status': 'error',
                'details': str(e)
            })
    
    # Check for common C2 indicators
    suspicious_processes = []
    if platform.system() == 'Linux':
        try:
            ps_output = subprocess.check_output(
                'ps aux',
                shell=True,
                timeout=10
            ).decode()
            
            # Look for suspicious patterns
            for line in ps_output.split('\n'):
                if any(keyword in line.lower() for keyword in ['nc', 'netcat', 'ncat', 'socat', 'reverse', 'shell']):
                    suspicious_processes.append(line.strip())
        except:
            pass
    
    elif platform.system() == 'Windows':
        try:
            ps_output = subprocess.check_output(
                'tasklist /v',
                shell=True,
                timeout=10
            ).decode()
            
            for line in ps_output.split('\n'):
                if any(keyword in line.lower() for keyword in ['powershell', 'cmd', 'nc.exe', 'netcat']):
                    suspicious_processes.append(line.strip())
        except:
            pass
    
    findings.append({
        'check': 'Suspicious Processes',
        'status': 'found' if suspicious_processes else 'none',
        'details': f"Found {len(suspicious_processes)} potentially suspicious processes",
        'items': suspicious_processes[:10]
    })
    
    results['findings'] = findings
    return results
