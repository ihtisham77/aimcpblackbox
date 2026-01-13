import os
import platform
import subprocess

def check_lateral_movement():
    """Check for lateral movement opportunities"""
    results = {
        'module': 'lateral_movement',
        'findings': [],
        'platform': platform.system()
    }
    
    if platform.system() == 'Linux':
        results['findings'].extend(check_linux_lateral())
    elif platform.system() == 'Windows':
        results['findings'].extend(check_windows_lateral())
    
    return results

def check_linux_lateral():
    """Linux lateral movement checks"""
    findings = []
    
    # Check for SSH access to other hosts
    ssh_config_path = os.path.expanduser('~/.ssh/config')
    if os.path.exists(ssh_config_path):
        try:
            with open(ssh_config_path, 'r') as f:
                config = f.read()
            
            hosts = [line.split()[1] for line in config.split('\n') if line.strip().startswith('Host ')]
            findings.append({
                'check': 'SSH Config Hosts',
                'status': 'found' if hosts else 'none',
                'details': f"Found {len(hosts)} configured SSH hosts",
                'items': hosts
            })
        except:
            findings.append({
                'check': 'SSH Config Hosts',
                'status': 'no_access',
                'details': 'Cannot read SSH config'
            })
    else:
        findings.append({
            'check': 'SSH Config Hosts',
            'status': 'none',
            'details': 'No SSH config file found'
        })
    
    # Check known_hosts
    known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
    if os.path.exists(known_hosts_path):
        try:
            with open(known_hosts_path, 'r') as f:
                hosts = f.readlines()
            
            findings.append({
                'check': 'SSH Known Hosts',
                'status': 'found',
                'details': f"Found {len(hosts)} known hosts",
                'count': len(hosts)
            })
        except:
            findings.append({
                'check': 'SSH Known Hosts',
                'status': 'no_access',
                'details': 'Cannot read known_hosts'
            })
    
    # Check for NFS shares
    try:
        showmount_output = subprocess.check_output(
            'showmount -e 2>/dev/null',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'NFS Shares',
            'status': 'found' if showmount_output.strip() else 'none',
            'details': showmount_output if showmount_output.strip() else 'No NFS shares'
        })
    except:
        findings.append({
            'check': 'NFS Shares',
            'status': 'none',
            'details': 'No NFS shares or showmount not available'
        })
    
    # Check for SMB/CIFS mounts
    try:
        mount_output = subprocess.check_output(
            'mount | grep cifs',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'SMB/CIFS Mounts',
            'status': 'found' if mount_output.strip() else 'none',
            'details': mount_output if mount_output.strip() else 'No SMB/CIFS mounts'
        })
    except:
        findings.append({
            'check': 'SMB/CIFS Mounts',
            'status': 'none',
            'details': 'No SMB/CIFS mounts found'
        })
    
    # Check ARP cache for local network hosts
    try:
        arp_output = subprocess.check_output(
            'arp -a 2>/dev/null || ip neigh show',
            shell=True,
            timeout=10
        ).decode()
        
        hosts = [line for line in arp_output.split('\n') if line.strip()]
        findings.append({
            'check': 'ARP Cache (Local Hosts)',
            'status': 'found',
            'details': f"Found {len(hosts)} hosts in ARP cache",
            'items': hosts[:20]
        })
    except Exception as e:
        findings.append({
            'check': 'ARP Cache',
            'status': 'error',
            'details': str(e)
        })
    
    return findings

def check_windows_lateral():
    """Windows lateral movement checks"""
    findings = []
    
    # Check network shares
    try:
        shares_output = subprocess.check_output(
            'net share',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Network Shares',
            'status': 'found',
            'details': shares_output
        })
    except Exception as e:
        findings.append({
            'check': 'Network Shares',
            'status': 'error',
            'details': str(e)
        })
    
    # Check mapped drives
    try:
        drives_output = subprocess.check_output(
            'net use',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Mapped Drives',
            'status': 'found' if 'OK' in drives_output else 'none',
            'details': drives_output
        })
    except Exception as e:
        findings.append({
            'check': 'Mapped Drives',
            'status': 'error',
            'details': str(e)
        })
    
    # Check domain computers
    try:
        computers_output = subprocess.check_output(
            'net view /domain',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Domain Computers',
            'status': 'found',
            'details': computers_output
        })
    except:
        findings.append({
            'check': 'Domain Computers',
            'status': 'none',
            'details': 'Not in a domain or no access'
        })
    
    # Check sessions
    try:
        sessions_output = subprocess.check_output(
            'net session',
            shell=True,
            timeout=10
        ).decode()
        
        findings.append({
            'check': 'Active Sessions',
            'status': 'found' if sessions_output.strip() else 'none',
            'details': sessions_output if sessions_output.strip() else 'No active sessions'
        })
    except Exception as e:
        findings.append({
            'check': 'Active Sessions',
            'status': 'error',
            'details': str(e)
        })
    
    # Check ARP cache
    try:
        arp_output = subprocess.check_output(
            'arp -a',
            shell=True,
            timeout=10
        ).decode()
        
        hosts = [line for line in arp_output.split('\n') if line.strip() and 'Interface' not in line]
        findings.append({
            'check': 'ARP Cache (Local Hosts)',
            'status': 'found',
            'details': f"Found {len(hosts)} hosts in ARP cache",
            'items': hosts[:20]
        })
    except Exception as e:
        findings.append({
            'check': 'ARP Cache',
            'status': 'error',
            'details': str(e)
        })
    
    return findings
