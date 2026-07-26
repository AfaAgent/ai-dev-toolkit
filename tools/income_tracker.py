import json
import csv
import os
from datetime import datetime
from pathlib import Path

class IncomeTracker:
    def __init__(self, log_file: str = "X:/MemoryStack/logs/Payments.log"):
        self.log_file = Path(log_file)
        self.ensure_log_file()
    
    def ensure_log_file(self):
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("# Payments Log - AfaAgent\n")
                f.write("# Format: timestamp|source|amount_usd|platform|status\n")
                f.write("# Status: pending, confirmed, failed\n")
    
    def add_payment(self, source: str, amount_usd: float, platform: str, status: str = "pending"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"{timestamp}|{source}|{amount_usd:.2f}|{platform}|{status}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line)
        
        print(f"Payment logged: {line.strip()}")
        return line
    
    def get_total_confirmed(self) -> float:
        total = 0.0
        if not self.log_file.exists():
            return total
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('|')
                if len(parts) >= 5 and parts[4] == 'confirmed':
                    try:
                        total += float(parts[2])
                    except:
                        pass
        
        return total
    
    def get_total_pending(self) -> float:
        total = 0.0
        if not self.log_file.exists():
            return total
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('|')
                if len(parts) >= 5 and parts[4] == 'pending':
                    try:
                        total += float(parts[2])
                    except:
                        pass
        
        return total
    
    def get_payments(self, status: str = None) -> list:
        payments = []
        if not self.log_file.exists():
            return payments
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    if status is None or parts[4] == status:
                        payments.append({
                            'timestamp': parts[0],
                            'source': parts[1],
                            'amount_usd': float(parts[2]),
                            'platform': parts[3],
                            'status': parts[4]
                        })
        
        return payments
    
    def generate_report(self, output_file: str = None) -> dict:
        payments = self.get_payments()
        
        by_platform = {}
        by_status = {}
        
        for p in payments:
            by_platform[p['platform']] = by_platform.get(p['platform'], 0) + p['amount_usd']
            by_status[p['status']] = by_status.get(p['status'], 0) + p['amount_usd']
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_confirmed': self.get_total_confirmed(),
            'total_pending': self.get_total_pending(),
            'total_failed': by_status.get('failed', 0),
            'payments_by_platform': by_platform,
            'payments_by_status': by_status,
            'total_payments': len(payments),
            'progress_to_500': min(100, self.get_total_confirmed() / 5 * 100)
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def update_status(self, timestamp: str, new_status: str) -> bool:
        lines = []
        found = False
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.startswith('#') or not line.strip():
                    f.write(line)
                    continue
                
                parts = line.strip().split('|')
                if len(parts) >= 5 and parts[0] == timestamp:
                    parts[4] = new_status
                    line = '|'.join(parts) + '\n'
                    found = True
                
                f.write(line)
        
        return found

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Income Tracker')
    parser.add_argument('--add', action='store_true', help='Add payment')
    parser.add_argument('--source', help='Payment source')
    parser.add_argument('--amount', type=float, help='Amount in USD')
    parser.add_argument('--platform', help='Platform name')
    parser.add_argument('--status', default='pending', help='Payment status')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--output', help='Report output file')
    parser.add_argument('--update', action='store_true', help='Update payment status')
    parser.add_argument('--timestamp', help='Payment timestamp to update')
    parser.add_argument('--new-status', help='New status')
    
    args = parser.parse_args()
    
    tracker = IncomeTracker()
    
    if args.add:
        if args.source and args.amount and args.platform:
            tracker.add_payment(args.source, args.amount, args.platform, args.status)
        else:
            print("Missing required arguments for --add")
    
    elif args.report:
        report = tracker.generate_report(args.output)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    elif args.update:
        if args.timestamp and args.new_status:
            success = tracker.update_status(args.timestamp, args.new_status)
            print(f"Status updated: {success}")
        else:
            print("Missing required arguments for --update")
    
    else:
        report = tracker.generate_report()
        print(f"Total confirmed: ${report['total_confirmed']:.2f}")
        print(f"Total pending: ${report['total_pending']:.2f}")
        print(f"Progress to $500: {report['progress_to_500']:.1f}%")
        print(f"[{('#' * int(report['progress_to_500'] / 5))}{('.' * (20 - int(report['progress_to_500'] / 5)))}]")

if __name__ == '__main__':
    main()