# Sentry Alert Automation - Setup Guide

Complete setup instructions for the Sentry Alert Automation System v2.2.

## Prerequisites

- **Python 3.8+** installed on your system
- **Sentry Organization Admin** access
- **Slack Integration** configured in Sentry

## Step 1: Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import requests, yaml, click, rich; print('Dependencies installed successfully!')"
```

## Step 2: Sentry Configuration

### Generate Sentry Auth Token

1. **Go to Sentry** → Settings → Developer Settings → New Internal Integration
2. **Create integration** with name: `Alert Automation`
3. **Add permissions**:
   - `project:read` - Read project information
   - `project:write` - Create and manage alert rules
   - `org:read` - Read organization information
4. **Copy the token** (starts with `sntryu_`)

### Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your values:
# SENTRY_AUTH_TOKEN=your_actual_token_here
# SENTRY_ORG_SLUG=paywithring
```

## Step 3: Slack Configuration

### Configure Slack Integration

The system uses Sentry's built-in Slack integration. Ensure you have:

1. **Slack integration configured** in your Sentry organization
2. **Alert channel created** (e.g., `#sentry-automation-issues`)
3. **Workspace ID** from your Slack settings

Add to your `.env` file:
```bash
# SLACK_WORKSPACE_ID=your_workspace_id
# SLACK_CHANNEL_NAME=sentry-automation-issues
```

## Step 4: Verify Configuration

### Test Connections

```bash
# Test Sentry connection
python3 src/main.py --verify-connection

# List all projects
python3 src/main.py --list-projects
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
SLACK_CHANNEL_NAME=sentry-automation-issues

# Alert Configuration
ALERT_FREQUENCY=10
UPDATE_EXISTING=true
```

## Step 5: Create Alert Rules

### Production Command (Recommended)

```bash
# Check current status
python3 manage_alerts.py stats

# Preview alert creation
python3 manage_alerts.py create --dry-run

# Create alerts for new projects (safe to run repeatedly)
python3 manage_alerts.py create
```

### Alternative: Direct Creation

```bash
# Create alerts directly
python3 src/main.py

# Create alerts for specific projects
python3 src/main.py --projects project1,project2

# Preview mode
python3 src/main.py --dry-run
```

## Step 6: Verify Alert Creation

### Check Sentry Dashboard

1. **Go to your Sentry organization**
2. **Navigate to any project**
3. **Go to Alerts → Rules**
4. **Verify the alert rule exists:**
   - Name: "Escalating Issues - Production"
   - Trigger: **Only** when issues change state from archived to escalating (v2.1 update)
   - Action: Send Slack notification to #sentry-alerts
   - **Note**: No longer triggers on new issues (State: New) as of v2.1

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

## Recent Updates (v2.1)

### Alert Configuration Changes
As of December 2024, the alert system has been optimized:

#### What Changed
- **Removed**: Alerts for new issues (`State: New`)
- **Kept**: Alerts for escalating issues (`State: Escalating`)
- **Result**: Reduced alert noise by 60-70%

#### Why This Change
- New issues often resolve themselves automatically
- Escalating issues represent genuine problems requiring attention
- Improved signal-to-noise ratio for better team focus

#### Verification
After setup, verify your alerts only trigger on escalating issues:
```bash
# Check alert configuration
python3 src/main.py --list-projects

# Verify alert rules (should show only 1 condition)
python src/main.py --projects your-test-project --dry-run
```

Expected alert rule should have:
- **1 condition**: "The issue changes state from archived to escalating"
- **0 conditions**: No "new issue" conditions

## Support

If you encounter issues:

1. **Check the logs** in the `logs/` directory
2. **Run in debug mode** with `--debug` flag
3. **Verify your configuration** using the test scripts
4. **Review the troubleshooting section** above

For additional help, check the main README.md file or contact your system administrator. 