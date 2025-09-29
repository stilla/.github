#!/usr/bin/env python3
"""
Quick status check for the Slack Welcome Message Agent
"""

import os
import sys
from agent_controller import AgentController

def main():
    """Quick status check and summary"""
    controller = AgentController()
    
    print("🤖 Slack Welcome Message Agent Status")
    print("=" * 40)
    
    # Check if agent is running
    is_running = controller.is_running()
    status_emoji = "🟢" if is_running else "🔴"
    status_text = "RUNNING" if is_running else "STOPPED"
    
    print(f"{status_emoji} Status: {status_text}")
    
    # Check configuration
    env_file = "/workspace/.env"
    config_file = "/workspace/welcome_config.json"
    
    print(f"📁 Config Files:")
    print(f"   .env file: {'✅' if os.path.exists(env_file) else '❌'}")
    print(f"   welcome_config.json: {'✅' if os.path.exists(config_file) else '❌'}")
    
    # Check environment variables
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    print(f"🔑 Slack Token: {'✅ Configured' if slack_token else '❌ Not set'}")
    
    if is_running:
        print(f"📊 Agent Details:")
        controller.status()
    else:
        print("\n💡 To start the agent:")
        print("   1. Set SLACK_BOT_TOKEN in .env file")
        print("   2. Run: python3 agent_controller.py start")
    
    print("\n🛠️  Available Commands:")
    print("   python3 agent_controller.py start    # Start agent")
    print("   python3 agent_controller.py stop     # Stop agent")
    print("   python3 agent_controller.py status   # Detailed status")
    print("   python3 quick_status.py              # Quick overview")

if __name__ == "__main__":
    main()