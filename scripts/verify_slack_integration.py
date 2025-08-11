#!/usr/bin/env python3
"""
Slack Integration Verification Script

This script helps users verify and configure Slack integration
for the Sentry alert automation system.
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
from utils.validators import validate_slack_token, validate_workspace_id, validate_channel_name
from slack_integration import SlackIntegration

console = Console()

def print_slack_setup_instructions():
    """Print instructions for setting up Slack integration."""
    instructions = """
    [bold blue]Slack Integration Setup[/bold blue]
    
    To use Slack notifications, you need to configure:
    
    [bold]1. Slack Bot Token:[/bold]
    • Go to https://api.slack.com/apps
    • Create a new app or use existing one
    • Add "chat:write" and "channels:read" scopes
    • Install the app to your workspace
    • Copy the Bot User OAuth Token (starts with xoxb-)
    
    [bold]2. Slack Workspace ID:[/bold]
    • Go to your Slack workspace settings
    • The workspace ID is in the URL or settings
    • Or use the API to get it: https://api.slack.com/methods/auth.test
    
    [bold]3. Channel Name:[/bold]
    • The channel where alerts will be sent
    • Default: sentry-alerts
    • Make sure the bot is invited to the channel
    
    [bold]Security Note:[/bold]
    • Store tokens securely in environment variables
    • Use bot tokens, not user tokens
    • Rotate tokens regularly
    """
    
    console.print(Panel(instructions, title="Slack Setup Instructions", border_style="blue"))

def test_slack_connection(bot_token: str, workspace_id: str, channel_name: str) -> bool:
    """Test the Slack connection with provided credentials."""
    try:
        # Temporarily set environment variables for testing
        os.environ['SLACK_BOT_TOKEN'] = bot_token
        os.environ['SLACK_WORKSPACE_ID'] = workspace_id
        os.environ['SLACK_CHANNEL_NAME'] = channel_name
        
        # Initialize Slack integration
        slack = SlackIntegration()
        
        # Test connection
        console.print("[bold]Testing Slack connection...[/bold]")
        
        # Get workspace info
        workspace_info = slack.get_workspace_info()
        if workspace_info.get('connected'):
            console.print(f"[green]✓ Connected to workspace: {workspace_info.get('workspace_name', 'Unknown')}[/green]")
        else:
            console.print("[red]✗ Failed to connect to Slack workspace[/red]")
            return False
        
        # Test channel access
        channel_id = slack.get_channel_id(f"#{channel_name}")
        if channel_id:
            console.print(f"[green]✓ Channel #{channel_name} found[/green]")
        else:
            console.print(f"[red]✗ Channel #{channel_name} not found or bot lacks access[/red]")
            return False
        
        # Test sending message
        console.print("[bold]Testing message sending...[/bold]")
        if slack.send_test_message():
            console.print("[green]✓ Test message sent successfully[/green]")
            return True
        else:
            console.print("[red]✗ Failed to send test message[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ Slack connection test failed: {e}[/red]")
        return False

def get_workspace_id_from_token(bot_token: str) -> str:
    """Try to get workspace ID from the bot token."""
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {bot_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post('https://slack.com/api/auth.test', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return data.get('team_id', '')
        
        return ''
        
    except Exception:
        return ''

def create_env_file(bot_token: str, workspace_id: str, channel_name: str):
    """Create or update the .env file with Slack configuration."""
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    # Read the example file if it exists
    env_content = ""
    if env_example.exists():
        with open(env_example, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Update or add the Slack variables
    lines = env_content.split('\n') if env_content else []
    updated_lines = []
    
    # Track if we've updated the required variables
    token_updated = False
    workspace_updated = False
    channel_updated = False
    
    for line in lines:
        if line.startswith('SLACK_BOT_TOKEN='):
            updated_lines.append(f'SLACK_BOT_TOKEN={bot_token}')
            token_updated = True
        elif line.startswith('SLACK_WORKSPACE_ID='):
            updated_lines.append(f'SLACK_WORKSPACE_ID={workspace_id}')
            workspace_updated = True
        elif line.startswith('SLACK_CHANNEL_NAME='):
            updated_lines.append(f'SLACK_CHANNEL_NAME={channel_name}')
            channel_updated = True
        else:
            updated_lines.append(line)
    
    # Add missing variables
    if not token_updated:
        updated_lines.append(f'SLACK_BOT_TOKEN={bot_token}')
    if not workspace_updated:
        updated_lines.append(f'SLACK_WORKSPACE_ID={workspace_id}')
    if not channel_updated:
        updated_lines.append(f'SLACK_CHANNEL_NAME={channel_name}')
    
    # Write the .env file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    console.print(f"[green]✓ Environment file updated: {env_file}[/green]")

def main():
    """Main verification function."""
    console.print(Panel.fit(
        "[bold blue]Sentry Alert Automation - Slack Integration Verification[/bold blue]\n"
        "This script will help you verify and configure your Slack integration.",
        border_style="blue"
    ))
    
    # Show setup instructions
    print_slack_setup_instructions()
    
    # Get user input
    console.print("\n[bold]Enter your Slack configuration:[/bold]")
    
    # Get bot token
    console.print("\n[yellow]Enter your Slack bot token:[/yellow]")
    console.print("(The token will be hidden when you type)")
    
    bot_token = getpass.getpass("Bot Token: ").strip()
    
    if not bot_token:
        console.print("[red]No bot token provided. Exiting.[/red]")
        sys.exit(1)
    
    # Validate token format
    if not validate_slack_token(bot_token):
        console.print("[red]Invalid bot token format. Bot tokens should start with 'xoxb-'[/red]")
        sys.exit(1)
    
    # Try to get workspace ID from token
    console.print("\n[bold]Attempting to get workspace ID from token...[/bold]")
    workspace_id = get_workspace_id_from_token(bot_token)
    
    if workspace_id:
        console.print(f"[green]✓ Found workspace ID: {workspace_id}[/green]")
        use_auto_workspace = Confirm.ask(
            "Use this workspace ID?",
            default=True
        )
        if not use_auto_workspace:
            workspace_id = Prompt.ask("Enter workspace ID manually")
    else:
        workspace_id = Prompt.ask("Enter your Slack workspace ID")
    
    # Validate workspace ID
    if not validate_workspace_id(workspace_id):
        console.print("[yellow]Warning: Workspace ID format may be invalid[/yellow]")
    
    # Get channel name
    channel_name = Prompt.ask(
        "Slack channel name (without #)",
        default="sentry-alerts"
    )
    
    # Validate channel name
    if not validate_channel_name(channel_name):
        console.print("[red]Invalid channel name format[/red]")
        sys.exit(1)
    
    # Test Slack connection
    console.print("\n[bold]Testing Slack integration...[/bold]")
    if not test_slack_connection(bot_token, workspace_id, channel_name):
        console.print("[red]Slack integration test failed. Please check your configuration.[/red]")
        sys.exit(1)
    
    # Ask if user wants to save to .env file
    save_to_env = Confirm.ask(
        "\nDo you want to save these settings to a .env file?",
        default=True
    )
    
    if save_to_env:
        create_env_file(bot_token, workspace_id, channel_name)
        console.print("\n[green]✓ Slack configuration saved successfully![/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Configure your Sentry integration")
        console.print("2. Run: python scripts/setup_sentry_token.py")
        console.print("3. Run: python src/main.py --test-slack")
    else:
        console.print("\n[yellow]Configuration not saved. You'll need to set environment variables manually.[/yellow]")
        console.print(f"Set SLACK_BOT_TOKEN={bot_token}")
        console.print(f"Set SLACK_WORKSPACE_ID={workspace_id}")
        console.print(f"Set SLACK_CHANNEL_NAME={channel_name}")
    
    console.print("\n[green]Slack integration verification completed![/green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Verification cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Verification failed: {e}[/red]")
        sys.exit(1) 