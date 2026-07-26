import json
import os
import re
from datetime import datetime

class GitHubAnalyzer:
    def __init__(self):
        self.findings = []
    
    def analyze_paillier(self, content, filename):
        issues = []
        
        if 'p * q' in content or 'p*q' in content:
            issues.append({
                'type': 'WEAK_KEY_GENERATION',
                'severity': 'HIGH',
                'description': 'Direct multiplication p*q may leak timing information',
                'location': filename
            })
        
        if 'random' in content.lower() and 'seed' not in content.lower():
            issues.append({
                'type': 'INSECURE_RANDOM',
                'severity': 'MEDIUM',
                'description': 'Potential insecure random number generation',
                'location': filename
            })
        
        if 'mod_inverse' in content or 'modular_inverse' in content:
            if 'extended_gcd' not in content:
                issues.append({
                    'type': 'WEAK_INVERSE',
                    'severity': 'LOW',
                    'description': 'Modular inverse implementation without extended GCD',
                    'location': filename
                })
        
        return issues
    
    def analyze_ecdsa(self, content, filename):
        issues = []
        
        if 'verify' in content.lower():
            if 'curve' not in content.lower():
                issues.append({
                    'type': 'MISSING_CURVE_VALIDATION',
                    'severity': 'HIGH',
                    'description': 'Signature verification without curve point validation',
                    'location': filename
                })
        
        if 'k =' in content or 'k=' in content:
            if 'random' not in content.lower():
                issues.append({
                    'type': 'REUSED_NONCE',
                    'severity': 'CRITICAL',
                    'description': 'Potential nonce reuse in ECDSA signature generation',
                    'location': filename
                })
        
        if 'private' in content.lower() and 'key' in content.lower():
            if 'secure' not in content.lower() and 'zeroize' not in content.lower():
                issues.append({
                    'type': 'KEY_NOT_ZEROIZED',
                    'severity': 'MEDIUM',
                    'description': 'Private key may not be zeroized after use',
                    'location': filename
                })
        
        return issues
    
    def analyze_schnorr(self, content, filename):
        issues = []
        
        if 'challenge' in content.lower():
            if 'hash' not in content.lower():
                issues.append({
                    'type': 'WEAK_CHALLENGE',
                    'severity': 'HIGH',
                    'description': 'Schnorr challenge without hash function',
                    'location': filename
                })
        
        if 'commitment' in content.lower():
            if 'random' not in content.lower():
                issues.append({
                    'type': 'INSECURE_COMMITMENT',
                    'severity': 'MEDIUM',
                    'description': 'Commitment without random component',
                    'location': filename
                })
        
        return issues
    
    def analyze_mpc(self, content, filename):
        issues = []
        
        if 'share' in content.lower():
            if 'secret' in content.lower() and 'threshold' not in content.lower():
                issues.append({
                    'type': 'INSUFFICIENT_THRESHOLD',
                    'severity': 'HIGH',
                    'description': 'Secret sharing without threshold protection',
                    'location': filename
                })
        
        if 'communication' in content.lower():
            if 'encrypt' not in content.lower():
                issues.append({
                    'type': 'UNENCRYPTED_COMMUNICATION',
                    'severity': 'MEDIUM',
                    'description': 'MPC communication without encryption',
                    'location': filename
                })
        
        return issues
    
    def analyze_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            filename = os.path.basename(filepath)
            issues = []
            
            if 'paillier' in filename.lower():
                issues.extend(self.analyze_paillier(content, filename))
            
            if 'ecdsa' in filename.lower():
                issues.extend(self.analyze_ecdsa(content, filename))
            
            if 'schnorr' in filename.lower():
                issues.extend(self.analyze_schnorr(content, filename))
            
            if 'mpc' in filename.lower() or 'protocol' in filename.lower():
                issues.extend(self.analyze_mpc(content, filename))
            
            if 'crypto' in filename.lower():
                issues.extend(self.analyze_paillier(content, filename))
                issues.extend(self.analyze_ecdsa(content, filename))
            
            for issue in issues:
                self.findings.append({
                    **issue,
                    'filepath': filepath,
                    'timestamp': datetime.now().isoformat()
                })
            
            return issues
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            return []
    
    def analyze_directory(self, dirpath):
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file.endswith('.cpp') or file.endswith('.h') or file.endswith('.py') or file.endswith('.go'):
                    filepath = os.path.join(root, file)
                    self.analyze_file(filepath)
    
    def generate_report(self, output_file='github_analysis.json'):
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_findings': len(self.findings),
            'findings_by_severity': {
                'CRITICAL': len([f for f in self.findings if f['severity'] == 'CRITICAL']),
                'HIGH': len([f for f in self.findings if f['severity'] == 'HIGH']),
                'MEDIUM': len([f for f in self.findings if f['severity'] == 'MEDIUM']),
                'LOW': len([f for f in self.findings if f['severity'] == 'LOW']),
            },
            'findings_by_type': {},
            'estimated_bounty_range': {
                'min': sum(200 if f['severity'] == 'LOW' else 500 if f['severity'] == 'MEDIUM' else 2000 if f['severity'] == 'HIGH' else 50000 for f in self.findings),
                'max': sum(500 if f['severity'] == 'LOW' else 2000 if f['severity'] == 'MEDIUM' else 15000 if f['severity'] == 'HIGH' else 1000000 for f in self.findings),
            },
            'findings': self.findings,
        }
        
        for f in self.findings:
            report['findings_by_type'][f['type']] = report['findings_by_type'].get(f['type'], 0) + 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

if __name__ == '__main__':
    analyzer = GitHubAnalyzer()
    
    print("Analyzing local codebase for MPC/crypto vulnerabilities...")
    
    code_dirs = [
        'X:/',
    ]
    
    for code_dir in code_dirs:
        if os.path.exists(code_dir):
            analyzer.analyze_directory(code_dir)
    
    report = analyzer.generate_report()
    
    print(f"\n=== Analysis Report ===")
    print(f"Total findings: {report['total_findings']}")
    print(f"\nBy severity:")
    for sev, count in report['findings_by_severity'].items():
        if count > 0:
            print(f"  {sev}: {count}")
    
    print(f"\nBy type:")
    for typ, count in report['findings_by_type'].items():
        print(f"  {typ}: {count}")
    
    print(f"\nEstimated bounty range: ${report['estimated_bounty_range']['min']:,} - ${report['estimated_bounty_range']['max']:,}")
    
    if report['findings']:
        print(f"\nTop findings:")
        for f in report['findings'][:10]:
            print(f"  [{f['severity']}] {f['type']}: {f['description']}")