"""Persistence Mechanisms Detection Module"""

import os
import platform
import subprocess


def check_persistence():
    """Check for persistence mechanisms"""
    results = {
        'module': 'persistence',
        'findings': [],
        'risk_level': 'info'
    }
    
    system = platform.system()
    
    if system == 'Linux':
        results['findings'].extend(check_linux_persistence())
    elif system == 'Windows':
        results['findings'].extend(check_windows_persistence())
    
    if any('HIGH' in str(f) for f in results['findings']):
        results['risk_level'] = 'high'
    elif any('MEDIUM' in str(f) for f in results['findings']):
        results['risk_level'] = 'medium'
    
    return results


def check_linux_persistence():
    """Check Linux persistence mechanisms"""
    findings = []
    
    # Check cron jobs
    try:
        cron_dirs = ['/etc/cron.d', '/etc/cron.daily', '/etc/cron.hourly', 
                     '/etc/cron.monthly', '/etc/cron.weekly', '/var/spool/cron']
        for cron_dir in cron_dirs:
            if os.path.exists(cron_dir):
                files = os.listdir(cron_dir)
                if files:
                    findings.append({
                        'check': f'Cron Jobs - {cron_dir}',
                        'status': 'FOUND',
                        'details': f'Found {len(files)} cron entries',
                        'items': files[:10],
                        'risk': 'MEDIUM'
                    })
    except Exception as e:
        findings.append({'check': 'Cron Jobs', 'status': 'ERROR', 'error': str(e)})
    
    # Check systemd services
    try:
        result = subprocess.run(
            ['systemctl', 'list-unit-files', '--type=service'],
            capture_output=True, text=True, timeout=10
        )
        services = result.stdout.split('\n')
        enabled_services = [s for s in services if 'enabled' in s]
        findings.append({
            'check': 'Systemd Services',
            'status': 'FOUND',
            'details': f'Found {len(enabled_services)} enabled services',
            'count': len(enabled_services),
            'risk': 'INFO'
        })
    except:
        pass
    
    # Check bashrc and profile files
    try:
        rc_files = [
            os.path.expanduser('~/.bashrc'),
            os.path.expanduser('~/.bash_profile'),
            os.path.expanduser('~/.profile'),
            '/etc/profile',
            '/etc/bash.bashrc'
        ]
        found_files = [f for f in rc_files if os.path.exists(f)]
        findings.append({
            'check': 'Shell RC Files',
            'status': 'FOUND',
            'details': f'Found {len(found_files)} shell configuration files',
            'items': found_files,
            'risk': 'MEDIUM'
        })
    except:
        pass
    
    # Check .ssh/authorized_keys
    try:
        ssh_key_file = os.path.expanduser('~/.ssh/authorized_keys')
        if os.path.exists(ssh_key_file):
            with open(ssh_key_file, 'r') as f:
                keys = f.readlines()
            findings.append({
                'check': 'SSH Authorized Keys',
                'status': 'FOUND',
                'details': f'Found {len(keys)} authorized SSH keys',
                'count': len(keys),
                'risk': 'HIGH'
            })
    except:
        pass
    
    return findings


def check_windows_persistence():
    """Check Windows persistence mechanisms"""
    findings = []
    
    # Check startup folder
    try:
        startup_paths = [
            os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'),
            r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup'
        ]
        for path in startup_paths:
            if os.path.exists(path):
                files = os.listdir(path)
                if files:
                    findings.append({
                        'check': f'Startup Folder - {path}',
                        'status': 'FOUND',
                        'details': f'Found {len(files)} startup items',
                        'items': files,
                        'risk': 'HIGH'
                    })
    except Exception as e:
        findings.append({'check': 'Startup Folders', 'status': 'ERROR', 'error': str(e)})
    
    # Check Run registry keys
    try:
        run_keys = [
            r'HKLM\Software\Microsoft\Windows\CurrentVersion\Run',
            r'HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce',
            r'HKCU\Software\Microsoft\Windows\CurrentVersion\Run',
            r'HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce'
        ]
        for key in run_keys:
            result = subprocess.run(
                ['reg', 'query', key],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout:
                entries = [line for line in result.stdout.split('\n') if 'REG_' in line]
                if entries:
                    findings.append({
                        'check': f'Registry Run Key - {key}',
                        'status': 'FOUND',
                        'details': f'Found {len(entries)} entries',
                        'count': len(entries),
                        'risk': 'HIGH'
                    })
    except:
        pass
    
    # Check scheduled tasks
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/fo', 'LIST'],
            capture_output=True, text=True, timeout=30
        )
        tasks = result.stdout.split('\n\n')
        findings.append({
            'check': 'Scheduled Tasks',
            'status': 'FOUND',
            'details': f'Found {len(tasks)} scheduled tasks',
            'count': len(tasks),
            'risk': 'MEDIUM'
        })
    except:
        pass
    
    # Check services
    try:
        result = subprocess.run(
            ['sc', 'query', 'type=', 'service', 'state=', 'all'],
            capture_output=True, text=True, timeout=30
        )
        services = [line for line in result.stdout.split('\n') if 'SERVICE_NAME' in line]
        findings.append({
            'check': 'Windows Services',
            'status': 'FOUND',
            'details': f'Found {len(services)} services',
            'count': len(services),
            'risk': 'INFO'
        })
    except:
        pass
    
    return findings


if __name__ == '__main__':
    import json
    result = check_persistence()
    print(json.dumps(result, indent=2))
