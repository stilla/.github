#!/usr/bin/env python3
"""
Slack Welcome Message Update Agent

This agent monitors and updates the Slack welcome message for the Cursor bot.
It can be configured to update messages based on various triggers like time,
events, or manual updates.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    print("Installing slack_sdk...")
    import subprocess
    subprocess.check_call(["pip", "install", "slack-sdk"])
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/slack_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WelcomeMessage:
    """Data class for welcome message configuration"""
    text: str
    blocks: Optional[List[Dict]] = None
    channel: Optional[str] = None
    thread_ts: Optional[str] = None

class SlackWelcomeAgent:
    """Agent responsible for updating Slack welcome messages"""
    
    def __init__(self, token: str, config_file: str = "/workspace/welcome_config.json"):
        """
        Initialize the Slack Welcome Agent
        
        Args:
            token: Slack bot token
            config_file: Path to welcome message configuration file
        """
        self.client = WebClient(token=token)
        self.config_file = config_file
        self.running = False
        self.welcome_messages = self._load_welcome_messages()
        
    def _load_welcome_messages(self) -> List[WelcomeMessage]:
        """Load welcome message configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return [WelcomeMessage(**msg) for msg in data.get('messages', [])]
            else:
                # Create default welcome messages
                default_messages = [
                    {
                        "text": "Welcome to Cursor for Slack! Here's how to use it:",
                        "blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "*Welcome to Cursor for Slack!* :cursor:\n\nHere's how to get started:"
                                }
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "• Type `@Cursor help` for assistance\n• Use `@Cursor code` to get coding help\n• Try `@Cursor review` for code reviews\n• Say `@Cursor explain` to understand code"
                                }
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "context",
                                "elements": [
                                    {
                                        "type": "mrkdwn",
                                        "text": f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
                                    }
                                ]
                            }
                        ]
                    }
                ]
                self._save_welcome_messages(default_messages)
                return [WelcomeMessage(**msg) for msg in default_messages]
        except Exception as e:
            logger.error(f"Failed to load welcome messages: {e}")
            return []
    
    def _save_welcome_messages(self, messages: List[Dict]):
        """Save welcome messages to configuration file"""
        try:
            config = {"messages": messages}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved welcome messages to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save welcome messages: {e}")
    
    async def update_welcome_message(self, message: WelcomeMessage, channel: str = None) -> bool:
        """
        Update a welcome message in Slack
        
        Args:
            message: WelcomeMessage object containing the message data
            channel: Override channel for the message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_channel = channel or message.channel or os.getenv('SLACK_CHANNEL', '#general')
            
            if message.blocks:
                response = self.client.chat_postMessage(
                    channel=target_channel,
                    text=message.text,
                    blocks=message.blocks,
                    thread_ts=message.thread_ts
                )
            else:
                response = self.client.chat_postMessage(
                    channel=target_channel,
                    text=message.text,
                    thread_ts=message.thread_ts
                )
            
            logger.info(f"Successfully posted welcome message to {target_channel}")
            return True
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Failed to update welcome message: {e}")
            return False
    
    async def update_all_welcome_messages(self, channel: str = None) -> int:
        """
        Update all configured welcome messages
        
        Args:
            channel: Override channel for all messages
            
        Returns:
            int: Number of successfully updated messages
        """
        success_count = 0
        for message in self.welcome_messages:
            if await self.update_welcome_message(message, channel):
                success_count += 1
        
        logger.info(f"Updated {success_count}/{len(self.welcome_messages)} welcome messages")
        return success_count
    
    def add_welcome_message(self, text: str, blocks: List[Dict] = None, channel: str = None) -> bool:
        """Add a new welcome message to the configuration"""
        try:
            new_message = WelcomeMessage(text=text, blocks=blocks, channel=channel)
            self.welcome_messages.append(new_message)
            
            # Save to file
            messages_data = []
            for msg in self.welcome_messages:
                msg_dict = {"text": msg.text}
                if msg.blocks:
                    msg_dict["blocks"] = msg.blocks
                if msg.channel:
                    msg_dict["channel"] = msg.channel
                if msg.thread_ts:
                    msg_dict["thread_ts"] = msg.thread_ts
                messages_data.append(msg_dict)
            
            self._save_welcome_messages(messages_data)
            logger.info("Added new welcome message")
            return True
        except Exception as e:
            logger.error(f"Failed to add welcome message: {e}")
            return False
    
    async def start_monitoring(self, update_interval: int = 3600):
        """
        Start monitoring and periodic updates
        
        Args:
            update_interval: Interval in seconds between automatic updates
        """
        self.running = True
        logger.info(f"Starting Slack welcome agent with {update_interval}s interval")
        
        while self.running:
            try:
                await self.update_all_welcome_messages()
                await asyncio.sleep(update_interval)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping agent")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False
        logger.info("Stopping Slack welcome agent")
    
    def is_running(self) -> bool:
        """Check if the agent is currently running"""
        return self.running
    
    async def test_connection(self) -> bool:
        """Test the Slack connection"""
        try:
            response = self.client.auth_test()
            logger.info(f"Connected to Slack as {response['user']} in team {response['team']}")
            return True
        except SlackApiError as e:
            logger.error(f"Slack connection failed: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

def main():
    """Main function to run the agent"""
    # Load environment variables
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if not slack_token:
        logger.error("SLACK_BOT_TOKEN environment variable not set")
        return
    
    # Create and start the agent
    agent = SlackWelcomeAgent(slack_token)
    
    # Test connection first
    if not asyncio.run(agent.test_connection()):
        logger.error("Failed to connect to Slack, exiting")
        return
    
    try:
        # Start monitoring
        asyncio.run(agent.start_monitoring())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Agent crashed: {e}")

if __name__ == "__main__":
    main()