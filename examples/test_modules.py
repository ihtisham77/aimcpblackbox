#!/usr/bin/env python3
"""
Test script to run all security assessment modules
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import MODULE_MAP

def test_all_modules():
    """Test all available security modules"""
    print("=" * 70)
    print("C2 Server - Security Assessment Module Test")
    print("=" * 70)
    print()
    
    results = {}
    
    for module_name, module_func in MODULE_MAP.items():
        print(f"[*] Testing module: {module_name}")
        print("-" * 70)
        
        try:
            result = module_func()
            results[module_name] = result
            
            print(f"    Platform: {result.get('platform', 'Unknown')}")
            print(f"    Findings: {len(result.get('findings', []))}")
            
            # Show first finding as example
            if result.get('findings'):
                first_finding = result['findings'][0]
                print(f"    Example: {first_finding.get('check', 'N/A')} - {first_finding.get('status', 'N/A')}")
            
            print(f"    Status: ✓ SUCCESS")
            
        except Exception as e:
            print(f"    Status: ✗ ERROR - {str(e)}")
            results[module_name] = {'error': str(e)}
        
        print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    successful = sum(1 for r in results.values() if 'error' not in r)
    failed = len(results) - successful
    
    print(f"Total modules: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print()
    
    # Save results to file
    output_file = 'module_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"[+] Full results saved to: {output_file}")
    
    return results

if __name__ == '__main__':
    test_all_modules()
