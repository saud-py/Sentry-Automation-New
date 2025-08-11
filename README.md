<<<<<<< HEAD
# sentry_automation
=======
# Sentry Alert Automation Setup

This project automates the creation of alert rules across all Sentry projects in your organization to receive timely notifications on Slack when issues enter the "escalating" state in production environments.

## Overview

The automation addresses Sentry's limitation of not supporting global alert rules across multiple projects by programmatically creating alerts for each project using the Sentry API.

## Features

- **Automated Alert Creation**: Creates alert rules across all projects in your Sentry organization
- **Slack Integration**: Sends notifications to `#sentry-alerts` channel
- **Production Environment Filter**: Only triggers for production environment issues
- **Rate Limiting**: Prevents alert spam with 10-minute frequency
- **Scalable**: Easy to add new projects as they're onboarded

## Alert Configuration

- **Trigger**: Issues entering "escalating" state
- **Environment**: Production only
- **Notification Channel**: `#sentry-alerts` on Slack
- **Frequency**: Every 10 minutes
- **Organization**: `paywithring`

## Prerequisites

1. **Sentry Auth Token**: Service-level token with `project:read/write` permissions
2. **Slack Integration**: Active Slack integration in Sentry
3. **Python 3.8+**: For running the automation scripts
4. **Required Python packages**: See `requirements.txt`

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Sentry and Slack credentials
   ```

3. **Run the automation**:
   ```bash
   python src/main.py
   ```

## Project Structure

```
saud/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── config/
│   ├── sentry_config.yaml   # Sentry organization and project settings
│   └── alert_config.yaml    # Alert rule configurations
├── src/
│   ├── main.py              # Main automation script
│   ├── sentry_client.py     # Sentry API client
│   ├── alert_manager.py     # Alert rule management
│   ├── slack_integration.py # Slack notification setup
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # Logging utilities
│       └── validators.py    # Input validation
├── scripts/
│   ├── setup_sentry_token.py    # Script to generate Sentry token
│   ├── verify_slack_integration.py # Verify Slack integration
│   └── list_projects.py         # List all projects in org
└── logs/                    # Application logs
    └── .gitkeep
```

## Configuration Files

### Environment Variables (.env)
- `SENTRY_AUTH_TOKEN`: Your Sentry service-level token
- `SENTRY_ORG_SLUG`: Your Sentry organization slug
- `SLACK_WORKSPACE_ID`: Your Slack workspace ID
- `SLACK_CHANNEL_NAME`: Target Slack channel name

### Sentry Configuration (config/sentry_config.yaml)
- Organization settings
- Project filtering rules
- Environment configurations

### Alert Configuration (config/alert_config.yaml)
- Alert rule templates
- Notification settings
- Frequency and threshold configurations

## Usage

### 1. Initial Setup
```bash
python scripts/setup_sentry_token.py
python scripts/verify_slack_integration.py
```

### 2. List Current Projects
```bash
python scripts/list_projects.py
```

### 3. Create Alerts for All Projects
```bash
python src/main.py
```

### 4. Create Alerts for Specific Projects
```bash
python src/main.py --projects project1,project2
```

## Monitoring and Maintenance

- **Logs**: Check `logs/` directory for execution logs
- **Alert Status**: Monitor alert creation status in Sentry dashboard
- **Slack Notifications**: Verify test notifications in `#sentry-alerts`

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your Sentry auth token has correct permissions
2. **Slack Integration**: Ensure Slack integration is active in Sentry
3. **Rate Limiting**: Sentry API has rate limits; scripts include delays
4. **Project Access**: Verify token has access to all target projects

### Debug Mode

Run with debug logging:
```bash
python src/main.py --debug
```

## Security Considerations

- Store sensitive tokens in environment variables
- Use service-level tokens with minimal required permissions
- Regularly rotate authentication tokens
- Monitor API usage and rate limits

## Contributing

1. Follow the existing code structure
2. Add appropriate logging and error handling
3. Update configuration files as needed
4. Test changes with a subset of projects first

## License

This project is for internal use by the paywithring organization. 
>>>>>>> aace654 (Initial commit)
