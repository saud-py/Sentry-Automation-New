#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentry Alert Automation - Main Script

This script automates the creation of alert rules across all Sentry projects
in the organization to receive timely notifications on Slack when issues
enter the "escalating" state in production environments.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from sentry_client import SentryClient
from alert_manager import AlertManager
from utils.logger import setup_logger
from utils.validators import validate_config

load_dotenv()

# Initialize rich console
console = Console()

class SentryAlertAutomation:
    """Main class for automating Sentry alert rule creation."""
    
    def __init__(self, config_path: str = None):
        """Initialize the automation with configuration."""
        # Determine the project root directory
        if config_path is None:
            # Try to find the project root (where config/ directory is located)
            current_file = Path(__file__)
            project_root = current_file.parent.parent  # Go up from src/ to project root
            config_path = project_root / "config"
        
        self.config_path = Path(config_path)
        self.logger = setup_logger()
        
        # Load configuration
        self.sentry_config = self._load_yaml_config("sentry_config.yaml")
        self.alert_config = self._load_yaml_config("alert_config.yaml")
        
        # Initialize clients
        self.sentry_client = SentryClient()
        self.alert_manager = AlertManager(self.sentry_client)
        
        # Check if Slack integration is available via Sentry integrations
        self.slack_enabled = False
        try:
            integrations = self.sentry_client.get_integrations()
            for integration in integrations:
                provider = integration.get('provider') or {}
                if provider.get('key') == 'slack':
                    self.slack_enabled = True
                    break
        except Exception:
            # Keep slack_enabled as False if integrations cannot be fetched
            pass
        
        # Validate configuration
        validate_config(self.sentry_config, self.alert_config)
    
    def _load_yaml_config(self, filename: str) -> dict:
        """Load YAML configuration file."""
        import yaml
        
        config_file = self.config_path / filename
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def list_projects(self) -> List[dict]:
        """List all projects in the Sentry organization."""
        console.print("\n[bold blue]Fetching Sentry projects...[/bold blue]")
        
        try:
            projects = self.sentry_client.get_projects()
            
            # Create a table to display projects
            table = Table(title="Sentry Projects")
            table.add_column("Project Name", style="cyan")
            table.add_column("Project Slug", style="green")
            table.add_column("Platform", style="yellow")
            table.add_column("Status", style="magenta")
            
            for project in projects:
                table.add_row(
                    project.get('name', 'N/A'),
                    project.get('slug', 'N/A'),
                    project.get('platform', 'N/A'),
                    project.get('status', 'N/A')
                )
            
            console.print(table)
            console.print(f"\n[green]Found {len(projects)} projects[/green]")
            
            return projects
            
        except Exception as e:
            console.print(f"[red]Error fetching projects: {e}[/red]")
            self.logger.error(f"Error fetching projects: {e}")
            return []
    
    def create_alerts_for_all_projects(self, dry_run: bool = False) -> dict:
        """Create alert rules for all projects in the organization."""
        console.print("\n[bold blue]Creating alert rules for all projects...[/bold blue]")
        
        # Show notification method
        if self.slack_enabled:
            console.print("[green]✓ Using Slack notifications[/green]")
        else:
            console.print("[yellow]⚠ Using email notifications (Slack not configured)[/yellow]")
        
        # Get all projects
        projects = self.sentry_client.get_projects()
        
        if not projects:
            console.print("[red]No projects found[/red]")
            return {"success": 0, "failed": 0, "skipped": 0}
        
        # Filter projects based on configuration
        filtered_projects = self._filter_projects(projects)
        
        if not filtered_projects:
            console.print("[yellow]No projects match the filter criteria[/yellow]")
            return {"success": 0, "failed": 0, "skipped": 0}
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Creating alerts...", total=len(filtered_projects))
            
            for project in filtered_projects:
                project_slug = project.get('slug')
                project_name = project.get('name', project_slug)
                
                progress.update(task, description=f"Processing {project_name}...")
                
                try:
                    if dry_run:
                        console.print(f"[yellow]DRY RUN: Would create alert for {project_name}[/yellow]")
                        results["skipped"] += 1
                    else:
                        success = self.alert_manager.create_escalating_alert(project_slug)
                        if success:
                            results["success"] += 1
                            console.print(f"[green]✓ Created alert for {project_name}[/green]")
                        else:
                            results["failed"] += 1
                            console.print(f"[red]✗ Failed to create alert for {project_name}[/red]")
                    
                except Exception as e:
                    results["failed"] += 1
                    console.print(f"[red]✗ Error creating alert for {project_name}: {e}[/red]")
                    self.logger.error(f"Error creating alert for {project_name}: {e}")
                
                progress.advance(task)
        
        return results
    
    def create_alerts_for_specific_projects(self, project_slugs: List[str], dry_run: bool = False) -> dict:
        """Create alert rules for specific projects."""
        console.print(f"\n[bold blue]Creating alert rules for specific projects: {', '.join(project_slugs)}[/bold blue]")
        
        # Show notification method
        if self.slack_enabled:
            console.print("[green]✓ Using Slack notifications[/green]")
        else:
            console.print("[yellow]⚠ Using email notifications (Slack not configured)[/yellow]")
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for project_slug in project_slugs:
            try:
                if dry_run:
                    console.print(f"[yellow]DRY RUN: Would create alert for {project_slug}[/yellow]")
                    results["skipped"] += 1
                else:
                    success = self.alert_manager.create_escalating_alert(project_slug)
                    if success:
                        results["success"] += 1
                        console.print(f"[green]✓ Created alert for {project_slug}[/green]")
                    else:
                        results["failed"] += 1
                        console.print(f"[red]✗ Failed to create alert for {project_slug}[/red]")
                        
            except Exception as e:
                results["failed"] += 1
                console.print(f"[red]✗ Error creating alert for {project_slug}: {e}[/red]")
                self.logger.error(f"Error creating alert for {project_slug}: {e}")
        
        return results
    
    def _filter_projects(self, projects: List[dict]) -> List[dict]:
        """Filter projects based on configuration."""
        config = self.sentry_config.get('projects', {})
        
        # If include_all is True, include all projects
        if config.get('include_all', True):
            filtered_projects = projects
        else:
            # Include only specific projects
            include_list = config.get('include', [])
            filtered_projects = [p for p in projects if p.get('slug') in include_list]
        
        # Exclude specific projects
        exclude_list = config.get('exclude', [])
        filtered_projects = [p for p in filtered_projects if p.get('slug') not in exclude_list]
        
        return filtered_projects
    
    def test_slack_integration(self) -> bool:
        """Test Slack integration by sending a test message."""
        if not self.slack_enabled:
            console.print("[yellow]Slack integration not configured. Skipping test.[/yellow]")
            return True
        
        console.print("\n[bold blue]Testing Slack integration...[/bold blue]")
        
        try:
            # Use the alert manager's Slack integration
            if hasattr(self.alert_manager, 'slack_integration') and self.alert_manager.slack_integration:
                # Test via Sentry's Slack integration
                console.print("[green]✓ Slack integration detected via Sentry[/green]")
                return True
            else:
                # Try direct Slack integration
                from slack_integration import SlackIntegration
                slack = SlackIntegration()
                success = slack.send_test_message()
                if success:
                    console.print("[green]✓ Direct Slack integration test successful[/green]")
                else:
                    console.print("[red]✗ Direct Slack integration test failed[/red]")
                return success
        except Exception as e:
            console.print(f"[red]✗ Slack integration test error: {e}[/red]")
            self.logger.error(f"Slack integration test error: {e}")
            return False
    
    def verify_sentry_connection(self) -> bool:
        """Verify Sentry API connection."""
        console.print("\n[bold blue]Verifying Sentry connection...[/bold blue]")
        
        try:
            org_info = self.sentry_client.get_organization_info()
            console.print(f"[green]✓ Connected to Sentry organization: {org_info.get('name', 'Unknown')}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Sentry connection failed: {e}[/red]")
            self.logger.error(f"Sentry connection failed: {e}")
            return False

