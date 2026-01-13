import os
import platform
import subprocess

def check_data_exfiltration():
    """Check for data exfiltration paths"""
    results = {
        'module': 'data_exfiltration',
        'findings': [],
        'platform': platform.system()
    }
    
    # Check network connectivity
    findings = []
    
    # Check internet connectivity
    try:
        if platform.system() == 'Windows':
            ping_output = subprocess.check_output(
                'ping -n 1 8.8.8.8',
                shell=True,
                timeout=5
            ).decode()
        else:
            ping_output = subprocess.check_output(
                'ping -c 1 8.8.8.8',
                shell=True,
                timeout=5
            ).decode()
        
        findings.append({
            'check': 'Internet Connectivity',
            'status': 'available',
            'details': 'Internet connection available for exfiltration'
        })
    except:
        findings.append({
            'check': 'Internet Connectivity',
            'status': 'unavailable',
            'details': 'No internet connectivity detected'
        })
    
    # Check for curl/wget
    exfil_tools = []
    for tool in ['curl', 'wget', 'nc', 'netcat', 'python', 'python3', 'powershell']:
        try:
            if platform.system() == 'Windows':
                subprocess.check_output(f'where {tool}', shell=True, timeout=5)
            else:
                subprocess.check_output(f'which {tool}', shell=True, timeout=5)
            exfil_tools.append(tool)
        except:
            pass
    
    findings.append({
        'check': 'Exfiltration Tools',
        'status': 'found' if exfil_tools else 'none',
        'details': f"Found {len(exfil_tools)} tools available for exfiltration",
        'items': exfil_tools
    })
    
    # Check for removable media
    if platform.system() == 'Linux':
        try:
            media_output = subprocess.check_output(
                'lsblk -o NAME,TYPE,MOUNTPOINT | grep -E "disk|part"',
                shell=True,
                timeout=10
            ).decode()
            
            findings.append({
                'check': 'Removable Media',
                'status': 'found',
                'details': media_output
            })
        except:
            findings.append({
                'check': 'Removable Media',
                'status': 'none',
                'details': 'No removable media detected'
            })
    
    elif platform.system() == 'Windows':
        try:
            drives_output = subprocess.check_output(
                'wmic logicaldisk get caption,drivetype,volumename',
                shell=True,
                timeout=10
            ).decode()
            
            # DriveType 2 = Removable
            removable = [line for line in drives_output.split('\n') if '2' in line]
            
            findings.append({
                'check': 'Removable Media',
                'status': 'found' if removable else 'none',
                'details': f"Found {len(removable)} removable drives" if removable else 'No removable media',
                'items': removable
            })
        except Exception as e:
            findings.append({
                'check': 'Removable Media',
                'status': 'error',
                'details': str(e)
            })
    
    # Check for cloud storage sync folders
    cloud_paths = []
    if platform.system() == 'Linux':
        cloud_paths = [
            '~/Dropbox',
            '~/Google Drive',
            '~/OneDrive',
            '~/.dropbox'
        ]
    elif platform.system() == 'Windows':
        cloud_paths = [
            os.path.expandvars('%USERPROFILE%\\Dropbox'),
            os.path.expandvars('%USERPROFILE%\\Google Drive'),
            os.path.expandvars('%USERPROFILE%\\OneDrive')
        ]
    
    found_cloud = []
    for path in cloud_paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            found_cloud.append(path)
    
    findings.append({
        'check': 'Cloud Storage Folders',
        'status': 'found' if found_cloud else 'none',
        'details': f"Found {len(found_cloud)} cloud storage folders",
        'items': found_cloud
    })
    
    # Check DNS resolution (for DNS tunneling)
    try:
        if platform.system() == 'Windows':
            nslookup_output = subprocess.check_output(
                'nslookup google.com',
                shell=True,
                timeout=5
            ).decode()
        else:
            nslookup_output = subprocess.check_output(
                'nslookup google.com',
                shell=True,
                timeout=5
            ).decode()
        
        findings.append({
            'check': 'DNS Resolution',
            'status': 'available',
            'details': 'DNS resolution available (potential for DNS tunneling)'
        })
    except:
        findings.append({
            'check': 'DNS Resolution',
            'status': 'unavailable',
            'details': 'DNS resolution not available'
        })
    
    results['findings'] = findings
    return results
