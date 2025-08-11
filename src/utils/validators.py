"""
Validation utilities for Sentry Alert Automation.

This module provides validation functions for configuration
and input parameters used throughout the application.
"""

import os
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

def validate_config(sentry_config: Dict[str, Any], alert_config: Dict[str, Any]) -> bool:
    """
    Validate the Sentry and alert configuration.
    
    Args:
        sentry_config: Sentry configuration dictionary
        alert_config: Alert configuration dictionary
    
    Returns:
        True if configuration is valid, raises ValueError otherwise
    
    Raises:
        ValueError: If configuration is invalid
    """
    errors = []
    
    # Validate Sentry configuration
    if not sentry_config:
        errors.append("Sentry configuration is empty")
    else:
        # Check required Sentry config fields
        org_config = sentry_config.get('organization', {})
        if not org_config.get('slug'):
            errors.append("Sentry organization slug is required")
        
        # Validate project configuration
        projects_config = sentry_config.get('projects', {})
        if not isinstance(projects_config, dict):
            errors.append("Projects configuration must be a dictionary")
        
        # Validate environment configuration
        environments_config = sentry_config.get('environments', {})
        if not isinstance(environments_config, dict):
            errors.append("Environments configuration must be a dictionary")
    
    # Validate alert configuration
    if not alert_config:
        errors.append("Alert configuration is empty")
    else:
        # Check required alert config fields
        alert_rules = alert_config.get('alert_rules', {})
        if not alert_rules:
            errors.append("Alert rules configuration is required")
        
        # Validate escalating issues alert
        escalating_config = alert_rules.get('escalating_issues', {})
        if not escalating_config:
            errors.append("Escalating issues alert configuration is required")
        else:
            if not escalating_config.get('name'):
                errors.append("Escalating issues alert name is required")
            if not escalating_config.get('actions'):
                errors.append("Escalating issues alert actions are required")
    
    # Validate Slack configuration
    slack_config = alert_config.get('slack', {})
    if not slack_config:
        errors.append("Slack configuration is required")
    else:
        if not slack_config.get('channel_name'):
            errors.append("Slack channel name is required")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True

