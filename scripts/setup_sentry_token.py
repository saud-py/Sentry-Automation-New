#!/usr/bin/env python3
"""
Sentry Token Setup Script

This script helps users generate and configure Sentry authentication tokens
for the alert automation system.
"""

import os
import sys
import getpass
from pathlib import Path

# Add src directory to path for imports
current_file = Path(__file__)
project_root = current_file.parent.parent
src_path = project_root / "src"
sys.path.append(str(src_path))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from utils.validators import validate_sentry_token

console = Console()

def print_setup_instructions():
    """Print instructions for setting up Sentry authentication."""
    instructions = """
    [bold blue]Sentry Authentication Token Setup[/bold blue]
    
    To use this automation, you need a Sentry authentication token with the following permissions:
    
    [bold]Required Permissions:[/bold]
    • project:read - To read project information
    • project:write - To create and manage alert rules
    • org:read - To read organization information
    
    [bold]How to generate a token:[/bold]
    1. Go to your Sentry organization settings
    2. Navigate to "Developer Settings" → "New Internal Integration"
    3. Give it a name like "Alert Automation"
    4. Add the required permissions listed above
    5. Save the integration and copy the token
    
    [bold]Security Note:[/bold]
    • Store the token securely
    • Use environment variables, not hardcoded values
    • Rotate tokens regularly
    """
    
    console.print(Panel(instructions, title="Setup Instructions", border_style="blue"))

def validate_token_format(token: str) -> bool:
    """Validate the token format."""
    if not token:
        return False
    
    if not validate_sentry_token(token):
        console.print("[red]Invalid token format. Please check your token.[/red]")
        return False
    
    return True

def test_token_connection(token: str, org_slug: str) -> bool:
    """Test the token connection to Sentry."""
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test organization access
        url = f"https://sentry.io/api/0/organizations/{org_slug}/"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            org_data = response.json()
            console.print(f"[green]✓ Successfully connected to organization: {org_data.get('name', 'Unknown')}[/green]")
            return True
        elif response.status_code == 403:
            console.print("[red]✗ Token lacks required permissions[/red]")
            return False
        elif response.status_code == 404:
            console.print("[red]✗ Organization not found or token lacks access[/red]")
            return False
        else:
            console.print(f"[red]✗ Connection failed with status code: {response.status_code}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ Connection test failed: {e}[/red]")
        return False

def create_env_file(token: str, org_slug: str):
    """Create or update the .env file with the token."""
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    # Read the example file if it exists
    env_content = ""
    if env_example.exists():
        with open(env_example, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Update or add the token and org slug
    lines = env_content.split('\n') if env_content else []
    updated_lines = []
    
    # Track if we've updated the required variables
    token_updated = False
    org_updated = False
    
    for line in lines:
        if line.startswith('SENTRY_AUTH_TOKEN='):
            updated_lines.append(f'SENTRY_AUTH_TOKEN={token}')
            token_updated = True
        elif line.startswith('SENTRY_ORG_SLUG='):
            updated_lines.append(f'SENTRY_ORG_SLUG={org_slug}')
            org_updated = True
        else:
            updated_lines.append(line)
    
    # Add missing variables
    if not token_updated:
        updated_lines.append(f'SENTRY_AUTH_TOKEN={token}')
    if not org_updated:
        updated_lines.append(f'SENTRY_ORG_SLUG={org_slug}')
    
    # Write the .env file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    console.print(f"[green]✓ Environment file updated: {env_file}[/green]")

def main():
    """Main setup function."""
    console.print(Panel.fit(
        "[bold blue]Sentry Alert Automation - Token Setup[/bold blue]\n"
        "This script will help you configure your Sentry authentication token.",
        border_style="blue"
    ))
    
    # Show setup instructions
    print_setup_instructions()
    
    # Get user input
    console.print("\n[bold]Enter your Sentry configuration:[/bold]")
    
    # Get organization slug
    org_slug = Prompt.ask(
        "Sentry Organization Slug",
        default="paywithring"
    )
    
    # Get authentication token
    console.print("\n[yellow]Enter your Sentry authentication token:[/yellow]")
    console.print("(The token will be hidden when you type)")
    
    token = getpass.getpass("Token: ").strip()
    
    if not token:
        console.print("[red]No token provided. Exiting.[/red]")
        sys.exit(1)
    
    # Validate token format
    if not validate_token_format(token):
        console.print("[red]Token format validation failed. Please check your token.[/red]")
        sys.exit(1)
    
    # Test token connection
    console.print("\n[bold]Testing token connection...[/bold]")
    if not test_token_connection(token, org_slug):
        console.print("[red]Token test failed. Please check your token and permissions.[/red]")
        sys.exit(1)
    
    # Ask if user wants to save to .env file
    save_to_env = Confirm.ask(
        "\nDo you want to save these settings to a .env file?",
        default=True
    )
    
    if save_to_env:
        create_env_file(token, org_slug)
        console.print("\n[green]✓ Configuration saved successfully![/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Configure your Slack integration")
        console.print("2. Run: python scripts/verify_slack_integration.py")
        console.print("3. Run: python src/main.py --verify-connection")
    else:
        console.print("\n[yellow]Configuration not saved. You'll need to set environment variables manually.[/yellow]")
        console.print(f"Set SENTRY_AUTH_TOKEN={token}")
        console.print(f"Set SENTRY_ORG_SLUG={org_slug}")
    
    console.print("\n[green]Token setup completed![/green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Setup failed: {e}[/red]")
        sys.exit(1) 