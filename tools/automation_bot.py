import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path

class AutomationBot:
    def __init__(self, config_file: str = None):
        self.tasks = {}
        self.running = False
        self.log_file = Path("X:/MemoryStack/logs/automation.log")
        self.ensure_log_file()
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def ensure_log_file(self):
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("# Automation Bot Log\n")
    
    def log(self, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line)
        print(line.strip())
    
    def load_config(self, config_file: str):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.tasks = config.get('tasks', {})
        self.log(f"Loaded {len(self.tasks)} tasks from {config_file}")
    
    def save_config(self, config_file: str):
        config = {'tasks': self.tasks}
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self.log(f"Saved config to {config_file}")
    
    def add_task(self, task_id: str, task_config: dict):
        self.tasks[task_id] = task_config
        self.log(f"Added task: {task_id}")
    
    def remove_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.log(f"Removed task: {task_id}")
    
    def execute_task(self, task_id: str):
        if task_id not in self.tasks:
            self.log(f"Task not found: {task_id}")
            return
        
        task = self.tasks[task_id]
        self.log(f"Executing task: {task_id}")
        
        try:
            command = task.get('command', '')
            if command:
                os.system(command)
                self.log(f"Task {task_id} completed")
            else:
                self.log(f"No command defined for task {task_id}")
        except Exception as e:
            self.log(f"Error executing task {task_id}: {str(e)}")
    
    def run_scheduler(self):
        self.running = True
        self.log("Automation bot started")
        
        while self.running:
            now = datetime.now()
            
            for task_id, task in self.tasks.items():
                schedule_type = task.get('schedule', 'manual')
                
                if schedule_type == 'daily':
                    time_str = task.get('time', '00:00')
                    if now.strftime('%H:%M') == time_str:
                        self.execute_task(task_id)
                        time.sleep(60)
                
                elif schedule_type == 'hourly':
                    minute = task.get('minute', 0)
                    if now.minute == minute:
                        self.execute_task(task_id)
                        time.sleep(60)
                
                elif schedule_type == 'interval':
                    interval = task.get('interval', 3600)
                    last_run = task.get('last_run', 0)
                    if now.timestamp() - last_run >= interval:
                        self.execute_task(task_id)
                        task['last_run'] = now.timestamp()
            
            time.sleep(60)
    
    def start(self):
        thread = threading.Thread(target=self.run_scheduler)
        thread.daemon = True
        thread.start()
        self.log("Scheduler thread started")
    
    def stop(self):
        self.running = False
        self.log("Automation bot stopped")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automation Bot')
    parser.add_argument('--config', help='Config file')
    parser.add_argument('--add', help='Add task')
    parser.add_argument('--remove', help='Remove task')
    parser.add_argument('--execute', help='Execute task')
    parser.add_argument('--start', action='store_true', help='Start scheduler')
    
    args = parser.parse_args()
    
    bot = AutomationBot(args.config)
    
    if args.add:
        task_id = args.add
        task_config = {
            'command': input("Enter command: "),
            'schedule': input("Schedule type (manual/daily/hourly/interval): "),
        }
        
        if task_config['schedule'] == 'daily':
            task_config['time'] = input("Time (HH:MM): ")
        elif task_config['schedule'] == 'hourly':
            task_config['minute'] = int(input("Minute (0-59): "))
        elif task_config['schedule'] == 'interval':
            task_config['interval'] = int(input("Interval in seconds: "))
        
        bot.add_task(task_id, task_config)
        
        if args.config:
            bot.save_config(args.config)
    
    elif args.remove:
        bot.remove_task(args.remove)
        if args.config:
            bot.save_config(args.config)
    
    elif args.execute:
        bot.execute_task(args.execute)
    
    elif args.start:
        bot.start()
        print("Automation bot running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            bot.stop()
    
    else:
        print(f"Loaded {len(bot.tasks)} tasks:")
        for task_id, task in bot.tasks.items():
            print(f"  {task_id}: {task}")

if __name__ == '__main__':
    main()