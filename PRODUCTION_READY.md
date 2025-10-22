# 🚀 Sentry Alert Automation - Production Guide

## ✅ System Status: PRODUCTION READY

The system is clean and ready for ongoing operations with new projects.

## 🎯 **THE SINGLE COMMAND YOU NEED**

```bash
# Create alerts for new projects, automatically skip existing ones
python3 manage_alerts.py create
```

This command is **safe to run repeatedly** - it will:
- ✅ Create alerts for new projects with production environments
- ✅ Skip projects that already have v2.2 alerts
- ✅ Never create duplicate alerts
- ✅ Show you exactly what it's doing

## 📊 Check Current Status

```bash
# See which projects need alerts
python3 manage_alerts.py stats
```

This shows you:
- Total projects in your organization
- Projects that already have v2.2 alerts
- Projects that need alerts (new projects)
- Current alert coverage percentage

## 🔍 Preview Before Creating

```bash
# See what would be created without actually creating it
python3 manage_alerts.py create --dry-run
```

## 📁 Clean Project Structure

```
sentry-alert-automation/
├── 📄 manage_alerts.py                # 🚀 MAIN PRODUCTION SCRIPT
├── 📄 README.md                       # Complete documentation
├── 📄 requirements.txt                # Dependencies (5 packages)
├── 📄 .env.example                    # Environment template
├── 🗂️ config/
│   ├── 📄 sentry_config.yaml          # Multi-environment config
│   └── 📄 alert_config.yaml           # v2.2 alert templates
├── 🗂️ src/
│   ├── 📄 main.py                     # Core script (alternative)
│   ├── 📄 sentry_client.py            # Sentry API client
│   ├── 📄 alert_manager.py            # Multi-environment manager
│   └── 🗂️ utils/                      # Utilities
└── 🗂️ logs/                           # Auto-created logs
```

## 🎯 What the System Does

### For New Projects
- **Detects** projects with production environments but no v2.2 alerts
- **Creates** environment-specific alerts: `"Escalating Issues - {environment}"`
- **Configures** proper v2.2 conditions (escalating issues only)
- **Sets up** Slack notifications (or email fallback)

### For Existing Projects
- **Skips** projects that already have v2.2 alerts
- **Never duplicates** existing alerts
- **Preserves** current monitoring

## 🔧 Environment Detection

Automatically detects these production environments:
- `production`, `prod`, `PROD`, `PRODUCTION`, `Production`
- `ECS_PROD`, `bulk_upload_prod`, `bw_production`
- `production-worker`, `production-email-worker`, `production-push-worker`, `production-sms-worker`
- `prodution` (handles typos)

## 📈 Expected Results

### Example: New Project Added
```
Project: new-microservice
Environments: ['production', 'production-worker']
Action: Creates 2 new alerts:
  - "Escalating Issues - production"
  - "Escalating Issues - production-worker"
```

### Example: Existing Project
```
Project: existing-service  
Current alerts: Has "Escalating Issues - production"
Action: Skipped (already has v2.2 alerts)
```

## 🛡️ Safety Features

- **Dry Run Mode**: Preview everything first
- **Smart Detection**: Only processes projects that need alerts
- **Error Isolation**: Failure in one project doesn't affect others
- **Detailed Logging**: All operations logged for audit
- **No Duplicates**: Never creates duplicate alerts

## 🚀 Recommended Workflow

### Daily/Weekly Operations
```bash
# Check if any new projects need alerts
python3 manage_alerts.py stats

# If new projects found, create alerts
python3 manage_alerts.py create
```

### When Adding New Projects
```bash
# After adding a new project to Sentry, just run:
python3 manage_alerts.py create
```

### Troubleshooting
```bash
# Verify Sentry connection
python3 src/main.py --verify-connection

# Check logs for details
tail -f logs/sentry_alerts.log
```

## 📞 Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 manage_alerts.py create` | **Main command** - Create alerts for new projects |
| `python3 manage_alerts.py create --dry-run` | Preview what would be created |
| `python3 manage_alerts.py stats` | Check current alert coverage |
| `python3 src/main.py --verify-connection` | Test Sentry API connection |

## 🎉 Success Metrics

After running the system, you should see:
- **100% coverage** of projects with production environments
- **Consistent naming** across all alerts
- **Clean, duplicate-free** alert configurations
- **Proper v2.2 behavior** (escalating issues only)

---

**Status**: ✅ **PRODUCTION READY**  
**Migration**: ✅ **COMPLETED**  
**Ready for**: Ongoing operations with new projects