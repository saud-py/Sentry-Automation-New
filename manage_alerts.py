#!/usr/bin/env python3
"""
Sentry Alert Management v2.2 - Production Ready

Single command to create v2.2 alerts for new projects while skipping existing ones.
Perfect for ongoing operations after migration is complete.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from sentry_client import SentryClient
from alert_manager import AlertManager
from utils.logger import setup_logger

console = Console()

class AlertManagement:
    """Production-ready alert management for ongoing operations."""
    
    def __init__(self):
        """Initialize alert management."""
        self.logger = setup_logger()
        self.sentry_client = SentryClient()
        self.alert_manager = AlertManager(self.sentry_client)
    
    def show_statistics(self):
        """Show comprehensive alert statistics."""
        console.print("\n[bold blue]📊 Current Alert Statistics[/bold blue]")
        
        try:
            projects = self.sentry_client.get_projects()
            total_projects = len(projects)
            projects_with_alerts = 0
            projects_without_alerts = 0
            total_v2_alerts = 0
            new_projects_needing_alerts = []
            
            for project in projects:
                project_slug = project.get('slug')
                project_name = project.get('name', project_slug)
                alerts = self.alert_manager.get_project_alerts(project_slug)
                
                # Check for v2.2 escalating alerts
                v2_alerts = [
                    alert for alert in alerts 
                    if alert.get('name', '').startswith('Escalating Issues - ')
                ]
                
                if v2_alerts:
                    projects_with_alerts += 1
                    total_v2_alerts += len(v2_alerts)
                else:
                    # Check if project has production environments
                    prod_envs = self.alert_manager.get_production_environments(project_slug)
                    if prod_envs:
                        projects_without_alerts += 1
                        new_projects_needing_alerts.append({
                            'name': project_name,
                            'slug': project_slug,
                            'environments': prod_envs
                        })
            
            # Display statistics
            table = Table(title="Alert Coverage Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Percentage", style="yellow")
            
            table.add_row("Total Projects", str(total_projects), "100%")
            table.add_row("Projects with v2.2 Alerts", str(projects_with_alerts), f"{projects_with_alerts/total_projects*100:.1f}%")
            table.add_row("Projects Needing Alerts", str(projects_without_alerts), f"{projects_without_alerts/total_projects*100:.1f}%")
            table.add_row("Total v2.2 Alerts", str(total_v2_alerts), "")
            
            console.print(table)
            
            # Show projects needing alerts
            if new_projects_needing_alerts:
                console.print(f"\n[bold yellow]🆕 Projects Needing Alerts ({len(new_projects_needing_alerts)}):[/bold yellow]")
                for project in new_projects_needing_alerts[:10]:  # Show first 10
                    env_count = len(project['environments'])
                    console.print(f"  • {project['name']} ({env_count} production environments)")
                
                if len(new_projects_needing_alerts) > 10:
                    console.print(f"  ... and {len(new_projects_needing_alerts) - 10} more projects")
                
                console.print(f"\n[blue]💡 Run 'python3 manage_alerts.py create' to create alerts for these projects[/blue]")
            else:
                console.print(f"\n[green]✅ All projects with production environments have v2.2 alerts![/green]")
            
        except Exception as e:
            console.print(f"[red]Error gathering statistics: {e}[/red]")
    
    def create_alerts_for_new_projects(self, dry_run: bool = False):
        """Create alerts for new projects, skip existing ones."""
        console.print(f"\n[bold blue]🆕 Creating Alerts for New Projects {'(DRY RUN)' if dry_run else ''}[/bold blue]")
        console.print("[dim]Automatically skips projects that already have v2.2 alerts[/dim]")
        
        try:
            projects = self.sentry_client.get_projects()
            results = {
                "new_alerts": 0,
                "skipped_existing": 0,
                "skipped_no_env": 0,
                "failed": 0
            }
            
            new_projects = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("Processing projects...", total=len(projects))
                
                for project in projects:
                    project_slug = project.get('slug')
                    project_name = project.get('name', project_slug)
                    
                    progress.update(task, description=f"Checking {project_name[:30]}...")
                    
                    try:
                        # Check if project already has v2.2 alerts
                        alerts = self.alert_manager.get_project_alerts(project_slug)
                        has_v2_alerts = any(
                            alert.get('name', '').startswith('Escalating Issues - ')
                            for alert in alerts
                        )
                        
                        if has_v2_alerts:
                            results["skipped_existing"] += 1
                            progress.advance(task)
                            continue
                        
                        # Check if project has production environments
                        prod_envs = self.alert_manager.get_production_environments(project_slug)
                        if not prod_envs:
                            results["skipped_no_env"] += 1
                            progress.advance(task)
                            continue
                        
                        # This is a new project needing alerts
                        if dry_run:
                            console.print(f"[yellow]Would create {len(prod_envs)} alerts for {project_name}[/yellow]")
                            for env in prod_envs:
                                console.print(f"  - Escalating Issues - {env}")
                            results["new_alerts"] += len(prod_envs)
                        else:
                            created = self.alert_manager.create_multi_environment_alerts(project_slug)
                            if created > 0:
                                results["new_alerts"] += created
                                new_projects.append(f"{project_name} ({created} alerts)")
                                console.print(f"[green]✓ Created {created} alerts for {project_name}[/green]")
                            else:
                                results["failed"] += 1
                                console.print(f"[red]✗ Failed to create alerts for {project_name}[/red]")
                    
                    except Exception as e:
                        results["failed"] += 1
                        console.print(f"[red]✗ Error processing {project_name}: {e}[/red]")
                    
                    progress.advance(task)
            
            # Display results
            console.print(f"\n[bold]📊 Results Summary:[/bold]")
            
            results_table = Table()
            results_table.add_column("Result", style="cyan")
            results_table.add_column("Count", style="green")
            results_table.add_column("Description", style="white")
            
            results_table.add_row("New Alerts Created", str(results["new_alerts"]), "Alerts for new projects")
            results_table.add_row("Existing Projects Skipped", str(results["skipped_existing"]), "Already have v2.2 alerts")
            results_table.add_row("No Production Env", str(results["skipped_no_env"]), "No production environments")
            results_table.add_row("Failed", str(results["failed"]), "Errors during creation")
            
            console.print(results_table)
            
            if dry_run and results["new_alerts"] > 0:
                console.print(f"\n[blue]👀 This was a dry run. Remove --dry-run to create {results['new_alerts']} alerts.[/blue]")
            elif not dry_run and results["new_alerts"] > 0:
                console.print(f"\n[green]🎉 Successfully created {results['new_alerts']} new v2.2 alerts![/green]")
                if new_projects:
                    console.print(f"[green]New projects with alerts:[/green]")
                    for project in new_projects[:5]:  # Show first 5
                        console.print(f"  • {project}")
                    if len(new_projects) > 5:
                        console.print(f"  ... and {len(new_projects) - 5} more")
            elif results["new_alerts"] == 0:
                console.print(f"\n[green]✅ No new projects found needing alerts. All projects are up to date![/green]")
            
        except Exception as e:
            console.print(f"[red]Error creating alerts: {e}[/red]")

def main():
    """Main function for ongoing alert management."""
    parser = argparse.ArgumentParser(
        description="Sentry Alert Management v2.2 - Production Ready",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Production Commands:
  python3 manage_alerts.py stats                    # Show current alert coverage
  python3 manage_alerts.py create --dry-run         # Preview alerts for new projects
  python3 manage_alerts.py create                   # Create alerts for new projects

Features:
  • Automatically skips projects with existing v2.2 alerts
  • Only creates alerts for new projects with production environments
  • Safe for regular execution (won't duplicate alerts)
        """
    )
    
    parser.add_argument(
        'action',
        choices=['stats', 'create'],
        help='Action to perform'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing'
    )
    
    args = parser.parse_args()
    
    try:
        console.print(Panel.fit(
            "[bold blue]🎯 Sentry Alert Management v2.2[/bold blue]\n"
            f"Action: [yellow]{args.action}[/yellow]\n"
            f"Mode: [{'yellow' if args.dry_run else 'green'}]{'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}[/{'yellow' if args.dry_run else 'green'}]\n"
            "[dim]Automatically skips existing alerts[/dim]",
            title="🚀 Production Ready"
        ))
        
        management = AlertManagement()
        
        if args.action == 'stats':
            management.show_statistics()
        elif args.action == 'create':
            management.create_alerts_for_new_projects(args.dry_run)
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Operation cancelled[/yellow]")
        return 1
    except Exception as e:
        console.print(f"[red]💥 Error: {e}[/red]")
        return 1

if __name__ == "__main__":
    sys.exit(main())