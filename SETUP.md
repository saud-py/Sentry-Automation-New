# Sentry Alert Automation - Setup Guide

This guide will walk you through setting up the automated Sentry alert system for your organization.

## Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** installed on your system
2. **Access to your Sentry organization** with admin permissions
3. **Access to your Slack workspace** with admin permissions
4. **Git** (for cloning the repository)

## Step 1: Installation

### Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd saud

# Install Python dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Test that all dependencies are installed
python -c "import requests, yaml, click, rich, slack_sdk; print('All dependencies installed successfully!')"
```

## Step 2: Sentry Configuration

### Generate Sentry Auth Token

1. **Go to your Sentry organization**
   - Navigate to Settings → Developer Settings → New Internal Integration

2. **Create the integration**
   - Name: `Alert Automation`
   - Description: `Automated alert rule creation for escalating issues`

3. **Add required permissions**
   - `project:read` - To read project information
   - `project:write` - To create and manage alert rules
   - `org:read` - To read organization information

4. **Save and copy the token**
   - The token will look like: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Configure Sentry Token

Run the setup script:

```bash
python scripts/setup_sentry_token.py
```

This script will:
- Guide you through entering your Sentry token
- Test the connection to your organization
- Save the configuration to `.env` file

## Step 3: Slack Configuration

### Create Slack App

1. **Go to Slack API**
   - Visit https://api.slack.com/apps
   - Click "Create New App" → "From scratch"

2. **Configure the app**
   - App Name: `Sentry Alert Bot`
   - Workspace: Select your workspace

3. **Add required scopes**
   - Go to "OAuth & Permissions"
   - Add these Bot Token Scopes:
     - `chat:write` - To send messages
     - `channels:read` - To read channel information
     - `channels:join` - To join channels (optional)

4. **Install the app**
   - Go to "Install App" in the sidebar
   - Click "Install to Workspace"
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### Create Alert Channel

1. **Create the alert channel**
   - In your Slack workspace, create a channel named `#sentry-alerts`
   - Make it public or private (ensure the bot can access it)

2. **Invite the bot**
   - Invite the bot user to the `#sentry-alerts` channel
   - Or make the channel public so the bot can join

### Configure Slack Integration

Run the verification script:

```bash
python scripts/verify_slack_integration.py
```

This script will:
- Guide you through entering your Slack bot token
- Automatically detect your workspace ID
- Test the connection and message sending
- Save the configuration to `.env` file

## Step 4: Verify Configuration

### Test Connections

```bash
# Test Sentry connection
python src/main.py --verify-connection

# Test Slack integration
python src/main.py --test-slack

# List all projects
python scripts/list_projects.py
```

### Check Environment Variables

Ensure your `.env` file contains:

```env
# Sentry Configuration
SENTRY_AUTH_TOKEN=your_sentry_token_here
SENTRY_ORG_SLUG=paywithring
SENTRY_API_BASE_URL=https://sentry.io/api/0

# Slack Configuration
SLACK_WORKSPACE_ID=your_workspace_id_here
SLACK_CHANNEL_NAME=sentry-alerts
SLACK_BOT_TOKEN=your_slack_bot_token_here

# Alert Configuration
ALERT_FREQUENCY=10
ALERT_ENVIRONMENT=production
ALERT_STATE=escalating
```

## Step 5: Create Alert Rules

### For All Projects

```bash
# Create alerts for all projects in your organization
python src/main.py
```

### For Specific Projects

```bash
# Create alerts for specific projects
python src/main.py --projects project1,project2,project3
```

### Dry Run (Test Mode)

```bash
# Test without creating actual alerts
python src/main.py --dry-run
```

## Step 6: Verify Alert Creation

### Check Sentry Dashboard

1. **Go to your Sentry organization**
2. **Navigate to any project**
3. **Go to Alerts → Rules**
4. **Verify the alert rule exists:**
   - Name: "Escalating Issues - Production"
   - Trigger: When issues enter escalating state
   - Action: Send Slack notification to #sentry-alerts

### Test Alert Triggering

1. **Create a test issue in Sentry**
2. **Mark it as escalating**
3. **Check your Slack channel for the alert**

## Configuration Options

### Alert Frequency

Modify the alert frequency in your `.env` file:

```env
ALERT_FREQUENCY=10  # minutes
```

### Environment Filter

Change the environment filter:

```env
ALERT_ENVIRONMENT=production  # or staging, development
```

### Project Filtering

Edit `config/sentry_config.yaml` to filter projects:

```yaml
projects:
  include_all: true  # Set to false to include only specific projects
  
  # Exclude specific projects
  exclude:
    - "test-project"
    - "staging-project"
  
  # Include only specific projects (when include_all: false)
  include:
    - "production-project-1"
    - "production-project-2"
```

## Troubleshooting

### Common Issues

#### 1. Sentry Authentication Failed

**Symptoms:**
- "Token lacks required permissions" error
- "Organization not found" error

**Solutions:**
- Verify your token has the required permissions
- Check that the organization slug is correct
- Ensure the token is not expired

#### 2. Slack Integration Failed

**Symptoms:**
- "Channel not found" error
- "Bot lacks access" error

**Solutions:**
- Ensure the bot is invited to the #sentry-alerts channel
- Check that the bot has the required scopes
- Verify the workspace ID is correct

#### 3. Alert Rules Not Created

**Symptoms:**
- No alert rules appear in Sentry dashboard
- "Failed to create alert" errors

**Solutions:**
- Check that your token has `project:write` permission
- Verify the project exists and is accessible
- Check the logs for detailed error messages

### Debug Mode

Run with debug logging to get more information:

```bash
python src/main.py --debug
```

### Log Files

Check the log files for detailed error information:

```bash
# View application logs
tail -f logs/sentry_alerts.log

# View error logs
tail -f logs/sentry_alerts_error.log
```

## Security Considerations

### Token Security

1. **Never commit tokens to version control**
   - The `.env` file is in `.gitignore`
   - Use environment variables in production

2. **Rotate tokens regularly**
   - Set up a schedule to rotate Sentry and Slack tokens
   - Update the `.env` file with new tokens

3. **Use minimal permissions**
   - Only grant the required permissions to tokens
   - Review and audit token permissions regularly

### Production Deployment

1. **Use environment variables**
   ```bash
   export SENTRY_AUTH_TOKEN=your_token
   export SLACK_BOT_TOKEN=your_token
   ```

2. **Secure file permissions**
   ```bash
   chmod 600 .env
   ```

3. **Monitor usage**
   - Check Sentry API rate limits
   - Monitor Slack API usage

## Maintenance

### Regular Tasks

1. **Check alert functionality**
   - Test alerts monthly
   - Verify Slack notifications are working

2. **Update configurations**
   - Review project filters quarterly
   - Update alert rules as needed

3. **Monitor logs**
   - Check log files for errors
   - Clean up old log files

### Adding New Projects

When new projects are added to your organization:

1. **Run the automation again**
   ```bash
   python src/main.py
   ```

2. **Or create alerts for specific new projects**
   ```bash
   python src/main.py --projects new-project-1,new-project-2
   ```

## Support

If you encounter issues:

1. **Check the logs** in the `logs/` directory
2. **Run in debug mode** with `--debug` flag
3. **Verify your configuration** using the test scripts
4. **Review the troubleshooting section** above

For additional help, check the main README.md file or contact your system administrator. 