@click.command()
@click.option('--projects', '-p', help='Comma-separated list of specific project slugs')
@click.option('--list-projects', '-l', is_flag=True, help='List all projects in the organization')
@click.option('--dry-run', is_flag=True, help='Run without making actual changes')
@click.option('--test-slack', is_flag=True, help='Test Slack integration')
@click.option('--verify-connection', is_flag=True, help='Verify Sentry connection')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(projects: Optional[str], list_projects: bool, dry_run: bool, 
         test_slack: bool, verify_connection: bool, debug: bool):
    """Sentry Alert Automation - Create alert rules across all projects."""
    
    # Set debug logging if requested
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize automation
        automation = SentryAlertAutomation()
        
        # Verify connection if requested
        if verify_connection:
            if not automation.verify_sentry_connection():
                sys.exit(1)
            return
        
        # Test Slack integration if requested
        if test_slack:
            if not automation.test_slack_integration():
                sys.exit(1)
            return
        
        # List projects if requested
        if list_projects:
            automation.list_projects()
            return
        
        # Create alerts
        if projects:
            # Create alerts for specific projects
            project_list = [p.strip() for p in projects.split(',')]
            results = automation.create_alerts_for_specific_projects(project_list, dry_run)
        else:
            # Create alerts for all projects
            results = automation.create_alerts_for_all_projects(dry_run)
        
        # Display results
        console.print("\n[bold blue]Results Summary:[/bold blue]")
        console.print(f"[green]Success: {results['success']}[/green]")
        console.print(f"[red]Failed: {results['failed']}[/red]")
        console.print(f"[yellow]Skipped: {results['skipped']}[/yellow]")
        
        if results['failed'] > 0:
            console.print("\n[yellow]Some alerts failed to create. Check logs for details.[/yellow]")
            sys.exit(1)
        elif results['success'] > 0:
            console.print("\n[green]Alert creation completed successfully![/green]")
        else:
            console.print("\n[yellow]No alerts were created.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logging.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 