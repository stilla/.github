#!/bin/bash
# Setup script for Slack Welcome Message Agent

echo "Setting up Slack Welcome Message Agent..."

# Install dependencies directly (virtual env not needed in this environment)
echo "Installing dependencies..."
python3 -m pip install --break-system-packages -r requirements.txt

# Install additional system dependencies
python3 -m pip install --break-system-packages python-dotenv psutil

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your Slack bot token!"
    echo "   Get your token from: https://api.slack.com/apps"
    echo ""
fi

# Make scripts executable
chmod +x slack_welcome_agent.py
chmod +x agent_controller.py

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Slack bot token"
echo "2. Run: python agent_controller.py start"
echo "3. Check status: python agent_controller.py status"
echo ""
echo "Usage commands:"
echo "  python agent_controller.py start    # Start the agent"
echo "  python agent_controller.py stop     # Stop the agent" 
echo "  python agent_controller.py restart  # Restart the agent"
echo "  python agent_controller.py status   # Check agent status"
echo "  python agent_controller.py update 'New message' '#channel'  # Manual update"