"""Data Access Assessment Module"""

import os
import platform
import subprocess
import glob


def check_data_access():
    """Check for sensitive data access opportunities"""
    results = {
        'module': 'data_access',
        'findings': [],
        'risk_level': 'info'
    }
    
    results['findings'].extend(check_sensitive_files())
    results['findings'].extend(check_databases())
    results['findings'].extend(check_documents())
    
    if any('HIGH' in str(f) for f in results['findings']):
        results['risk_level'] = 'high'
    elif any('MEDIUM' in str(f) for f in results['findings']):
        results['risk_level'] = 'medium'
    
    return results


def check_sensitive_files():
    """Check for sensitive files"""
    findings = []
    
    try:
        sensitive_patterns = [
            '*.key',
            '*.pem',
            '*.p12',
            '*.pfx',
            '*password*',
            '*secret*',
            '*.env',
            'id_rsa',
            'id_dsa',
            'id_ecdsa',
            'id_ed25519'
        ]
        
        home_dir = os.path.expanduser('~')
        found_files = []
        
        for pattern in sensitive_patterns:
            try:
                files = glob.glob(os.path.join(home_dir, '**', pattern), recursive=True)
                found_files.extend(files[:5])  # Limit results
            except:
                pass
        
        if found_files:
            findings.append({
                'check': 'Sensitive Files',
                'status': 'FOUND',
                'details': f'Found {len(found_files)} potentially sensitive files',
                'items': [os.path.basename(f) for f in found_files],
                'risk': 'HIGH'
            })
    except Exception as e:
        findings.append({'check': 'Sensitive Files', 'status': 'ERROR', 'error': str(e)})
    
    return findings


def check_databases():
    """Check for database files and connections"""
    findings = []
    
    try:
        db_patterns = [
            '*.db',
            '*.sqlite',
            '*.sqlite3',
            '*.mdb',
            '*.accdb'
        ]
        
        home_dir = os.path.expanduser('~')
        found_dbs = []
        
        for pattern in db_patterns:
            try:
                dbs = glob.glob(os.path.join(home_dir, '**', pattern), recursive=True)
                found_dbs.extend(dbs[:10])
            except:
                pass
        
        if found_dbs:
            findings.append({
                'check': 'Database Files',
                'status': 'FOUND',
                'details': f'Found {len(found_dbs)} database files',
                'items': [os.path.basename(f) for f in found_dbs],
                'risk': 'HIGH'
            })
    except:
        pass
    
    # Check for running database services
    try:
        system = platform.system()
        db_ports = ['3306', '5432', '1433', '27017', '6379']  # MySQL, PostgreSQL, MSSQL, MongoDB, Redis
        
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
            running_dbs = []
            for port in db_ports:
                if f':{port}' in result.stdout:
                    running_dbs.append(port)
            
            if running_dbs:
                findings.append({
                    'check': 'Running Database Services',
                    'status': 'FOUND',
                    'details': f'Found {len(running_dbs)} database services',
                    'ports': running_dbs,
                    'risk': 'HIGH'
                })
    except:
        pass
    
    return findings


def check_documents():
    """Check for accessible documents"""
    findings = []
    
    try:
        doc_patterns = [
            '*.pdf',
            '*.doc',
            '*.docx',
            '*.xls',
            '*.xlsx',
            '*.txt'
        ]
        
        # Check common document locations
        doc_dirs = []
        if platform.system() == 'Windows':
            doc_dirs = [
                os.path.expandvars(r'%USERPROFILE%\Documents'),
                os.path.expandvars(r'%USERPROFILE%\Desktop'),
                os.path.expandvars(r'%USERPROFILE%\Downloads')
            ]
        else:
            doc_dirs = [
                os.path.expanduser('~/Documents'),
                os.path.expanduser('~/Desktop'),
                os.path.expanduser('~/Downloads')
            ]
        
        total_docs = 0
        for doc_dir in doc_dirs:
            if os.path.exists(doc_dir):
                try:
                    files = os.listdir(doc_dir)
                    docs = [f for f in files if any(f.endswith(ext.replace('*', '')) for ext in doc_patterns)]
                    total_docs += len(docs)
                except:
                    pass
        
        if total_docs > 0:
            findings.append({
                'check': 'Accessible Documents',
                'status': 'FOUND',
                'details': f'Found {total_docs} accessible documents',
                'count': total_docs,
                'risk': 'MEDIUM'
            })
    except:
        pass
    
    # Check for cloud storage folders
    try:
        cloud_dirs = []
        if platform.system() == 'Windows':
            cloud_dirs = [
                os.path.expandvars(r'%USERPROFILE%\OneDrive'),
                os.path.expandvars(r'%USERPROFILE%\Dropbox'),
                os.path.expandvars(r'%USERPROFILE%\Google Drive')
            ]
        else:
            cloud_dirs = [
                os.path.expanduser('~/OneDrive'),
                os.path.expanduser('~/Dropbox'),
                os.path.expanduser('~/Google Drive')
            ]
        
        found_cloud = [d for d in cloud_dirs if os.path.exists(d)]
        if found_cloud:
            findings.append({
                'check': 'Cloud Storage Folders',
                'status': 'FOUND',
                'details': f'Found {len(found_cloud)} cloud storage folders',
                'items': [os.path.basename(d) for d in found_cloud],
                'risk': 'HIGH'
            })
    except:
        pass
    
    return findings


if __name__ == '__main__':
    import json
    result = check_data_access()
    print(json.dumps(result, indent=2))
