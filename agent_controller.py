#!/usr/bin/env python3
"""
Slack Welcome Agent Controller

This script provides control interface for the Slack welcome message agent.
Use this to start, stop, check status, and manage the agent.
"""

import os
import sys
import json
import signal
import subprocess
import time
from pathlib import Path
import psutil

class AgentController:
    """Controller for managing the Slack welcome agent"""
    
    def __init__(self):
        self.agent_script = "/workspace/slack_welcome_agent.py"
        self.pid_file = "/workspace/agent.pid"
        self.log_file = "/workspace/slack_agent.log"
        
    def is_running(self) -> bool:
        """Check if the agent is currently running"""
        if not os.path.exists(self.pid_file):
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists and is our agent
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                if 'slack_welcome_agent.py' in ' '.join(proc.cmdline()):
                    return True
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Clean up stale PID file
        self._cleanup_pid_file()
        return False
    
    def start(self) -> bool:
        """Start the agent"""
        if self.is_running():
            print("Agent is already running")
            return True
        
        # Check if environment is configured
        if not os.getenv('SLACK_BOT_TOKEN'):
            print("ERROR: SLACK_BOT_TOKEN environment variable not set")
            print("Please set your Slack bot token or copy .env.example to .env and configure it")
            return False
        
        try:
            # Start the agent in background
            process = subprocess.Popen(
                [sys.executable, self.agent_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Give it a moment to start
            time.sleep(2)
            
            if self.is_running():
                print(f"Agent started successfully (PID: {process.pid})")
                print(f"Logs: {self.log_file}")
                return True
            else:
                print("Failed to start agent")
                return False
                
        except Exception as e:
            print(f"Error starting agent: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the agent"""
        if not self.is_running():
            print("Agent is not running")
            return True
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Send SIGTERM
            os.kill(pid, signal.SIGTERM)
            
            # Wait for graceful shutdown
            for _ in range(10):
                if not self.is_running():
                    print("Agent stopped successfully")
                    return True
                time.sleep(1)
            
            # Force kill if needed
            try:
                os.kill(pid, signal.SIGKILL)
                print("Agent force-stopped")
            except ProcessLookupError:
                pass
            
            self._cleanup_pid_file()
            return True
            
        except Exception as e:
            print(f"Error stopping agent: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart the agent"""
        print("Restarting agent...")
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self):
        """Show agent status"""
        running = self.is_running()
        print(f"Agent Status: {'RUNNING' if running else 'STOPPED'}")
        
        if running:
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                proc = psutil.Process(pid)
                print(f"PID: {pid}")
                print(f"Memory Usage: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
                print(f"CPU Percent: {proc.cpu_percent():.1f}%")
                print(f"Started: {proc.create_time()}")
            except Exception:
                print("Could not get detailed status")
        
        # Show recent logs
        if os.path.exists(self.log_file):
            print(f"\nRecent logs ({self.log_file}):")
            try:
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:  # Last 10 lines
                        print(f"  {line.strip()}")
            except Exception:
                print("  Could not read log file")
    
    def update_message(self, text: str, channel: str = None):
        """Manually trigger a welcome message update"""
        if not self.is_running():
            print("Agent is not running. Starting temporarily...")
            # Run a one-time update
            try:
                import asyncio
                from slack_welcome_agent import SlackWelcomeAgent, WelcomeMessage
                
                token = os.getenv('SLACK_BOT_TOKEN')
                if not token:
                    print("ERROR: SLACK_BOT_TOKEN not set")
                    return
                
                agent = SlackWelcomeAgent(token)
                message = WelcomeMessage(text=text, channel=channel)
                success = asyncio.run(agent.update_welcome_message(message, channel))
                
                if success:
                    print("Welcome message updated successfully")
                else:
                    print("Failed to update welcome message")
                    
            except Exception as e:
                print(f"Error updating message: {e}")
        else:
            print("Agent is running - it will update messages automatically")
            print("To modify the welcome message, edit welcome_config.json")
    
    def _cleanup_pid_file(self):
        """Remove stale PID file"""
        try:
            os.remove(self.pid_file)
        except FileNotFoundError:
            pass

def main():
    """Main CLI interface"""
    controller = AgentController()
    
    if len(sys.argv) < 2:
        print("Usage: python agent_controller.py <command>")
        print("Commands: start, stop, restart, status, update")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        controller.start()
    elif command == "stop":
        controller.stop()
    elif command == "restart":
        controller.restart()
    elif command == "status":
        controller.status()
    elif command == "update":
        text = sys.argv[2] if len(sys.argv) > 2 else "Welcome to Cursor for Slack! Here's how to use it:"
        channel = sys.argv[3] if len(sys.argv) > 3 else None
        controller.update_message(text, channel)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, restart, status, update")

if __name__ == "__main__":
    main()