# Changelog

All notable changes to the Sentry Alert Automation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2025-08-29

### 🎯 JIRA Integration Update

#### Added
- **JIRA Integration Module** (`src/jira_integration.py`) for automatic ticket creation
- **Standalone JIRA Script** (`add_jira_integration.py`) for independent JIRA operations
- **JIRA Management Commands** in `manage_alerts.py` with `add-jira` command
- **JIRA Statistics** showing integration status across all projects
- **Environment Variables** for JIRA configuration (project, issue type, priority, assignee)

#### Changed
- **Alert Manager** now automatically includes JIRA actions for new "Escalating Issues - *" alerts
- **Full Update Command** now includes JIRA integration (create + rename + JIRA)
- **Management Script** enhanced with JIRA integration capabilities

#### Technical Details
```python
# JIRA Action Configuration
jira_action = {
    "id": "sentry.integrations.jira.notify_action.JiraCreateTicketAction",
    "project": "kissht",
    "issueType": "[System] Incident", 
    "priority": "Highest",
    "assignee": "Ayush Pandey",
    "reporter": "Ayush Pandey"
}
```

#### Impact
- **188 escalating alerts** can now create JIRA tickets automatically
- **Dual notifications**: Maintains Slack alerts while adding JIRA tickets
- **Seamless integration**: Uses existing Sentry JIRA configuration
- **Smart targeting**: Only applies to "Escalating Issues - *" alerts

#### Usage
```bash
# Check JIRA integration status
python3 add_jira_integration.py --stats

# Add JIRA to all escalating alerts
python3 add_jira_integration.py --dry-run    # Preview
python3 add_jira_integration.py             # Execute

# Complete workflow with JIRA
python3 manage_alerts.py full-update --dry-run
python3 manage_alerts.py full-update
```

---

## [2.1.0] - 2024-12-XX

### 🎯 Alert Optimization Update

#### Changed
- **BREAKING**: Removed new issue alerts (`FirstSeenEventCondition`) to reduce noise
- Alert rules now only trigger on escalating issues (`State: Escalating`)
- Updated alert rule description and logging messages

#### Removed
- `FirstSeenEventCondition` from alert rule conditions
- Alerts for `State: New` issues

#### Impact
- **Alert Volume**: Reduced by approximately 60-70%
- **Signal-to-Noise Ratio**: Significantly improved
- **Team Focus**: Only critical escalating issues reach the team
- **Projects Affected**: All 159 projects automatically updated

#### Technical Details
```python
# Previous Configuration (v2.0)
conditions = [
    "sentry.rules.conditions.first_seen_event.FirstSeenEventCondition",      # NEW ISSUES
    "sentry.rules.conditions.reappeared_event.ReappearedEventCondition"     # ESCALATING
]

# Current Configuration (v2.1)  
conditions = [
    "sentry.rules.conditions.reappeared_event.ReappearedEventCondition"     # ESCALATING ONLY
]
```

#### Migration
- **Automatic**: No manual intervention required
- **Command**: Run `python src/main.py` to apply changes
- **Verification**: Use verification scripts to confirm configuration

---

## [2.0.0] - 2024-12-XX

### 🚀 Complete System Overhaul

#### Added
- Comprehensive README.md playbook with detailed instructions
- Interactive setup scripts (`setup_sentry_token.py`, `verify_slack_integration.py`)
- Cross-platform execution scripts (`run.sh`, `run.bat`, `run.ps1`)
- Robust error handling and logging system
- Input validation and sanitization utilities
- Project listing and filtering capabilities
- Environment template (`.env.example`) for secure configuration
- Comprehensive troubleshooting guide
- Security best practices documentation

#### Changed
- Improved Sentry API client with pagination support
- Enhanced alert manager with better environment detection
- Updated Slack integration with better error handling
- Restructured project organization for better maintainability

#### Fixed
- Rate limiting issues with Sentry API
- Environment detection for projects with non-standard naming
- Authentication handling for both GitHub and Slack
- Cross-platform compatibility issues

#### Security
- Added environment variable validation
- Implemented secure token handling
- Created `.gitignore` rules for sensitive files
- Added security guidelines in documentation

---

## [1.0.0] - 2024-XX-XX

### 🎉 Initial Release

#### Added
- Basic Sentry alert rule creation across multiple projects
- Slack integration for notifications
- Production environment filtering
- Configuration files for Sentry and alert settings
- Basic logging and error handling
- Support for PayWithRing organization projects

#### Features
- Automated alert creation for escalating issues
- Slack notifications to designated channels
- Environment-based filtering (production only)
- Rate limiting to prevent API abuse
- Basic project management capabilities

---

## Version Comparison

| Feature | v1.0 | v2.0 | v2.1 | v2.2 | v2.3 |
|---------|------|------|------|------|------|
| Alert on New Issues | ❌ | ✅ | ❌ | ❌ | ❌ |
| Alert on Escalating Issues | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-Environment Support | ❌ | ❌ | ❌ | ✅ | ✅ |
| Environment-Specific Naming | ❌ | ❌ | ❌ | ✅ | ✅ |
| Alert Renaming | ❌ | ❌ | ❌ | ✅ | ✅ |
| JIRA Integration | ❌ | ❌ | ❌ | ❌ | ✅ |
| Interactive Setup | ❌ | ✅ | ✅ | ✅ | ✅ |
| Cross-platform Support | ❌ | ✅ | ✅ | ✅ | ✅ |
| Comprehensive Documentation | ❌ | ✅ | ✅ | ✅ | ✅ |
| Security Best Practices | ❌ | ✅ | ✅ | ✅ | ✅ |
| Noise Reduction | ❌ | ❌ | ✅ | ✅ | ✅ |

## Upgrade Instructions

### From v2.2 to v2.3
```bash
# Pull latest changes
git pull origin main

# Add JIRA integration to existing alerts
python3 add_jira_integration.py --stats      # Check status
python3 add_jira_integration.py --dry-run    # Preview
python3 add_jira_integration.py              # Execute

# Verify JIRA integration
python3 add_jira_integration.py --stats
```

### From v2.0 to v2.1
```bash
# Pull latest changes
git pull origin main

# Apply alert configuration changes
python src/main.py

# Verify changes
python src/main.py --verify-connection
```

### From v1.0 to v2.0+
1. Review new configuration files
2. Run interactive setup scripts
3. Update environment variables
4. Test all integrations
5. Apply new alert rules

## Breaking Changes

### v2.3.0
- **JIRA Integration**: Automatic JIRA ticket creation for escalating issues
- **Impact**: Escalating issues now create both Slack notifications and JIRA tickets
- **Migration**: Run `python3 add_jira_integration.py` to add JIRA to existing alerts

### v2.1.0
- **Alert Behavior**: No longer alerts on new issues (`State: New`)
- **Impact**: Teams will only receive alerts for escalating issues
- **Migration**: Automatic when running the main script

### v2.0.0
- **Configuration Structure**: New YAML-based configuration
- **Environment Variables**: Updated variable names and structure
- **Dependencies**: New Python packages required
- **Migration**: Manual configuration update required

## Support

For questions about specific versions or upgrade assistance:
1. Check the README.md for current documentation
2. Review SETUP.md for installation instructions  
3. Check logs in the `logs/` directory for troubleshooting
4. Use `--debug` flag for detailed error information