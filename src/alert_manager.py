"""
Alert Manager

This module manages the creation and configuration of Sentry alert rules
for escalating issues in production environments.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from sentry_client import SentryClient

class AlertManager:
    """Manages Sentry alert rule creation and configuration."""
    
    def __init__(self, sentry_client: SentryClient):
        """Initialize the alert manager with a Sentry client."""
        self.sentry_client = sentry_client
        self.logger = logging.getLogger(__name__)
        
        # Load configuration from environment
        self.alert_frequency = int(os.getenv('ALERT_FREQUENCY', '10'))
        self.alert_environment = os.getenv('ALERT_ENVIRONMENT', 'production')
        self.alert_state = os.getenv('ALERT_STATE', 'escalating')
        self.slack_channel = os.getenv('SLACK_CHANNEL_NAME', 'sentry-alerts')
        
        # Detect Slack integration via Sentry API; allow env override for channel name
        self.slack_integration = None
        try:
            integrations = self.sentry_client.get_integrations()
            for integration in integrations:
                provider = integration.get('provider') or {}
                if provider.get('key') == 'slack':
                    self.slack_integration = integration
                    break
        except Exception as integration_error:
            self.logger.debug(f"Failed to fetch integrations: {integration_error}")

        self.slack_enabled = self.slack_integration is not None
    
    def create_escalating_alert(self, project_slug: str) -> bool:
        """Create an alert rule for escalating issues in production."""
        try:
            # Check if alert rule already exists
            rule_name = f"Escalating Issues - {self.alert_environment.title()}"
            existing_rule_id = self.sentry_client.check_alert_rule_exists(project_slug, rule_name)
            
            if existing_rule_id:
                self.logger.info(f"Alert rule already exists for project {project_slug}: {existing_rule_id}")
                return True
            
            # Create alert rule data
            rule_data = self._build_escalating_alert_rule(project_slug, rule_name)
            
            # Create the alert rule
            response = self.sentry_client.create_alert_rule(project_slug, rule_data)
            
            if response and response.get('id'):
                self.logger.info(f"Successfully created alert rule for project {project_slug}: {response['id']}")
                return True
            else:
                self.logger.error(f"Failed to create alert rule for project {project_slug}: Invalid response")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating alert rule for project {project_slug}: {e}")
            return False
    
    def _build_escalating_alert_rule(self, project_slug: str, rule_name: str) -> Dict[str, Any]:
        """Build the alert rule configuration for escalating issues."""
        
        # Base alert rule structure
        allowed_interval = self._resolve_allowed_interval(project_slug)
        rule_data = {
            "name": rule_name,
            "description": f"Alert when issues enter escalating state in {self.alert_environment} environment",
            "actionMatch": "all",
            "filterMatch": "all",
            "frequency": self.alert_frequency,
            "environment": self.alert_environment,
            "conditions": [
                {
                    "id": "sentry.rules.conditions.event_frequency.EventFrequencyCondition",
                    "value": 1,
                    "interval": allowed_interval
                }
            ],
            "filters": [],
            "actions": []
        }
        
        # Add Slack action if Slack is enabled
        if self.slack_enabled:
            rule_data["actions"].append({
                "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
                "workspace": str(self.slack_integration.get('id')),
                "channel": f"#{self.slack_channel}"
            })
        else:
            # Add email action as fallback
            rule_data["actions"].append({
                "id": "sentry.rules.actions.notify_event.NotifyEventAction",
                "name": "Send a notification to all team members and issue owners",
                "tags": "environment,project,issue_title,issue_url,timestamp"
            })
        
        return rule_data
    
    def create_high_error_rate_alert(self, project_slug: str, threshold: int = 5) -> bool:
        """Create an alert rule for high error rates."""
        try:
            rule_name = f"High Error Rate - {self.alert_environment.title()}"
            existing_rule_id = self.sentry_client.check_alert_rule_exists(project_slug, rule_name)
            
            if existing_rule_id:
                self.logger.info(f"High error rate alert rule already exists for project {project_slug}")
                return True
            
            rule_data = self._build_high_error_rate_alert_rule(project_slug, rule_name, threshold)
            response = self.sentry_client.create_alert_rule(project_slug, rule_data)
            
            if response and response.get('id'):
                self.logger.info(f"Successfully created high error rate alert for project {project_slug}")
                return True
            else:
                self.logger.error(f"Failed to create high error rate alert for project {project_slug}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating high error rate alert for project {project_slug}: {e}")
            return False
    
    def _build_high_error_rate_alert_rule(self, project_slug: str, rule_name: str, threshold: int) -> Dict[str, Any]:
        """Build the alert rule configuration for high error rates."""
        
        allowed_interval = self._resolve_allowed_interval(project_slug)
        rule_data = {
            "name": rule_name,
            "description": f"Alert when error rate exceeds {threshold}% in {self.alert_environment} environment",
            "actionMatch": "all",
            "filterMatch": "all",
            "frequency": self.alert_frequency,
            "environment": self.alert_environment,
            "conditions": [
                {
                    "id": "sentry.rules.conditions.event_frequency.EventFrequencyCondition",
                    "value": threshold,
                    "interval": allowed_interval
                }
            ],
            "filters": [],
            "actions": []
        }
        
        # Add Slack action if Slack is enabled
        if self.slack_enabled:
            rule_data["actions"].append({
                "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
                "workspace": str(self.slack_integration.get('id')),
                "channel": f"#{self.slack_channel}"
            })
        else:
            # Add email action as fallback
            rule_data["actions"].append({
                "id": "sentry.rules.actions.notify_event.NotifyEventAction",
                "name": "Send a notification to all team members and issue owners",
                "tags": "environment,project,error_rate,threshold,time_window"
            })
        
        return rule_data
    
    def create_critical_issue_alert(self, project_slug: str) -> bool:
        """Create an alert rule for critical (fatal) issues."""
        try:
            rule_name = f"Critical Issues - {self.alert_environment.title()}"
            existing_rule_id = self.sentry_client.check_alert_rule_exists(project_slug, rule_name)
            
            if existing_rule_id:
                self.logger.info(f"Critical issue alert rule already exists for project {project_slug}")
                return True
            
            rule_data = self._build_critical_issue_alert_rule(project_slug, rule_name)
            response = self.sentry_client.create_alert_rule(project_slug, rule_data)
            
            if response and response.get('id'):
                self.logger.info(f"Successfully created critical issue alert for project {project_slug}")
                return True
            else:
                self.logger.error(f"Failed to create critical issue alert for project {project_slug}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating critical issue alert for project {project_slug}: {e}")
            return False
    
    def _build_critical_issue_alert_rule(self, project_slug: str, rule_name: str) -> Dict[str, Any]:
        """Build the alert rule configuration for critical issues."""
        
        allowed_interval = self._resolve_allowed_interval(project_slug)
        rule_data = {
            "name": rule_name,
            "description": f"Alert for critical (fatal) issues in {self.alert_environment} environment",
            "actionMatch": "all",
            "filterMatch": "all",
            "frequency": self.alert_frequency,
            "environment": self.alert_environment,
            "conditions": [
                {
                    "id": "sentry.rules.conditions.event_frequency.EventFrequencyCondition",
                    "value": 1,
                    "interval": allowed_interval
                }
            ],
            "filters": [
                {
                    "id": "sentry.rules.filters.event_attribute.EventAttributeFilter",
                    "attribute": "level",
                    "value": "fatal"
                }
            ],
            "actions": []
        }
        
        # Add Slack action if Slack is enabled
        if self.slack_enabled:
            rule_data["actions"].append({
                "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
                "workspace": str(self.slack_integration.get('id')),
                "channel": f"#{self.slack_channel}"
            })
        else:
            # Add email action as fallback
            rule_data["actions"].append({
                "id": "sentry.rules.actions.notify_event.NotifyEventAction",
                "name": "Send a notification to all team members and issue owners",
                "tags": "environment,project,issue_level,issue_title,issue_url,timestamp"
            })
        
        return rule_data

    def _resolve_allowed_interval(self, project_slug: str) -> Any:
        """Return a valid interval accepted by Sentry for EventFrequencyCondition.

        Attempts to match the configured ALERT_FREQUENCY. If unavailable, falls back to
        the first allowed choice.
        """
        try:
            config = self.sentry_client.get_rule_configuration(project_slug)
            for node in config.get('conditions', []):
                if node.get('id') == 'sentry.rules.conditions.event_frequency.EventFrequencyCondition':
                    form_fields = node.get('formFields', {})
                    interval_field = form_fields.get('interval') or form_fields.get('timeWindow') or {}
                    choices = interval_field.get('choices') or []
                    # choices can be list of [value, label] or flat list
                    allowed_values = []
                    for choice in choices:
                        if isinstance(choice, (list, tuple)) and len(choice) > 0:
                            allowed_values.append(choice[0])
                        else:
                            allowed_values.append(choice)
                    # Try exact int match
                    if self.alert_frequency in allowed_values:
                        return self.alert_frequency
                    # Try string minute like "10m"
                    if f"{self.alert_frequency}m" in allowed_values:
                        return f"{self.alert_frequency}m"
                    # Try string match of number
                    if str(self.alert_frequency) in allowed_values:
                        return str(self.alert_frequency)
                    # Fallback to first
                    if allowed_values:
                        return allowed_values[0]
            # If schema didn't include interval choices, default to 10
            return 10
        except Exception as e:
            self.logger.debug(f"Failed to resolve allowed interval for {project_slug}: {e}")
            return 10
    
    def update_alert_rule(self, project_slug: str, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing alert rule."""
        try:
            response = self.sentry_client.update_alert_rule(project_slug, rule_id, updates)
            if response:
                self.logger.info(f"Successfully updated alert rule {rule_id} for project {project_slug}")
                return True
            else:
                self.logger.error(f"Failed to update alert rule {rule_id} for project {project_slug}")
                return False
        except Exception as e:
            self.logger.error(f"Error updating alert rule {rule_id} for project {project_slug}: {e}")
            return False
    
    def delete_alert_rule(self, project_slug: str, rule_id: str) -> bool:
        """Delete an alert rule."""
        try:
            success = self.sentry_client.delete_alert_rule(project_slug, rule_id)
            if success:
                self.logger.info(f"Successfully deleted alert rule {rule_id} for project {project_slug}")
            else:
                self.logger.error(f"Failed to delete alert rule {rule_id} for project {project_slug}")
            return success
        except Exception as e:
            self.logger.error(f"Error deleting alert rule {rule_id} for project {project_slug}: {e}")
            return False
    
    def get_project_alerts(self, project_slug: str) -> list:
        """Get all alert rules for a project."""
        try:
            alerts = self.sentry_client.get_alert_rules(project_slug)
            self.logger.info(f"Found {len(alerts)} alert rules for project {project_slug}")
            return alerts
        except Exception as e:
            self.logger.error(f"Error getting alert rules for project {project_slug}: {e}")
            return []
    
    def validate_alert_configuration(self, project_slug: str) -> Dict[str, Any]:
        """Validate that a project has the required alert configurations."""
        try:
            alerts = self.get_project_alerts(project_slug)
            
            validation_result = {
                "project": project_slug,
                "total_alerts": len(alerts),
                "escalating_alert": False,
                "high_error_rate_alert": False,
                "critical_alert": False,
                "missing_alerts": []
            }
            
            for alert in alerts:
                alert_name = alert.get('name', '')
                if 'Escalating Issues' in alert_name:
                    validation_result["escalating_alert"] = True
                elif 'High Error Rate' in alert_name:
                    validation_result["high_error_rate_alert"] = True
                elif 'Critical Issues' in alert_name:
                    validation_result["critical_alert"] = True
            
            # Check for missing alerts
            if not validation_result["escalating_alert"]:
                validation_result["missing_alerts"].append("Escalating Issues Alert")
            if not validation_result["high_error_rate_alert"]:
                validation_result["missing_alerts"].append("High Error Rate Alert")
            if not validation_result["critical_alert"]:
                validation_result["missing_alerts"].append("Critical Issues Alert")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating alert configuration for project {project_slug}: {e}")
            return {
                "project": project_slug,
                "error": str(e),
                "total_alerts": 0,
                "escalating_alert": False,
                "high_error_rate_alert": False,
                "critical_alert": False,
                "missing_alerts": ["All alerts"]
            } 