def validate_environment_variables() -> List[str]:
    """
    Validate required environment variables.
    
    Returns:
        List of missing environment variables
    """
    required_vars = [
        'SENTRY_AUTH_TOKEN',
        'SENTRY_ORG_SLUG',
        'SLACK_BOT_TOKEN',
        'SLACK_WORKSPACE_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def validate_sentry_token(token: str) -> bool:
    """
    Validate Sentry authentication token format.
    
    Args:
        token: The Sentry authentication token
    
    Returns:
        True if token format is valid
    """
    if not token:
        return False
    
    # Sentry tokens are typically alphanumeric and may contain hyphens
    # They are usually 40+ characters long
    token_pattern = r'^[a-zA-Z0-9\-_]{40,}$'
    return bool(re.match(token_pattern, token))

def validate_slack_token(token: str) -> bool:
    """
    Validate Slack bot token format.
    
    Args:
        token: The Slack bot token
    
    Returns:
        True if token format is valid
    """
    if not token:
        return False
    
    # Slack bot tokens start with 'xoxb-'
    slack_pattern = r'^xoxb-[a-zA-Z0-9\-]+$'
    return bool(re.match(slack_pattern, token))

def validate_project_slug(slug: str) -> bool:
    """
    Validate Sentry project slug format.
    
    Args:
        slug: The project slug
    
    Returns:
        True if slug format is valid
    """
    if not slug:
        return False
    
    # Project slugs are lowercase, alphanumeric, and may contain hyphens
    slug_pattern = r'^[a-z0-9\-]+$'
    return bool(re.match(slug_pattern, slug))

def validate_channel_name(channel: str) -> bool:
    """
    Validate Slack channel name format.
    
    Args:
        channel: The channel name
    
    Returns:
        True if channel name format is valid
    """
    if not channel:
        return False
    
    # Remove # if present
    channel = channel.lstrip('#')
    
    # Slack channel names are lowercase, alphanumeric, and may contain hyphens/underscores
    channel_pattern = r'^[a-z0-9\-_]+$'
    return bool(re.match(channel_pattern, channel))

def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: The URL to validate
    
    Returns:
        True if URL format is valid
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_alert_frequency(frequency: int) -> bool:
    """
    Validate alert frequency value.
    
    Args:
        frequency: The alert frequency in minutes
    
    Returns:
        True if frequency is valid
    """
    return isinstance(frequency, int) and 1 <= frequency <= 1440  # 1 minute to 24 hours

def validate_environment_name(environment: str) -> bool:
    """
    Validate environment name.
    
    Args:
        environment: The environment name
    
    Returns:
        True if environment name is valid
    """
    if not environment:
        return False
    
    # Environment names are typically lowercase, alphanumeric, and may contain hyphens
    env_pattern = r'^[a-z0-9\-]+$'
    return bool(re.match(env_pattern, environment))

def validate_workspace_id(workspace_id: str) -> bool:
    """
    Validate Slack workspace ID format.
    
    Args:
        workspace_id: The Slack workspace ID
    
    Returns:
        True if workspace ID format is valid
    """
    if not workspace_id:
        return False
    
    # Slack workspace IDs are typically alphanumeric
    workspace_pattern = r'^[A-Z0-9]+$'
    return bool(re.match(workspace_pattern, workspace_id))

def validate_config_file_path(file_path: str) -> bool:
    """
    Validate that a configuration file exists and is readable.
    
    Args:
        file_path: Path to the configuration file
    
    Returns:
        True if file exists and is readable
    """
    import os
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

def validate_alert_rule_data(rule_data: Dict[str, Any]) -> List[str]:
    """
    Validate alert rule data structure.
    
    Args:
        rule_data: The alert rule data dictionary
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    required_fields = ['name', 'description', 'conditions', 'filters', 'actions']
    for field in required_fields:
        if field not in rule_data:
            errors.append(f"Missing required field: {field}")
    
    if 'name' in rule_data and not rule_data['name']:
        errors.append("Alert rule name cannot be empty")
    
    if 'conditions' in rule_data:
        if not isinstance(rule_data['conditions'], list):
            errors.append("Conditions must be a list")
        elif not rule_data['conditions']:
            errors.append("At least one condition is required")
    
    if 'filters' in rule_data:
        if not isinstance(rule_data['filters'], list):
            errors.append("Filters must be a list")
    
    if 'actions' in rule_data:
        if not isinstance(rule_data['actions'], list):
            errors.append("Actions must be a list")
        elif not rule_data['actions']:
            errors.append("At least one action is required")
    
    return errors

def sanitize_project_name(name: str) -> str:
    """
    Sanitize project name for use in alert rules.
    
    Args:
        name: The project name
    
    Returns:
        Sanitized project name
    """
    if not name:
        return "unknown-project"
    
    # Remove special characters and replace with hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '-', name)
    # Remove multiple consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    
    return sanitized.lower() if sanitized else "unknown-project"

def validate_and_sanitize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize configuration data.
    
    Args:
        config: The configuration dictionary
    
    Returns:
        Sanitized configuration dictionary
    
    Raises:
        ValueError: If configuration is invalid
    """
    sanitized_config = config.copy()
    
    # Validate required fields
    if 'organization' not in sanitized_config:
        raise ValueError("Organization configuration is required")
    
    # Sanitize organization slug
    org_slug = sanitized_config['organization'].get('slug', '')
    if not validate_project_slug(org_slug):
        raise ValueError(f"Invalid organization slug: {org_slug}")
    
    # Sanitize project names in configuration
    if 'projects' in sanitized_config:
        projects_config = sanitized_config['projects']
        if 'exclude' in projects_config:
            projects_config['exclude'] = [
                sanitize_project_name(project) 
                for project in projects_config['exclude']
            ]
        if 'include' in projects_config:
            projects_config['include'] = [
                sanitize_project_name(project) 
                for project in projects_config['include']
            ]
    
    return sanitized_config 