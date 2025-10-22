"""
Alert Manager v2.2 - Multi-Environment Support

This module manages the creation of environment-specific Sentry alert rules
for escalating issues across multiple production environments.
"""

import os
import logging
from typing import Dict, Any, Optional, List

from sentry_client import SentryClient

class AlertManager:
    """Manages v2.2 multi-environment Sentry alert rule creation."""
    
    def __init__(self, sentry_client: SentryClient):
        """Initialize the alert manager with v2.2 multi-environment support."""
        self.sentry_client = sentry_client
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.alert_frequency = int(os.getenv('ALERT_FREQUENCY', '10'))
        self.slack_channel = os.getenv('SLACK_CHANNEL_NAME', 'sentry-automation-issues')
        self.slack_workspace_id = os.getenv('SLACK_WORKSPACE_ID')
        
        # v2.2: Production environment variations (auto-detection)
        self.production_envs = [
            'production', 'prod', 'PROD', 'PRODUCTION', 'Production',
            'ECS_PROD', 'bulk_upload_prod', 'bw_production',
            'production-worker', 'production-email-worker', 
            'production-push-worker', 'production-sms-worker',
            'prodution'  # handles typos
        ]
        
        # Detect Slack integration only (v2.2)
        self.slack_integration = None
        self._detect_slack_integration()
    
    def _detect_slack_integration(self):
        """Detect available Slack integration."""
        try:
            integrations = self.sentry_client.get_integrations()
            for integration in integrations:
                provider = integration.get('provider', {})
                if provider.get('key') == 'slack':
                    self.slack_integration = integration
                    break
        except Exception as e:
            self.logger.debug(f"Failed to detect Slack integration: {e}")
    
    def create_multi_environment_alerts(self, project_slug: str) -> int:
        """Create environment-specific alerts for all production environments (v2.2)."""
        try:
            production_environments = self.get_production_environments(project_slug)
            
            if not production_environments:
                self.logger.warning(f"No production environments found for {project_slug}")
                return 0
            
            success_count = 0
            
            for env_name in production_environments:
                rule_name = f"Escalating Issues - {env_name}"
                
                try:
                    # Check if rule already exists
                    existing_rule_id = self.sentry_client.check_alert_rule_exists(project_slug, rule_name)
                    
                    if existing_rule_id:
                        self.logger.info(f"Alert already exists for {project_slug} - {env_name}")
                        success_count += 1
                    else:
                        # Create new rule
                        rule_data = self._build_escalating_alert_rule(rule_name, env_name)
                        response = self.sentry_client.create_alert_rule(project_slug, rule_data)
                        
                        if response and response.get('id'):
                            self.logger.info(f"Created alert: {rule_name} for {project_slug}")
                            success_count += 1
                        else:
                            self.logger.error(f"Failed to create alert for {project_slug} - {env_name}")
                
                except Exception as env_error:
                    self.logger.error(f"Error creating alert for {project_slug} - {env_name}: {env_error}")
            
            return success_count
                
        except Exception as e:
            self.logger.error(f"Error creating multi-environment alerts for {project_slug}: {e}")
            return 0
    
    def get_production_environments(self, project_slug: str) -> List[str]:
        """Get all production environment names for a project (v2.2)."""
        try:
            environments = self.sentry_client.get_environments(project_slug)
            env_names = [env.get('name', '') for env in environments]
            
            # Find matching production environments
            production_environments = []
            for prod_env in self.production_envs:
                if prod_env in env_names:
                    production_environments.append(prod_env)
            
            self.logger.debug(f"Project {project_slug} production envs: {production_environments}")
            return production_environments
            
        except Exception as e:
            self.logger.error(f"Error getting environments for {project_slug}: {e}")
            return []

    def _build_escalating_alert_rule(self, rule_name: str, environment: str) -> Dict[str, Any]:
        """Build v2.2 escalating alert rule configuration.
        
        Creates alerts only for issues changing from archived to escalating state.
        No new issue alerts to reduce noise (v2.2 specification).
        """
        
        rule_data = {
            "name": rule_name,
            "description": f"Alert when issues change state from archived to escalating in {environment}",
            "actionMatch": "any",
            "filterMatch": "all", 
            "frequency": self.alert_frequency,
            "environment": environment,
            "conditions": [
                {
                    "id": "sentry.rules.conditions.reappeared_event.ReappearedEventCondition"
                }
            ],
            "filters": [
                {
                    "id": "sentry.rules.filters.issue_occurrences.IssueOccurrencesFilter",
                    "value": 1
                }
            ],
            "actions": []
        }
        
        # Add Slack action
        if self.slack_integration:
            rule_data["actions"].append({
                "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
                "workspace": str(self.slack_integration.get('id')),
                "channel": self.slack_channel,
                "tags": "environment,transaction"
            })
        else:
            # Email fallback
            rule_data["actions"].append({
                "id": "sentry.rules.actions.notify_event.NotifyEventAction"
            })
        
        
        return rule_data
    
    def get_project_alerts(self, project_slug: str) -> List[dict]:
        """Get all alert rules for a project."""
        try:
            alerts = self.sentry_client.get_alert_rules(project_slug)
            return alerts
        except Exception as e:
            self.logger.error(f"Error getting alert rules for {project_slug}: {e}")
            return []
    
    def safe_replace_alerts(self, project_slug: str, dry_run: bool = False) -> dict:
        """Safely replace existing escalating alerts with new v2.2 alerts.
        
        Strategy:
        1. Create new alerts with temporary names
        2. Verify new alerts are working
        3. Delete old alerts
        4. Rename new alerts to final names
        
        This ensures continuous monitoring during the replacement.
        """
        try:
            production_environments = self.get_production_environments(project_slug)
            
            if not production_environments:
                self.logger.warning(f"No production environments found for {project_slug}")
                return {"success": 0, "failed": 0, "skipped": 0}
            
            results = {"success": 0, "failed": 0, "skipped": 0}
            
            for env_name in production_environments:
                old_rule_name = f"Escalating Issues - {env_name}"
                temp_rule_name = f"Escalating Issues - {env_name} (v2.2-temp)"
                
                try:
                    # Step 1: Check if old alert exists
                    existing_rule_id = self.sentry_client.check_alert_rule_exists(project_slug, old_rule_name)
                    
                    if not existing_rule_id:
                        self.logger.info(f"No existing alert found for {project_slug} - {env_name}, creating new one")
                        if not dry_run:
                            rule_data = self._build_escalating_alert_rule(old_rule_name, env_name)
                            response = self.sentry_client.create_alert_rule(project_slug, rule_data)
                            if response and response.get('id'):
                                results["success"] += 1
                            else:
                                results["failed"] += 1
                        else:
                            results["skipped"] += 1
                        continue
                    
                    if dry_run:
                        self.logger.info(f"DRY RUN: Would replace alert for {project_slug} - {env_name}")
                        results["skipped"] += 1
                        continue
                    
                    # Step 2: Create temporary alert with new v2.2 configuration
                    self.logger.info(f"Creating temporary v2.2 alert for {project_slug} - {env_name}")
                    temp_rule_data = self._build_escalating_alert_rule(temp_rule_name, env_name)
                    temp_response = self.sentry_client.create_alert_rule(project_slug, temp_rule_data)
                    
                    if not temp_response or not temp_response.get('id'):
                        self.logger.error(f"Failed to create temporary alert for {project_slug} - {env_name}")
                        results["failed"] += 1
                        continue
                    
                    temp_rule_id = temp_response.get('id')
                    self.logger.info(f"Created temporary alert {temp_rule_id} for {project_slug} - {env_name}")
                    
                    # Step 3: Delete old alert
                    self.logger.info(f"Deleting old alert {existing_rule_id} for {project_slug} - {env_name}")
                    delete_success = self.sentry_client.delete_alert_rule(project_slug, existing_rule_id)
                    
                    if not delete_success:
                        self.logger.error(f"Failed to delete old alert for {project_slug} - {env_name}")
                        # Clean up temporary alert
                        cleanup_success = self.sentry_client.delete_alert_rule(project_slug, temp_rule_id)
                        if cleanup_success:
                            self.logger.info(f"Cleaned up temporary alert {temp_rule_id}")
                        else:
                            self.logger.warning(f"Failed to clean up temporary alert {temp_rule_id}")
                        results["failed"] += 1
                        continue
                    
                    # Verify old alert was actually deleted
                    if self.sentry_client.alert_rule_exists_by_id(project_slug, existing_rule_id):
                        self.logger.error(f"Old alert {existing_rule_id} still exists after deletion attempt")
                        results["failed"] += 1
                        continue
                    
                    # Step 4: Rename temporary alert to final name
                    self.logger.info(f"Renaming temporary alert to final name for {project_slug} - {env_name}")
                    rename_data = {"name": old_rule_name}
                    rename_success = self.sentry_client.update_alert_rule(project_slug, temp_rule_id, rename_data)
                    
                    if rename_success:
                        self.logger.info(f"Successfully replaced alert for {project_slug} - {env_name}")
                        results["success"] += 1
                    else:
                        self.logger.error(f"Failed to rename temporary alert for {project_slug} - {env_name}")
                        results["failed"] += 1
                
                except Exception as env_error:
                    self.logger.error(f"Error replacing alert for {project_slug} - {env_name}: {env_error}")
                    results["failed"] += 1
            
            return results
                
        except Exception as e:
            self.logger.error(f"Error in safe alert replacement for {project_slug}: {e}")
            return {"success": 0, "failed": 0, "skipped": 0}
    
    def delete_escalating_alerts(self, project_slug: str, dry_run: bool = False) -> dict:
        """Delete all 'Escalating Issues - *' alerts for a project."""
        try:
            alerts = self.get_project_alerts(project_slug)
            results = {"deleted": 0, "failed": 0, "skipped": 0}
            
            for alert in alerts:
                alert_name = alert.get('name', '')
                alert_id = alert.get('id')
                
                if alert_name.startswith("Escalating Issues - "):
                    if dry_run:
                        self.logger.info(f"DRY RUN: Would delete alert '{alert_name}' for {project_slug}")
                        results["skipped"] += 1
                    else:
                        self.logger.info(f"Deleting alert '{alert_name}' (ID: {alert_id}) for {project_slug}")
                        success = self.sentry_client.delete_alert_rule(project_slug, alert_id)
                        if success:
                            results["deleted"] += 1
                            self.logger.info(f"Successfully deleted alert '{alert_name}'")
                        else:
                            # Even if the API reports failure, the alert might have been deleted
                            # Check if it still exists
                            if not self.sentry_client.alert_rule_exists_by_id(project_slug, alert_id):
                                results["deleted"] += 1
                                self.logger.info(f"Alert '{alert_name}' was successfully deleted (despite API response)")
                            else:
                                results["failed"] += 1
                                self.logger.error(f"Failed to delete alert '{alert_name}'")
            
            return results
                
        except Exception as e:
            self.logger.error(f"Error deleting escalating alerts for {project_slug}: {e}")
            return {"deleted": 0, "failed": 0, "skipped": 0}
    
    def simple_replace_alerts(self, project_slug: str, dry_run: bool = False) -> dict:
        """Simple replacement: delete old alerts and create new ones.
        
        This is simpler than the safe_replace_alerts method but has a brief monitoring gap.
        """
        try:
            results = {"success": 0, "failed": 0, "skipped": 0}
            
            if dry_run:
                # Show what would be done
                delete_results = self.delete_escalating_alerts(project_slug, dry_run=True)
                create_count = len(self.get_production_environments(project_slug))
                
                results["skipped"] = delete_results["skipped"] + create_count
                self.logger.info(f"DRY RUN: Would delete {delete_results['skipped']} alerts and create {create_count} new alerts for {project_slug}")
                return results
            
            # Step 1: Delete existing escalating alerts
            self.logger.info(f"Step 1: Deleting existing escalating alerts for {project_slug}")
            delete_results = self.delete_escalating_alerts(project_slug, dry_run=False)
            
            if delete_results["failed"] > 0:
                self.logger.warning(f"Some alerts failed to delete for {project_slug}")
            
            # Step 2: Create new v2.2 alerts
            self.logger.info(f"Step 2: Creating new v2.2 alerts for {project_slug}")
            create_count = self.create_multi_environment_alerts(project_slug)
            
            results["success"] = create_count
            results["failed"] = delete_results["failed"]
            
            if create_count > 0:
                self.logger.info(f"Successfully replaced alerts for {project_slug}: deleted {delete_results['deleted']}, created {create_count}")
            else:
                self.logger.error(f"Failed to create new alerts for {project_slug}")
                results["failed"] += 1
            
            return results
                
        except Exception as e:
            self.logger.error(f"Error in simple alert replacement for {project_slug}: {e}")
            return {"success": 0, "failed": 1, "skipped": 0} 