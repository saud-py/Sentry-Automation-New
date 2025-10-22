# Sentry Alert Automation - Product Support Team Guide

## 🎯 Quick Overview

This system automatically creates Sentry alert rules for new projects. It's designed to be **safe, simple, and production-ready**.

## 🚀 **The One Command You Need**

```bash
python3 manage_alerts.py create
```

**This command:**
- ✅ Creates alerts for new projects with production environments
- ✅ Skips projects that already have alerts
- ✅ Never creates duplicates
- ✅ Safe to run daily/weekly

## 📊 Essential Commands for Support Team

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `python3 manage_alerts.py stats` | Check alert coverage | Before creating alerts |
| `python3 manage_alerts.py create --dry-run` | Preview changes | First time or verification |
| `python3 manage_alerts.py create` | **Main command** | Regular operations |
| `python3 src/main.py --verify-connection` | Test API connection | Troubleshooting |

## 🔧 Common Support Scenarios

### 1. New Project Added to Sentry
**User Request**: "We added a new microservice, can you set up alerts?"

**Solution:**
```bash
# Check if it needs alerts
python3 manage_alerts.py stats

# Create alerts (safe to run)
python3 manage_alerts.py create
```

### 2. Check Alert Coverage
**User Request**: "Do all our projects have alerts?"

**Solution:**
```bash
python3 manage_alerts.py stats
```

**Expected Output:**
```
Alert Coverage Statistics
┌─────────────────────────┬───────┬────────────┐
│ Metric                  │ Count │ Percentage │
├─────────────────────────┼───────┼────────────┤
│ Total Projects          │   161 │       100% │
│ Projects with v2.2 Alerts │   158 │      98.1% │
│ Projects Needing Alerts │     3 │       1.9% │
└─────────────────────────┴───────┴────────────┘
```

### 3. Verify System is Working
**User Request**: "Are the alerts working properly?"

**Solution:**
```bash
# Test connection
python3 src/main.py --verify-connection

# Check logs
tail -f logs/sentry_alerts.log
```

### 4. Preview Before Making Changes
**User Request**: "What will happen if I run the alert creation?"

**Solution:**
```bash
python3 manage_alerts.py create --dry-run
```

## 🚨 Troubleshooting Guide

### Issue: "No alerts created"
**Possible Causes:**
- Project has no production environments
- Project already has alerts
- API connection issues

**Diagnosis:**
```bash
# Check project environments
python3 src/main.py --list-projects

# Test connection
python3 src/main.py --verify-connection
```

### Issue: "Connection failed"
**Possible Causes:**
- Invalid Sentry token
- Network issues
- Insufficient permissions

**Solution:**
1. Check `.env` file has correct `SENTRY_AUTH_TOKEN`
2. Verify token permissions in Sentry (project:read/write, org:read)
3. Test connection: `python3 src/main.py --verify-connection`

### Issue: "Slack notifications not working"
**Possible Causes:**
- Slack integration not configured in Sentry
- Wrong channel name
- Workspace ID incorrect

**Solution:**
1. Verify Slack integration exists in Sentry
2. Check `.env` file has correct `SLACK_WORKSPACE_ID` and `SLACK_CHANNEL_NAME`
3. Test in Sentry dashboard

## 📋 What the System Creates

### Alert Configuration
- **Name**: `"Escalating Issues - {environment}"`
- **Trigger**: When issues change from archived to escalating
- **Action**: Send Slack notification
- **Environments**: production, prod, PROD, ECS_PROD, etc.

### Example for New Project
```
Project: new-microservice
Environments detected: ['production', 'production-worker']
Alerts created:
  - "Escalating Issues - production"
  - "Escalating Issues - production-worker"
```

## 🛡️ Safety Features

- **No Duplicates**: Never creates duplicate alerts
- **Smart Detection**: Only processes projects that need alerts
- **Dry Run Mode**: Preview changes with `--dry-run`
- **Error Isolation**: One project failure doesn't affect others
- **Detailed Logging**: All operations logged in `logs/`

## 📞 Escalation Path

### Level 1: Self-Service
- Use commands in this guide
- Check logs in `logs/sentry_alerts.log`
- Verify configuration

### Level 2: Technical Support
- Review `.env` configuration
- Check Sentry token permissions
- Verify Slack integration

### Level 3: Development Team
- Code issues
- API changes
- System modifications

## 📈 Success Metrics

After running the system:
- **100% coverage** of projects with production environments
- **Consistent naming** across all alerts
- **No duplicate alerts**
- **Slack notifications working**

## 🔄 Regular Maintenance

### Weekly Tasks
```bash
# Check for new projects needing alerts
python3 manage_alerts.py stats

# Create alerts if needed
python3 manage_alerts.py create
```

### Monthly Tasks
- Review alert coverage statistics
- Check log files for errors
- Verify Slack notifications are working

## 📝 Quick Reference Card

```bash
# Status Check
python3 manage_alerts.py stats

# Create Alerts (Main Command)
python3 manage_alerts.py create

# Preview Changes
python3 manage_alerts.py create --dry-run

# Test Connection
python3 src/main.py --verify-connection

# Check Logs
tail -f logs/sentry_alerts.log
```

---

**System Status**: ✅ Production Ready  
**Support Level**: Self-Service + Technical Support  
**Update Frequency**: As needed for new projects