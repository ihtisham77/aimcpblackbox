"""Internal Reconnaissance Module"""

import os
import platform
import socket
import subprocess


def check_reconnaissance():
    """Perform internal reconnaissance"""
    results = {
        'module': 'reconnaissance',
        'findings': [],
        'risk_level': 'info'
    }
    
    results['findings'].extend(check_system_info())
    results['findings'].extend(check_network_info())
    results['findings'].extend(check_users_groups())
    
    return results


def check_system_info():
    """Gather system information"""
    findings = []
    
    try:
        system_info = {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor()
        }
        
        findings.append({
            'check': 'System Information',
            'status': 'COLLECTED',
            'details': system_info,
            'risk': 'INFO'
        })
    except Exception as e:
        findings.append({'check': 'System Information', 'status': 'ERROR', 'error': str(e)})
    
    # Check installed software
    try:
        system = platform.system()
        if system == 'Linux':
            result = subprocess.run(
                ['dpkg', '-l'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                packages = len(result.stdout.split('\n'))
                findings.append({
                    'check': 'Installed Packages',
                    'status': 'COLLECTED',
                    'details': f'Found {packages} installed packages',
                    'count': packages,
                    'risk': 'INFO'
                })
        elif system == 'Windows':
            result = subprocess.run(
                ['wmic', 'product', 'get', 'name,version'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                products = len([l for l in result.stdout.split('\n') if l.strip()])
                findings.append({
                    'check': 'Installed Software',
                    'status': 'COLLECTED',
                    'details': f'Found {products} installed products',
                    'count': products,
                    'risk': 'INFO'
                })
    except:
        pass
    
    return findings


def check_network_info():
    """Gather network information"""
    findings = []
    
    # Get network interfaces
    try:
        system = platform.system()
        if system == 'Linux':
            result = subprocess.run(
                ['ip', 'addr', 'show'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                findings.append({
                    'check': 'Network Interfaces',
                    'status': 'COLLECTED',
                    'details': result.stdout[:1000],
                    'risk': 'INFO'
                })
        elif system == 'Windows':
            result = subprocess.run(
                ['ipconfig', '/all'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                findings.append({
                    'check': 'Network Configuration',
                    'status': 'COLLECTED',
                    'details': result.stdout[:1000],
                    'risk': 'INFO'
                })
    except:
        pass
    
    # Check routing table
    try:
        system = platform.system()
        if system == 'Linux':
            result = subprocess.run(
                ['ip', 'route', 'show'],
                capture_output=True, text=True, timeout=5
            )
        else:
            result = subprocess.run(
                ['route', 'print'],
                capture_output=True, text=True, timeout=5
            )
        
        if result.returncode == 0:
            findings.append({
                'check': 'Routing Table',
                'status': 'COLLECTED',
                'details': result.stdout[:1000],
                'risk': 'INFO'
            })
    except:
        pass
    
    # Check ARP cache
    try:
        result = subprocess.run(
            ['arp', '-a'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            arp_entries = len([l for l in result.stdout.split('\n') if l.strip()])
            findings.append({
                'check': 'ARP Cache',
                'status': 'COLLECTED',
                'details': f'Found {arp_entries} ARP entries',
                'count': arp_entries,
                'risk': 'INFO'
            })
    except:
        pass
    
    # Check listening ports
    try:
        system = platform.system()
        if system == 'Linux':
            result = subprocess.run(
                ['ss', '-tuln'],
                capture_output=True, text=True, timeout=5
            )
        else:
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True, text=True, timeout=5
            )
        
        if result.returncode == 0:
            listening = [l for l in result.stdout.split('\n') if 'LISTEN' in l or 'LISTENING' in l]
            findings.append({
                'check': 'Listening Ports',
                'status': 'COLLECTED',
                'details': f'Found {len(listening)} listening ports',
                'count': len(listening),
                'items': listening[:20],
                'risk': 'MEDIUM'
            })
    except:
        pass
    
    return findings


def check_users_groups():
    """Check users and groups"""
    findings = []
    
    try:
        system = platform.system()
        
        if system == 'Linux':
            # Check users
            if os.path.exists('/etc/passwd'):
                with open('/etc/passwd', 'r') as f:
                    users = [line.split(':')[0] for line in f.readlines()]
                findings.append({
                    'check': 'System Users',
                    'status': 'COLLECTED',
                    'details': f'Found {len(users)} users',
                    'count': len(users),
                    'items': users[:20],
                    'risk': 'INFO'
                })
            
            # Check groups
            if os.path.exists('/etc/group'):
                with open('/etc/group', 'r') as f:
                    groups = [line.split(':')[0] for line in f.readlines()]
                findings.append({
                    'check': 'System Groups',
                    'status': 'COLLECTED',
                    'details': f'Found {len(groups)} groups',
                    'count': len(groups),
                    'risk': 'INFO'
                })
        
        elif system == 'Windows':
            # Check local users
            result = subprocess.run(
                ['net', 'user'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                users = [l.strip() for l in result.stdout.split('\n') if l.strip() and not l.startswith('-')]
                findings.append({
                    'check': 'Local Users',
                    'status': 'COLLECTED',
                    'details': f'Found {len(users)} local users',
                    'count': len(users),
                    'risk': 'INFO'
                })
            
            # Check local groups
            result = subprocess.run(
                ['net', 'localgroup'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                groups = [l.strip() for l in result.stdout.split('\n') if l.strip() and not l.startswith('*')]
                findings.append({
                    'check': 'Local Groups',
                    'status': 'COLLECTED',
                    'details': f'Found {len(groups)} local groups',
                    'count': len(groups),
                    'risk': 'INFO'
                })
    except Exception as e:
        findings.append({'check': 'Users and Groups', 'status': 'ERROR', 'error': str(e)})
    
    return findings


if __name__ == '__main__':
    import json
    result = check_reconnaissance()
    print(json.dumps(result, indent=2))
