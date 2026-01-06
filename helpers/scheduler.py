#!/usr/bin/env python3
"""
NetScan Scheduled Scanning Module
Automate network scans using cron (Linux) or launchd (macOS)

Features:
- Create/manage scheduled scan jobs
- Configurable intervals (hourly, daily, weekly, custom)
- Email notifications for changes
- Automatic report generation
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
import platform


@dataclass
class ScheduledJob:
    """Scheduled scan job configuration"""
    name: str
    schedule: str  # cron expression or interval name
    scan_type: str = "quick"  # quick, full, arp
    notify_email: str = ""
    notify_on: str = "changes"  # always, changes, new_devices, never
    export_format: str = "json"
    enabled: bool = True
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_run: str = ""
    next_run: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


class ScheduleManager:
    """Manage scheduled network scans"""
    
    # Predefined schedules
    SCHEDULES = {
        'hourly': '0 * * * *',
        'daily': '0 9 * * *',  # 9 AM daily
        'nightly': '0 2 * * *',  # 2 AM daily
        'weekly': '0 9 * * 1',  # Monday 9 AM
        'monthly': '0 9 1 * *',  # 1st of month 9 AM
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or os.path.expanduser("~/.netscan"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_file = self.data_dir / "scheduled_jobs.json"
        self.script_dir = Path(__file__).parent.parent  # netscan root
        self.system = platform.system()
        
        # Load jobs
        self.jobs: Dict[str, ScheduledJob] = {}
        self._load_jobs()
    
    def _load_jobs(self):
        """Load jobs from file"""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file) as f:
                    data = json.load(f)
                    for name, job_data in data.items():
                        self.jobs[name] = ScheduledJob(**job_data)
            except Exception as e:
                print(f"Warning: Could not load jobs: {e}", file=sys.stderr)
    
    def _save_jobs(self):
        """Save jobs to file"""
        data = {name: job.to_dict() for name, job in self.jobs.items()}
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_cron_schedule(self, schedule: str) -> str:
        """Convert schedule name to cron expression"""
        return self.SCHEDULES.get(schedule.lower(), schedule)
    
    def _calculate_next_run(self, cron_expr: str) -> str:
        """Calculate next run time from cron expression"""
        try:
            from croniter import croniter
            cron = croniter(cron_expr, datetime.now())
            return cron.get_next(datetime).isoformat()
        except ImportError:
            # Approximate based on common schedules
            now = datetime.now()
            if cron_expr == self.SCHEDULES['hourly']:
                next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            elif cron_expr == self.SCHEDULES['daily']:
                next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
            elif cron_expr == self.SCHEDULES['weekly']:
                days_until_monday = (7 - now.weekday()) % 7
                if days_until_monday == 0 and now.hour >= 9:
                    days_until_monday = 7
                next_run = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
            else:
                next_run = now + timedelta(hours=1)  # Default
            return next_run.isoformat()
        except Exception:
            return "Unknown"
    
    def create_job(
        self,
        name: str,
        schedule: str = "daily",
        scan_type: str = "quick",
        notify_email: str = "",
        notify_on: str = "changes",
        export_format: str = "json"
    ) -> ScheduledJob:
        """Create a new scheduled scan job"""
        cron_expr = self._get_cron_schedule(schedule)
        
        job = ScheduledJob(
            name=name,
            schedule=cron_expr,
            scan_type=scan_type,
            notify_email=notify_email,
            notify_on=notify_on,
            export_format=export_format,
            next_run=self._calculate_next_run(cron_expr)
        )
        
        self.jobs[name] = job
        self._save_jobs()
        
        # Install system job
        if self.system == "Darwin":
            self._install_launchd(job)
        else:
            self._install_cron(job)
        
        return job
    
    def remove_job(self, name: str) -> bool:
        """Remove a scheduled job"""
        if name not in self.jobs:
            return False
        
        job = self.jobs[name]
        
        # Remove system job
        if self.system == "Darwin":
            self._uninstall_launchd(job)
        else:
            self._uninstall_cron(job)
        
        del self.jobs[name]
        self._save_jobs()
        return True
    
    def enable_job(self, name: str, enabled: bool = True) -> bool:
        """Enable or disable a job"""
        if name not in self.jobs:
            return False
        
        self.jobs[name].enabled = enabled
        self._save_jobs()
        
        # Update system job
        if enabled:
            if self.system == "Darwin":
                self._install_launchd(self.jobs[name])
            else:
                self._install_cron(self.jobs[name])
        else:
            if self.system == "Darwin":
                self._uninstall_launchd(self.jobs[name])
            else:
                self._uninstall_cron(self.jobs[name])
        
        return True
    
    def list_jobs(self) -> List[ScheduledJob]:
        """List all scheduled jobs"""
        return list(self.jobs.values())
    
    def get_job(self, name: str) -> Optional[ScheduledJob]:
        """Get a specific job"""
        return self.jobs.get(name)
    
    def run_job(self, name: str) -> bool:
        """Manually run a scheduled job"""
        job = self.jobs.get(name)
        if not job:
            return False
        
        # Run the scan
        self._execute_scan(job)
        
        # Update last run
        job.last_run = datetime.now().isoformat()
        job.next_run = self._calculate_next_run(job.schedule)
        self._save_jobs()
        
        return True
    
    def _execute_scan(self, job: ScheduledJob):
        """Execute a scan for a job"""
        # Build scan command
        netscan = self.script_dir / "netscan"
        
        if not netscan.exists():
            print(f"Error: netscan not found at {netscan}", file=sys.stderr)
            return
        
        # Output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.data_dir / "scheduled_scans"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{job.name}_{timestamp}.{job.export_format}"
        
        # Run scan based on type
        if job.scan_type == "quick":
            cmd = [str(netscan), "-q", "-o", str(output_file)]
        elif job.scan_type == "full":
            cmd = [str(netscan), "-f", "-o", str(output_file)]
        else:
            cmd = [str(netscan), "-a", "-o", str(output_file)]
        
        print(f"Running scheduled scan: {job.name}")
        print(f"  Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"  Scan completed: {output_file}")
                
                # Check for changes if needed
                if job.notify_on != "never" and job.notify_email:
                    self._check_and_notify(job, output_file)
            else:
                print(f"  Scan failed: {result.stderr}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print("  Scan timed out", file=sys.stderr)
        except Exception as e:
            print(f"  Error running scan: {e}", file=sys.stderr)
    
    def _check_and_notify(self, job: ScheduledJob, output_file: Path):
        """Check for changes and send notification"""
        # Find previous scan
        scan_dir = output_file.parent
        scans = sorted(scan_dir.glob(f"{job.name}_*.{job.export_format}"))
        
        if len(scans) < 2:
            return  # No previous scan to compare
        
        prev_scan = scans[-2]
        
        try:
            with open(prev_scan) as f:
                prev_data = json.load(f)
            with open(output_file) as f:
                curr_data = json.load(f)
            
            # Compare devices
            prev_devices = prev_data.get('devices', prev_data) if isinstance(prev_data, dict) else prev_data
            curr_devices = curr_data.get('devices', curr_data) if isinstance(curr_data, dict) else curr_data
            
            prev_macs = {d.get('mac', '') for d in prev_devices if isinstance(d, dict)}
            curr_macs = {d.get('mac', '') for d in curr_devices if isinstance(d, dict)}
            
            new_devices = curr_macs - prev_macs
            gone_devices = prev_macs - curr_macs
            
            should_notify = False
            if job.notify_on == "always":
                should_notify = True
            elif job.notify_on == "changes" and (new_devices or gone_devices):
                should_notify = True
            elif job.notify_on == "new_devices" and new_devices:
                should_notify = True
            
            if should_notify:
                subject = f"NetScan Alert: {job.name}"
                body = f"Scheduled scan completed: {job.name}\n\n"
                
                if new_devices:
                    body += f"New devices ({len(new_devices)}):\n"
                    for mac in new_devices:
                        body += f"  - {mac}\n"
                
                if gone_devices:
                    body += f"\nGone devices ({len(gone_devices)}):\n"
                    for mac in gone_devices:
                        body += f"  - {mac}\n"
                
                body += f"\nTotal devices: {len(curr_macs)}\n"
                body += f"Scan file: {output_file}\n"
                
                self._send_email(job.notify_email, subject, body)
        
        except Exception as e:
            print(f"  Could not check changes: {e}", file=sys.stderr)
    
    def _send_email(self, to: str, subject: str, body: str):
        """Send email notification"""
        try:
            # Try using mail command
            cmd = ['mail', '-s', subject, to]
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            proc.communicate(input=body.encode())
            
            if proc.returncode == 0:
                print(f"  Email sent to {to}")
            else:
                print(f"  Could not send email", file=sys.stderr)
        except Exception as e:
            print(f"  Email error: {e}", file=sys.stderr)
    
    def _install_launchd(self, job: ScheduledJob):
        """Install launchd job on macOS"""
        plist_dir = Path.home() / "Library/LaunchAgents"
        plist_dir.mkdir(parents=True, exist_ok=True)
        
        label = f"com.netscan.{job.name}"
        plist_file = plist_dir / f"{label}.plist"
        
        # Convert cron to launchd calendar intervals
        # Simple parsing for common cases
        cron_parts = job.schedule.split()
        if len(cron_parts) == 5:
            minute, hour, day, month, weekday = cron_parts
        else:
            minute, hour, day, month, weekday = "0", "*", "*", "*", "*"
        
        calendar_interval = {}
        if minute != "*":
            calendar_interval["Minute"] = int(minute)
        if hour != "*":
            calendar_interval["Hour"] = int(hour)
        if day != "*":
            calendar_interval["Day"] = int(day)
        if month != "*":
            calendar_interval["Month"] = int(month)
        if weekday != "*":
            calendar_interval["Weekday"] = int(weekday)
        
        # Python command to run the scan
        python_exec = sys.executable
        runner_script = self.data_dir / "run_scheduled.py"
        
        # Create runner script
        runner_content = f'''#!/usr/bin/env python3
import sys
sys.path.insert(0, "{self.script_dir / 'helpers'}")
from scheduler import ScheduleManager
mgr = ScheduleManager("{self.data_dir}")
mgr.run_job("{job.name}")
'''
        with open(runner_script, 'w') as f:
            f.write(runner_content)
        runner_script.chmod(0o755)
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exec}</string>
        <string>{runner_script}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
'''
        for key, value in calendar_interval.items():
            plist_content += f'''        <key>{key}</key>
        <integer>{value}</integer>
'''
        
        plist_content += '''    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>''' + str(self.data_dir / "scheduler.log") + '''</string>
    <key>StandardErrorPath</key>
    <string>''' + str(self.data_dir / "scheduler.log") + '''</string>
</dict>
</plist>
'''
        
        # Write plist
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        # Load the job
        subprocess.run(['launchctl', 'unload', str(plist_file)], capture_output=True)
        result = subprocess.run(['launchctl', 'load', str(plist_file)], capture_output=True)
        
        if result.returncode == 0:
            print(f"  Installed launchd job: {label}")
        else:
            print(f"  Warning: Could not load launchd job: {result.stderr.decode()}", file=sys.stderr)
    
    def _uninstall_launchd(self, job: ScheduledJob):
        """Remove launchd job on macOS"""
        label = f"com.netscan.{job.name}"
        plist_file = Path.home() / "Library/LaunchAgents" / f"{label}.plist"
        
        if plist_file.exists():
            subprocess.run(['launchctl', 'unload', str(plist_file)], capture_output=True)
            plist_file.unlink()
            print(f"  Removed launchd job: {label}")
    
    def _install_cron(self, job: ScheduledJob):
        """Install cron job on Linux"""
        # Create runner script
        runner_script = self.data_dir / f"run_{job.name}.sh"
        runner_content = f'''#!/bin/bash
cd "{self.script_dir}"
{sys.executable} "{self.script_dir / 'helpers/scheduler.py'}" --run "{job.name}"
'''
        with open(runner_script, 'w') as f:
            f.write(runner_content)
        runner_script.chmod(0o755)
        
        # Get current crontab
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
        except:
            current_crontab = ""
        
        # Remove existing entry for this job
        marker = f"# netscan:{job.name}"
        lines = [l for l in current_crontab.split('\n') if marker not in l]
        
        # Add new entry
        cron_line = f"{job.schedule} {runner_script} {marker}"
        lines.append(cron_line)
        
        # Install new crontab
        new_crontab = '\n'.join(filter(None, lines)) + '\n'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(new_crontab)
            temp_file = f.name
        
        try:
            subprocess.run(['crontab', temp_file], check=True)
            print(f"  Installed cron job: {job.name}")
        finally:
            os.unlink(temp_file)
    
    def _uninstall_cron(self, job: ScheduledJob):
        """Remove cron job on Linux"""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                return
            
            marker = f"# netscan:{job.name}"
            lines = [l for l in result.stdout.split('\n') if marker not in l]
            
            new_crontab = '\n'.join(filter(None, lines)) + '\n'
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(new_crontab)
                temp_file = f.name
            
            try:
                subprocess.run(['crontab', temp_file], check=True)
                print(f"  Removed cron job: {job.name}")
            finally:
                os.unlink(temp_file)
        except Exception as e:
            print(f"  Error removing cron job: {e}", file=sys.stderr)
        
        # Remove runner script
        runner_script = self.data_dir / f"run_{job.name}.sh"
        if runner_script.exists():
            runner_script.unlink()


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="NetScan Scheduled Scanning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scheduler.py --create daily_scan --schedule daily
  python scheduler.py --create hourly_check --schedule hourly --notify user@email.com
  python scheduler.py --create weekly --schedule "0 9 * * 0" --scan-type full
  python scheduler.py --list
  python scheduler.py --run daily_scan
  python scheduler.py --remove daily_scan
        '''
    )
    
    # Actions
    parser.add_argument('--create', metavar='NAME',
                       help='Create a new scheduled job')
    parser.add_argument('--remove', metavar='NAME',
                       help='Remove a scheduled job')
    parser.add_argument('--enable', metavar='NAME',
                       help='Enable a scheduled job')
    parser.add_argument('--disable', metavar='NAME',
                       help='Disable a scheduled job')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all scheduled jobs')
    parser.add_argument('--run', metavar='NAME',
                       help='Run a job immediately')
    parser.add_argument('--show', metavar='NAME',
                       help='Show job details')
    
    # Job options
    parser.add_argument('--schedule', '-s', default='daily',
                       help='Schedule (hourly, daily, nightly, weekly, monthly, or cron expression)')
    parser.add_argument('--scan-type', '-t', default='quick',
                       choices=['quick', 'full', 'arp'],
                       help='Type of scan')
    parser.add_argument('--notify', '-n', metavar='EMAIL',
                       help='Email for notifications')
    parser.add_argument('--notify-on', default='changes',
                       choices=['always', 'changes', 'new_devices', 'never'],
                       help='When to send notifications')
    parser.add_argument('--format', '-f', default='json',
                       choices=['json', 'csv', 'html'],
                       help='Export format')
    
    # Output
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output as JSON')
    
    args = parser.parse_args()
    
    manager = ScheduleManager()
    
    # List jobs
    if args.list:
        jobs = manager.list_jobs()
        
        if args.json:
            print(json.dumps([j.to_dict() for j in jobs], indent=2))
        else:
            if not jobs:
                print("No scheduled jobs.")
            else:
                print(f"\n{'Name':<20} {'Schedule':<20} {'Type':<10} {'Status':<10} {'Last Run':<20}")
                print("-" * 80)
                for job in jobs:
                    status = "Enabled" if job.enabled else "Disabled"
                    last_run = job.last_run[:19] if job.last_run else "Never"
                    # Show human-readable schedule
                    schedule_name = next((k for k, v in ScheduleManager.SCHEDULES.items() 
                                         if v == job.schedule), job.schedule)
                    print(f"{job.name:<20} {schedule_name:<20} {job.scan_type:<10} {status:<10} {last_run:<20}")
        return 0
    
    # Show job details
    if args.show:
        job = manager.get_job(args.show)
        if not job:
            print(f"Job not found: {args.show}")
            return 1
        
        if args.json:
            print(json.dumps(job.to_dict(), indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"Job Name: {job.name}")
            print(f"Schedule: {job.schedule}")
            
            # Show human-readable
            schedule_name = next((k for k, v in ScheduleManager.SCHEDULES.items() 
                                 if v == job.schedule), None)
            if schedule_name:
                print(f"         ({schedule_name})")
            
            print(f"Scan Type: {job.scan_type}")
            print(f"Export Format: {job.export_format}")
            print(f"Status: {'Enabled' if job.enabled else 'Disabled'}")
            print(f"Notify Email: {job.notify_email or 'None'}")
            print(f"Notify On: {job.notify_on}")
            print(f"Created: {job.created[:19] if job.created else 'Unknown'}")
            print(f"Last Run: {job.last_run[:19] if job.last_run else 'Never'}")
            print(f"Next Run: {job.next_run[:19] if job.next_run else 'Unknown'}")
            print(f"{'='*50}")
        return 0
    
    # Create job
    if args.create:
        print(f"Creating scheduled job: {args.create}")
        job = manager.create_job(
            name=args.create,
            schedule=args.schedule,
            scan_type=args.scan_type,
            notify_email=args.notify or "",
            notify_on=args.notify_on,
            export_format=args.format
        )
        print(f"✓ Created job: {job.name}")
        print(f"  Schedule: {job.schedule}")
        print(f"  Next run: {job.next_run[:19] if job.next_run else 'Unknown'}")
        return 0
    
    # Remove job
    if args.remove:
        if manager.remove_job(args.remove):
            print(f"✓ Removed job: {args.remove}")
        else:
            print(f"✗ Job not found: {args.remove}")
            return 1
        return 0
    
    # Enable job
    if args.enable:
        if manager.enable_job(args.enable, True):
            print(f"✓ Enabled job: {args.enable}")
        else:
            print(f"✗ Job not found: {args.enable}")
            return 1
        return 0
    
    # Disable job
    if args.disable:
        if manager.enable_job(args.disable, False):
            print(f"✓ Disabled job: {args.disable}")
        else:
            print(f"✗ Job not found: {args.disable}")
            return 1
        return 0
    
    # Run job
    if args.run:
        if manager.run_job(args.run):
            print(f"✓ Job completed: {args.run}")
        else:
            print(f"✗ Job not found: {args.run}")
            return 1
        return 0
    
    # No action specified
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
