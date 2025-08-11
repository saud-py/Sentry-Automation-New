#!/usr/bin/env python3
"""
Sentry Projects List Script

This script lists all projects in your Sentry organization
to help you understand what projects are available for alert automation.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
current_file = Path(__file__)
project_root = current_file.parent.parent
src_path = project_root / "src"
sys.path.append(str(src_path))

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from sentry_client import SentryClient

# Load environment variables
load_dotenv()

console = Console()

def display_projects(projects: list):
    """Display projects in a formatted table."""
    if not projects:
        console.print("[yellow]No projects found in the organization.[/yellow]")
        return
    
    # Create table
    table = Table(title="Sentry Projects")
    table.add_column("Project Name", style="cyan", no_wrap=True)
    table.add_column("Project Slug", style="green", no_wrap=True)
    table.add_column("Platform", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Team", style="blue")
    table.add_column("Date Created", style="dim")
    
    for project in projects:
        # Format date if available
        date_created = project.get('dateCreated', 'N/A')
        if date_created != 'N/A':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(date_created.replace('Z', '+00:00'))
                date_created = dt.strftime('%Y-%m-%d')
            except:
                pass
        
        table.add_row(
            project.get('name', 'N/A'),
            project.get('slug', 'N/A'),
            project.get('platform', 'N/A'),
            project.get('status', 'N/A'),
            project.get('team', {}).get('name', 'N/A'),
            date_created
        )
    
    console.print(table)
    console.print(f"\n[green]Found {len(projects)} projects[/green]")

def filter_projects(projects: list, filter_type: str = None, filter_value: str = None):
    """Filter projects based on criteria."""
    if not filter_type or not filter_value:
        return projects
    
    filtered_projects = []
    
    for project in projects:
        if filter_type == 'platform':
            if project.get('platform', '').lower() == filter_value.lower():
                filtered_projects.append(project)
        elif filter_type == 'status':
            if project.get('status', '').lower() == filter_value.lower():
                filtered_projects.append(project)
        elif filter_type == 'team':
            team_name = project.get('team', {}).get('name', '').lower()
            if filter_value.lower() in team_name:
                filtered_projects.append(project)
        elif filter_type == 'name':
            project_name = project.get('name', '').lower()
            if filter_value.lower() in project_name:
                filtered_projects.append(project)
    
    return filtered_projects

def export_projects_csv(projects: list, filename: str = "sentry_projects.csv"):
    """Export projects to CSV file."""
    import csv
    
    try:
        csv_path = project_root / filename
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'slug', 'platform', 'status', 'team', 'dateCreated']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for project in projects:
                # Flatten team info
                row = {
                    'name': project.get('name', ''),
                    'slug': project.get('slug', ''),
                    'platform': project.get('platform', ''),
                    'status': project.get('status', ''),
                    'team': project.get('team', {}).get('name', ''),
                    'dateCreated': project.get('dateCreated', '')
                }
                writer.writerow(row)
        
        console.print(f"[green]✓ Projects exported to {csv_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to export projects: {e}[/red]")
        return False

def main():
    """Main function to list projects."""
    console.print(Panel.fit(
        "[bold blue]Sentry Projects Lister[/bold blue]\n"
        "This script lists all projects in your Sentry organization.",
        border_style="blue"
    ))
    
    try:
        # Initialize Sentry client
        sentry_client = SentryClient()
        
        # Test connection
        console.print("[bold]Testing Sentry connection...[/bold]")
        if not sentry_client.test_connection():
            console.print("[red]Failed to connect to Sentry. Please check your configuration.[/red]")
            sys.exit(1)
        
        # Get organization info
        org_info = sentry_client.get_organization_info()
        console.print(f"[green]✓ Connected to organization: {org_info.get('name', 'Unknown')}[/green]")
        
        # Get projects
        console.print("\n[bold]Fetching projects...[/bold]")
        projects = sentry_client.get_projects()
        
        if not projects:
            console.print("[yellow]No projects found in the organization.[/yellow]")
            return
        
        # Display projects
        display_projects(projects)
        
        # Ask for filtering
        filter_choice = Prompt.ask(
            "\nWould you like to filter projects?",
            choices=["n", "platform", "status", "team", "name"],
            default="n"
        )
        
        if filter_choice != "n":
            filter_value = Prompt.ask(f"Enter {filter_choice} to filter by")
            filtered_projects = filter_projects(projects, filter_choice, filter_value)
            
            if filtered_projects:
                console.print(f"\n[bold]Filtered projects ({len(filtered_projects)} found):[/bold]")
                display_projects(filtered_projects)
            else:
                console.print(f"[yellow]No projects found matching '{filter_value}'[/yellow]")
        
        # Ask for export
        export_choice = Confirm.ask(
            "\nWould you like to export the projects to CSV?",
            default=False
        )
        
        if export_choice:
            filename = Prompt.ask(
                "Enter filename for export",
                default="sentry_projects.csv"
            )
            export_projects_csv(projects, filename)
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("• Use project slugs to create alerts for specific projects")
        console.print("• Run: python src/main.py --projects project1,project2")
        console.print("• Run: python src/main.py (for all projects)")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Operation failed: {e}[/red]")
        sys.exit(1) 