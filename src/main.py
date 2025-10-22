#!/usr/bin/env python3
"""
Sentry Alert Automation v2.2 - Core Script

Multi-environment alert creation with environment-specific naming.
Creates separate alert rules for each production environment per project.
Automatically skips projects that already have v2.2 alerts.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from sentry_client import SentryClient
from alert_manager import AlertManager
from utils.logger import setup_logger

load_dotenv()
console = Console()

class SentryAlertAutomation:
    """Main class for v2.2 multi-environment alert automation."""
    
    def __init__(self):
        """Initialize the automation."""
        self.logger = setup_logger()
        self.sentry_client = SentryClient()
        self.alert_manager = AlertManager(self.sentry_client)
        
        # Check Slack integration
        self.slack_enabled = self._check_slack_integration()
    
    def _check_slack_integration(self) -> bool:
        """Check if Slack integration is available."""
        try:
            integrations = self.sentry_client.get_integrations()
            return any(
                integration.get('provider', {}).get('key') == 'slack'
                for integration in integrations
            )
        except Exception:
            return False
    
    def list_projects(self) -> List[dict]:
        """List all projects with environment information."""
        console.print("\n[bold blue]🔍 Fetching Sentry projects...[/bold blue]")
        
        try:
            projects = self.sentry_client.get_projects()
            
            table = Table(title="Sentry Projects")
            table.add_column("Project Name", style="cyan")
            table.add_column("Project Slug", style="green")
            table.add_column("Production Envs", style="yellow")
            
            for project in projects:
                project_slug = project.get('slug')
                prod_envs = self.alert_manager.get_production_environments(project_slug)
                
                table.add_row(
                    project.get('name', 'N/A'),
                    project_slug,
                    ', '.join(prod_envs) if prod_envs else 'None'
                )
            
            console.print(table)
            console.print(f"\n[green]Found {len(projects)} projects[/green]")
            return projects
            
        except Exception as e:
            console.print(f"[red]Error fetching projects: {e}[/red]")
            self.logger.error(f"Error fetching projects: {e}")
            return []
    
    def create_alerts_for_all_projects(self, dry_run: bool = False) -> dict:
        """Create multi-environment alerts for all projects."""
        self.logger.info("🚀 STARTING v2.2 MULTI-ENVIRONMENT ALERT CREATION")
        self.logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
        
        console.print("\n[bold blue]🌍 Creating multi-environment alert rules...[/bold blue]")
        
        if self.slack_enabled:
            console.print("[green]✓ Using Slack notifications[/green]")
        else:
            console.print("[yellow]⚠ Using email notifications[/yellow]")
        
        projects = self.sentry_client.get_projects()
        if not projects:
            console.print("[red]No projects found[/red]")
            return {"success": 0, "failed": 0, "skipped": 0}
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Creating alerts...", total=len(projects))
            
            for project in projects:
                project_slug = project.get('slug')
                project_name = project.get('name', project_slug)
                
                progress.update(task, description=f"Processing {project_name}...")
                
                try:
                    if dry_run:
                        # Show what would be created
                        prod_envs = self.alert_manager.get_production_environments(project_slug)
                        if prod_envs:
                            console.print(f"[yellow]DRY RUN: Would create {len(prod_envs)} alerts for {project_name}[/yellow]")
                            for env in prod_envs:
                                console.print(f"  - Escalating Issues - {env}")
                        results["skipped"] += 1
                    else:
                        # Create alerts for all production environments
                        success_count = self.alert_manager.create_multi_environment_alerts(project_slug)
                        if success_count > 0:
                            results["success"] += success_count
                            console.print(f"[green]✓ Created {success_count} alerts for {project_name}[/green]")
                        else:
                            results["failed"] += 1
                            console.print(f"[red]✗ Failed to create alerts for {project_name}[/red]")
                    
                except Exception as e:
                    results["failed"] += 1
                    console.print(f"[red]✗ Error processing {project_name}: {e}[/red]")
                    self.logger.error(f"Error processing {project_name}: {e}")
                
                progress.advance(task)
        
        self.logger.info(f"✅ Execution completed: {results}")
        return results
    
    def verify_sentry_connection(self) -> bool:
        """Verify Sentry API connection."""
        console.print("\n[bold blue]🔗 Verifying Sentry connection...[/bold blue]")
        
        try:
            org_info = self.sentry_client.get_organization_info()
            console.print(f"[green]✓ Connected to: {org_info.get('name', 'Unknown')}[/green]")
            
            # Check Slack integration
            if self.slack_enabled:
                console.print("[green]✓ Slack integration available[/green]")
            else:
                console.print("[yellow]⚠ Slack integration not configured[/yellow]")
            
            return True
        except Exception as e:
            console.print(f"[red]✗ Connection failed: {e}[/red]")
            return False

@click.command()
@click.option('--projects', '-p', help='Comma-separated list of project slugs')
@click.option('--list-projects', '-l', is_flag=True, help='List all projects with environments')
@click.option('--dry-run', is_flag=True, help='Preview changes without executing')
@click.option('--verify-connection', is_flag=True, help='Verify Sentry connection')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(projects: Optional[str], list_projects: bool, dry_run: bool, 
         verify_connection: bool, debug: bool):
    """Sentry Alert Automation v2.2 - Multi-environment alert creation."""
    
    try:
        automation = SentryAlertAutomation()
        
        if verify_connection:
            if not automation.verify_sentry_connection():
                sys.exit(1)
            return
        
        if list_projects:
            automation.list_projects()
            return
        
        # Create alerts
        if projects:
            project_list = [p.strip() for p in projects.split(',')]
            console.print(f"[blue]Processing specific projects: {', '.join(project_list)}[/blue]")
            # For specific projects, we'd implement similar logic
            results = {"success": 0, "failed": 0, "skipped": 0}  # Placeholder
        else:
            results = automation.create_alerts_for_all_projects(dry_run)
        
        # Display results
        console.print("\n[bold blue]📊 Results Summary:[/bold blue]")
        console.print(f"[green]Success: {results['success']}[/green]")
        console.print(f"[red]Failed: {results['failed']}[/red]")
        console.print(f"[yellow]Skipped: {results['skipped']}[/yellow]")
        
        if results['failed'] > 0:
            console.print("\n[yellow]⚠ Some operations failed. Check logs for details.[/yellow]")
            sys.exit(1)
        elif results['success'] > 0:
            console.print("\n[green]🎉 Alert creation completed successfully![/green]")
    
    except Exception as e:
        console.print(f"[red]💥 Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 