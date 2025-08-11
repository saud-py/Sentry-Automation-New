"""
Slack Integration

This module handles Slack integration for sending notifications
and testing the connection to the Slack workspace.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackIntegration:
    """Handles Slack integration for Sentry alert notifications."""
    
    def __init__(self):
        """Initialize the Slack integration."""
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.workspace_id = os.getenv('SLACK_WORKSPACE_ID')
        self.channel_name = os.getenv('SLACK_CHANNEL_NAME', 'sentry-alerts')
        
        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN environment variable is required")
        
        if not self.workspace_id:
            raise ValueError("SLACK_WORKSPACE_ID environment variable is required")
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize Slack client
        self.client = WebClient(token=self.bot_token)
        
        # Channel ID cache
        self._channel_id_cache = {}
    
    def get_channel_id(self, channel_name: str) -> Optional[str]:
        """Get the channel ID for a given channel name."""
        if channel_name in self._channel_id_cache:
            return self._channel_id_cache[channel_name]
        
        try:
            # Try to get channel ID by name
            response = self.client.conversations_list(
                types="public_channel,private_channel"
            )
            
            for channel in response['channels']:
                if channel['name'] == channel_name.replace('#', ''):
                    self._channel_id_cache[channel_name] = channel['id']
                    return channel['id']
            
            self.logger.warning(f"Channel {channel_name} not found")
            return None
            
        except SlackApiError as e:
            self.logger.error(f"Error getting channel ID for {channel_name}: {e}")
            return None
    
    def send_message(self, channel: str, message: str, **kwargs) -> bool:
        """Send a message to a Slack channel."""
        try:
            channel_id = self.get_channel_id(channel)
            if not channel_id:
                self.logger.error(f"Could not find channel ID for {channel}")
                return False
            
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=message,
                **kwargs
            )
            
            if response['ok']:
                self.logger.info(f"Message sent successfully to {channel}")
                return True
            else:
                self.logger.error(f"Failed to send message to {channel}: {response}")
                return False
                
        except SlackApiError as e:
            self.logger.error(f"Slack API error sending message to {channel}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending message to {channel}: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """Send a test message to verify Slack integration."""
        test_message = (
            "✅ *Sentry Alert Test*\n\n"
            "This is a test message to verify the Slack integration is working correctly.\n\n"
            f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            "*Status:* Integration test successful"
        )
        
        return self.send_message(
            channel=f"#{self.channel_name}",
            message=test_message,
            username="Sentry Alert Bot",
            icon_emoji=":white_check_mark:"
        )
    
    def send_escalating_alert(self, project: str, environment: str, issue_title: str, 
                             issue_url: str, event_count: int = 1, stack_trace: str = "") -> bool:
        """Send an escalating issue alert to Slack."""
        message = (
            "🚨 *Escalating Issue Alert*\n\n"
            f"*Project:* {project}\n"
            f"*Environment:* {environment}\n"
            f"*Issue Title:* {issue_title}\n"
            f"*Issue URL:* {issue_url}\n"
            f"*Event Count:* {event_count}\n"
            f"*Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        )
        
        if stack_trace:
            # Truncate stack trace if too long
            if len(stack_trace) > 500:
                stack_trace = stack_trace[:500] + "..."
            message += f"*Stack Trace Preview:*\n```\n{stack_trace}\n```\n\n"
        
        message += "Please investigate this escalating issue immediately."
        
        return self.send_message(
            channel=f"#{self.channel_name}",
            message=message,
            username="Sentry Alert Bot",
            icon_emoji=":warning:",
            unfurl_links=False
        )
    
    def send_high_error_rate_alert(self, project: str, environment: str, error_rate: float, 
                                  threshold: float, time_window: str) -> bool:
        """Send a high error rate alert to Slack."""
        message = (
            "📊 *High Error Rate Alert*\n\n"
            f"*Project:* {project}\n"
            f"*Environment:* {environment}\n"
            f"*Error Rate:* {error_rate:.2f}%\n"
            f"*Threshold:* {threshold}%\n"
            f"*Time Window:* {time_window}\n"
            f"*Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            "Please investigate the increased error rate."
        )
        
        return self.send_message(
            channel=f"#{self.channel_name}",
            message=message,
            username="Sentry Alert Bot",
            icon_emoji=":chart_with_upwards_trend:",
            unfurl_links=False
        )
    
    def send_critical_issue_alert(self, project: str, environment: str, issue_level: str,
                                 issue_title: str, issue_url: str) -> bool:
        """Send a critical issue alert to Slack."""
        message = (
            "🔥 *Critical Issue Alert*\n\n"
            f"*Project:* {project}\n"
            f"*Environment:* {environment}\n"
            f"*Issue Level:* {issue_level}\n"
            f"*Issue Title:* {issue_title}\n"
            f"*Issue URL:* {issue_url}\n"
            f"*Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            "This is a critical issue requiring immediate attention!"
        )
        
        return self.send_message(
            channel=f"#{self.channel_name}",
            message=message,
            username="Sentry Alert Bot",
            icon_emoji=":fire:",
            unfurl_links=False
        )
    
    def send_alert_creation_error(self, project: str, error_message: str) -> bool:
        """Send an error notification when alert creation fails."""
        message = (
            "❌ *Alert Creation Error*\n\n"
            f"Failed to create alert rule for project: {project}\n"
            f"*Error:* {error_message}\n"
            f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            "Please check the automation logs for more details."
        )
        
        return self.send_message(
            channel=f"#{self.channel_name}",
            message=message,
            username="Sentry Alert Bot",
            icon_emoji=":x:",
            unfurl_links=False
        )
    
    def send_automation_summary(self, results: Dict[str, int]) -> bool:
        """Send a summary of the automation results."""
        message = (
            "📋 *Sentry Alert Automation Summary*\n\n"
            f"*Successful:* {results.get('success', 0)}\n"
            f"*Failed:* {results.get('failed', 0)}\n"
            f"*Skipped:* {results.get('skipped', 0)}\n"
            f"*Total Processed:* {sum(results.values())}\n"
            f"*Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        )
        
        if results.get('failed', 0) > 0:
            message += "⚠️ Some alerts failed to create. Check logs for details."
        elif results.get('success', 0) > 0:
            message += "✅ Alert creation completed successfully!"
        else:
            message += "ℹ️ No alerts were created."
        
        return self.send_message(
            channel=f"#{self.channel_name}",
            message=message,
            username="Sentry Alert Bot",
            icon_emoji=":clipboard:",
            unfurl_links=False
        )
    
    def test_connection(self) -> bool:
        """Test the Slack connection and permissions."""
        try:
            # Test authentication
            auth_response = self.client.auth_test()
            if not auth_response['ok']:
                self.logger.error("Slack authentication failed")
                return False
            
            # Test channel access
            channel_id = self.get_channel_id(f"#{self.channel_name}")
            if not channel_id:
                self.logger.error(f"Cannot access channel #{self.channel_name}")
                return False
            
            # Test posting permission
            test_response = self.client.chat_postMessage(
                channel=channel_id,
                text="Test message - will be deleted",
                username="Sentry Alert Bot Test"
            )
            
            if test_response['ok']:
                # Delete the test message
                try:
                    self.client.chat_delete(
                        channel=channel_id,
                        ts=test_response['ts']
                    )
                except SlackApiError:
                    # Ignore errors when deleting test message
                    pass
                
                self.logger.info("Slack connection test successful")
                return True
            else:
                self.logger.error("Slack posting permission test failed")
                return False
                
        except SlackApiError as e:
            self.logger.error(f"Slack connection test failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during Slack connection test: {e}")
            return False
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about the Slack workspace."""
        try:
            auth_response = self.client.auth_test()
            return {
                "workspace_name": auth_response.get('team', 'Unknown'),
                "workspace_id": auth_response.get('team_id', 'Unknown'),
                "bot_user_id": auth_response.get('user_id', 'Unknown'),
                "bot_username": auth_response.get('user', 'Unknown'),
                "connected": auth_response.get('ok', False)
            }
        except SlackApiError as e:
            self.logger.error(f"Error getting workspace info: {e}")
            return {
                "workspace_name": "Unknown",
                "workspace_id": "Unknown",
                "bot_user_id": "Unknown",
                "bot_username": "Unknown",
                "connected": False,
                "error": str(e)
            } 