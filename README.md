# Slack Welcome Message Agent

An intelligent agent that automatically updates and manages Slack welcome messages for the Cursor bot integration.

## Features

- 🤖 **Automated Updates**: Periodically updates welcome messages
- 📝 **Configurable Messages**: JSON-based message configuration
- 🔄 **Real-time Monitoring**: Continuous monitoring and status reporting
- 🛠️ **Easy Management**: Simple start/stop/restart controls
- 📊 **Rich Formatting**: Support for Slack blocks and rich text
- 🔧 **Flexible Configuration**: Environment-based configuration

## Quick Start

1. **Setup the environment:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure your Slack token:**
   ```bash
   cp .env.example .env
   # Edit .env and add your SLACK_BOT_TOKEN
   ```

3. **Start the agent:**
   ```bash
   python agent_controller.py start
   ```

4. **Check status:**
   ```bash
   python agent_controller.py status
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Optional
SLACK_CHANNEL=#general
UPDATE_INTERVAL=3600
LOG_LEVEL=INFO
```

### Welcome Messages

Edit `welcome_config.json` to customize your welcome messages:

```json
{
  "messages": [
    {
      "text": "Welcome to Cursor for Slack!",
      "blocks": [...],
      "channel": "#general"
    }
  ]
}
```

## Agent Commands

### Start the Agent
```bash
python agent_controller.py start
```

### Stop the Agent
```bash
python agent_controller.py stop
```

### Restart the Agent
```bash
python agent_controller.py restart
```

### Check Status
```bash
python agent_controller.py status
```

### Manual Message Update
```bash
python agent_controller.py update "New welcome message" "#channel"
```

## Slack Bot Setup

1. **Create a Slack App** at https://api.slack.com/apps
2. **Add Bot Token Scopes:**
   - `chat:write`
   - `chat:write.public`
   - `channels:read`
   - `groups:read`
3. **Install the app** to your workspace
4. **Copy the Bot User OAuth Token** (starts with `xoxb-`)

## Architecture

### Core Components

- **`slack_welcome_agent.py`**: Main agent implementation
- **`agent_controller.py`**: Management interface
- **`welcome_config.json`**: Message configuration
- **`requirements.txt`**: Python dependencies
- **`.env`**: Environment configuration

### How It Works

1. The agent loads message configurations from `welcome_config.json`
2. It connects to Slack using the WebClient API
3. Messages are posted according to the configured schedule
4. The controller manages the agent lifecycle (start/stop/status)
5. Logs are written to `slack_agent.log` for monitoring

## Message Format

Welcome messages support both simple text and rich Slack Block Kit formatting:

```json
{
  "text": "Fallback text",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Welcome to Cursor!* :cursor:"
      }
    }
  ]
}
```

## Monitoring & Logs

- **Log File**: `slack_agent.log`
- **Status Check**: `python agent_controller.py status`
- **Process Monitoring**: Uses PID file for process tracking

## Troubleshooting

### Agent Won't Start
1. Check if `SLACK_BOT_TOKEN` is set in `.env`
2. Verify Slack bot permissions
3. Check logs in `slack_agent.log`

### Messages Not Posting
1. Verify bot has `chat:write` permission
2. Check if bot is added to the target channel
3. Review Slack API error messages in logs

### Connection Issues
1. Test with: `python -c "from slack_welcome_agent import SlackWelcomeAgent; import asyncio; import os; agent = SlackWelcomeAgent(os.getenv('SLACK_BOT_TOKEN')); print(asyncio.run(agent.test_connection()))"`
2. Verify token format (should start with `xoxb-`)
3. Check network connectivity

## Development

### Running in Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Run agent directly
python slack_welcome_agent.py

# Or use the controller
python agent_controller.py start
```

### Testing
```bash
# Test Slack connection
python agent_controller.py status

# Send test message
python agent_controller.py update "Test message" "#test-channel"
```

## License

This project is open source and available under the MIT License.