"""
Sentry API Client

This module provides a client for interacting with Sentry's REST API
to manage projects, alert rules, and organizations.
"""

import os
import time
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SentryClient:
    """Client for interacting with Sentry's REST API."""
    
    def __init__(self):
        """Initialize the Sentry client with authentication."""
        self.auth_token = os.getenv('SENTRY_AUTH_TOKEN')
        self.org_slug = os.getenv('SENTRY_ORG_SLUG')
        self.api_base_url = os.getenv('SENTRY_API_BASE_URL', 'https://sentry.io/api/0')
        
        if not self.auth_token:
            raise ValueError("SENTRY_AUTH_TOKEN environment variable is required")
        
        if not self.org_slug:
            raise ValueError("SENTRY_ORG_SLUG environment variable is required")
        
        self.logger = logging.getLogger(__name__)
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'SentryAlertAutomation/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Sentry API with error handling.

        Note: Do NOT use urljoin with a leading '/' in endpoint because it will
        drop the '/api/0' path from the base URL. Build the URL manually.
        """
        url = f"{self.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Debug: Print response details
            self.logger.debug(f"Request URL: {url}")
            self.logger.debug(f"Response Status: {response.status_code}")
            self.logger.debug(f"Response Headers: {dict(response.headers)}")
            self.logger.debug(f"Response Text: {response.text[:500]}...")  # First 500 chars
            
            response.raise_for_status()
            
            # Check if response is empty
            if not response.text.strip():
                self.logger.error("Empty response received from API")
                raise ValueError("Empty response received from API")
            
            # Rate limiting - respect Sentry's rate limits
            if 'X-Sentry-Rate-Limit-Remaining' in response.headers:
                remaining = int(response.headers['X-Sentry-Rate-Limit-Remaining'])
                if remaining < 10:
                    time.sleep(1)  # Add delay if rate limit is low
            
            try:
                return response.json()
            except ValueError as json_error:
                self.logger.error(f"Failed to parse JSON response: {json_error}")
                self.logger.error(f"Response content: {response.text}")
                raise ValueError(f"Invalid JSON response: {json_error}")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            raise

    def _extract_data(self, response: Any):
        """Normalize Sentry API responses that may return either a list or a dict with 'data'."""
        if isinstance(response, list):
            return response
        if isinstance(response, dict):
            if 'data' in response and isinstance(response['data'], list):
                return response['data']
            return response
        return response
    
    def get_organization_info(self) -> Dict[str, Any]:
        """Get information about the Sentry organization."""
        endpoint = f'/organizations/{self.org_slug}/'
        return self._make_request('GET', endpoint)
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects in the organization."""
        endpoint = f'/organizations/{self.org_slug}/projects/'
        response = self._make_request('GET', endpoint)
        return self._extract_data(response)
    
    def get_project(self, project_slug: str) -> Dict[str, Any]:
        """Get information about a specific project."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/'
        return self._make_request('GET', endpoint)
    
    def get_alert_rules(self, project_slug: str) -> List[Dict[str, Any]]:
        """Get all alert rules for a project."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/rules/'
        response = self._make_request('GET', endpoint)
        return self._extract_data(response)
    
    def create_alert_rule(self, project_slug: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert rule for a project."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/rules/'
        return self._make_request('POST', endpoint, json=rule_data)

    def get_rule_configuration(self, project_slug: str) -> Dict[str, Any]:
        """Fetch the rule configuration for a project (conditions/filters/actions and their accepted values)."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/rules/configuration/'
        return self._make_request('GET', endpoint)
    
    def update_alert_rule(self, project_slug: str, rule_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing alert rule."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/rules/{rule_id}/'
        return self._make_request('PUT', endpoint, json=rule_data)
    
    def delete_alert_rule(self, project_slug: str, rule_id: str) -> bool:
        """Delete an alert rule."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/rules/{rule_id}/'
        try:
            self._make_request('DELETE', endpoint)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete alert rule {rule_id}: {e}")
            return False
    
    def get_alert_rule(self, project_slug: str, rule_id: str) -> Dict[str, Any]:
        """Get a specific alert rule."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/rules/{rule_id}/'
        return self._make_request('GET', endpoint)
    
    def check_alert_rule_exists(self, project_slug: str, rule_name: str) -> Optional[str]:
        """Check if an alert rule with the given name exists and return its ID."""
        try:
            rules = self.get_alert_rules(project_slug)
            for rule in rules:
                if rule.get('name') == rule_name:
                    return rule.get('id')
            return None
        except Exception as e:
            self.logger.error(f"Error checking alert rule existence: {e}")
            return None
    
    def get_environments(self, project_slug: str) -> List[Dict[str, Any]]:
        """Get all environments for a project."""
        endpoint = f'/projects/{self.org_slug}/{project_slug}/environments/'
        response = self._make_request('GET', endpoint)
        return self._extract_data(response)
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams in the organization."""
        endpoint = f'/organizations/{self.org_slug}/teams/'
        response = self._make_request('GET', endpoint)
        return self._extract_data(response)
    
    def get_integrations(self) -> List[Dict[str, Any]]:
        """Get all integrations in the organization."""
        endpoint = f'/organizations/{self.org_slug}/integrations/'
        response = self._make_request('GET', endpoint)
        return self._extract_data(response)
    
    def test_connection(self) -> bool:
        """Test the connection to Sentry API."""
        try:
            self.get_organization_info()
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False 