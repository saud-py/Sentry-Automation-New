# Sentry Alert Automation System v2.2

**Production-ready automation for creating Sentry alert rules across multiple projects with environment-specific naming.**

## 🎯 Overview

This system automates the creation of Sentry alert rules across all projects in your organization. It creates environment-specific alerts that trigger when issues escalate, ensuring your team is immediately notified via Slack when critical issues require attention.

## 🚀 **Main Command (Production Ready)**

```bash
# Create alerts for new projects, automatically skip existing ones
python3 manage_alerts.py create
```

**This command is safe to run repeatedly and will:**
- ✅ Create alerts for new projects with production environments
- ✅ Skip projects that already have v2.2 alerts  
- ✅ Never create duplicate alerts
- ✅ Show you exactly what it's doing

## 📊 Essential Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `python3 manage_alerts.py stats` | Check current alert coverage | Before creating alerts |
| `python3 manage_alerts.py create --dry-run` | Preview what would be created | First time or to verify |
| `python3 manage_alerts.py create` | **Main command** - Create alerts for new projects | Regular operations |
| `python3 src/main.py --verify-connection` | Test Sentry API connection | Troubleshooting |

## 🎯 How It Works

### Alert Behavior
- ✅ **Escalating Issues Only**: Alerts when issues change from archived to escalating state
- ❌ **No New Issue Alerts**: Reduces noise by focusing on critical issues
- 🌍 **Multi-Environment**: Creates separate alerts for each production environment

### Environment Detection
Automatically detects these production environments:
- `production`, `prod`, `PROD`, `PRODUCTION`, `Production`
- `ECS_PROD`, `bulk_upload_prod`, `bw_production`  
- `production-worker`, `production-email-worker`, `production-push-worker`, `production-sms-worker`

### Example Output
```
Project: user-service
Environments: ['production', 'production-worker']
Created Alerts:
  - "Escalating Issues - production"
  - "Escalating Issues - production-worker"
```

## 📋 Prerequisites

- **Sentry Auth Token**: Service-level token with `project:read/write` and `org:read` permissions
- **Slack Integration**: Configured in your Sentry organization
- **Python 3.8+**: For running the automation scripts

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Sentry token and Slack settings

# Verify setup
python3 src/main.py --verify-connection
```

### 2. Create Alerts
```bash
# Check current status
python3 manage_alerts.py stats

# Create alerts for new projects (safe to run repeatedly)
python3 manage_alerts.py create
```

## 📁 Project Structure

```
sentry-alert-automation/
├── 📄 manage_alerts.py                # 🚀 MAIN PRODUCTION SCRIPT
├── 📄 README.md                       # This guide
├── 📄 SETUP.md                        # Detailed setup instructions
├── 📄 requirements.txt                # Python dependencies (5 packages)
├── 📄 .env.example                    # Environment template
├── 🗂️ config/
│   ├── 📄 sentry_config.yaml          # Multi-environment configuration
│   └── 📄 alert_config.yaml           # Alert templates
├── 🗂️ src/
│   ├── 📄 main.py                     # Core alert creation script
│   ├── 📄 sentry_client.py            # Sentry API client
│   ├── 📄 alert_manager.py            # Multi-environment manager
│   └── 🗂️ utils/                      # Utility modules
└── 🗂️ logs/                           # Application logs (auto-created)
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Sentry Configuration
SENTRY_AUTH_TOKEN=your_sentry_token_here
SENTRY_ORG_SLUG=paywithring
SENTRY_API_BASE_URL=https://sentry.io/api/0

# Slack Configuration  
SLACK_WORKSPACE_ID=your_workspace_id
SLACK_CHANNEL_NAME=sentry-automation-issues

# Alert Configuration
ALERT_FREQUENCY=10
UPDATE_EXISTING=true
```

## 📊 Monitoring & Statistics

### Check Alert Coverage
```bash
python3 manage_alerts.py stats
```

**Example Output:**
```
Alert Coverage Statistics
┌─────────────────────────┬───────┬────────────┐
│ Metric                  │ Count │ Percentage │
├─────────────────────────┼───────┼────────────┤
│ Total Projects          │   161 │       100% │
│ Projects with v2.2 Alerts │   158 │      98.1% │
│ Projects Needing Alerts │     3 │       1.9% │
│ Total v2.2 Alerts      │   342 │            │
└─────────────────────────┴───────┴────────────┘

🆕 Projects Needing Alerts (3):
  • new-microservice (2 production environments)
  • test-project (1 production environment)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Connection Issues
```bash
# Test Sentry connection
python3 src/main.py --verify-connection

# Check logs
tail -f logs/sentry_alerts.log
```

#### 2. No Alerts Created
**Possible Causes:**
- Project has no production environments
- Project already has v2.2 alerts
- Insufficient Sentry permissions

**Solution:**
```bash
# Check project environments
python3 src/main.py --list-projects

# Verify token permissions in Sentry
```

#### 3. Slack Notifications Not Working
**Check:**
- Slack integration is configured in Sentry
- Channel name is correct in `.env`
- Bot has access to the channel

## 🔄 Regular Operations

### Daily/Weekly Workflow
```bash
# 1. Check if new projects need alerts
python3 manage_alerts.py stats

# 2. If new projects found, create alerts
python3 manage_alerts.py create
```

### When Adding New Projects
```bash
# After adding a new project to Sentry, just run:
python3 manage_alerts.py create
```

## 🛡️ Safety Features

- **Dry Run Mode**: Preview everything first with `--dry-run`
- **Smart Detection**: Only processes projects that need alerts
- **Error Isolation**: Failure in one project doesn't affect others
- **Detailed Logging**: All operations logged for audit
- **No Duplicates**: Never creates duplicate alerts

## 📈 Expected Results

After running the system, you should see:
- **100% coverage** of projects with production environments
- **Consistent naming** across all alerts (`Escalating Issues - {environment}`)
- **Clean, duplicate-free** alert configurations
- **Proper v2.2 behavior** (escalating issues only)

## 📞 Support

### Quick Reference Commands
```bash
# Main operations
python3 manage_alerts.py stats                    # Check status
python3 manage_alerts.py create --dry-run         # Preview
python3 manage_alerts.py create                   # Execute

# Troubleshooting
python3 src/main.py --verify-connection          # Test connection
tail -f logs/sentry_alerts.log                   # Check logs
```

### Getting Help
1. **Check logs** in the `logs/` directory
2. **Run with debug** using `python3 src/main.py --debug`
3. **Verify configuration** using connection test
4. **Review this documentation** for common solutions

---

**Version**: 2.2 (Production Ready)  
**Status**: ✅ **READY FOR PRODUCTION USE**  
**Organization**: PayWithRing  
**Last Updated**: October 2025
