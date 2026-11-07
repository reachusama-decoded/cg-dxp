"""Interactive credential setup for Catalyst client integrations.

Provides validation and guided setup for external system connectors.
No one reads guides — this prompts users interactively with inline instructions.
"""

from __future__ import annotations

import getpass
import os
import sys
import webbrowser
from pathlib import Path
from typing import Literal

# Service → required env vars mapping
SERVICE_CREDENTIALS: dict[str, list[str]] = {
    "jira": ["JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN"],
    "confluence": ["CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN"],
    "github": ["GITHUB_TOKEN"],
    "databricks": ["DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_WAREHOUSE_ID"],
}

# Token generation URLs for each service
TOKEN_URLS: dict[str, str] = {
    "jira": "https://id.atlassian.com/manage-profile/security/api-tokens",
    "confluence": "https://id.atlassian.com/manage-profile/security/api-tokens",
    "github": "https://github.com/settings/tokens/new?scopes=repo,read:org,workflow&description=Catalyst%20DPLC",
}

Service = Literal["jira", "confluence", "github", "databricks"]


def check_integration(service: Service) -> tuple[bool, list[str]]:
    """Check if a service integration is configured.
    
    Args:
        service: Service name ("jira", "confluence", "github", "databricks").
        
    Returns:
        Tuple of (ready: bool, missing_vars: list[str]).
        
    Example:
        ready, missing = check_integration("jira")
        if not ready:
            print(f"Missing: {', '.join(missing)}")
    """
    required = SERVICE_CREDENTIALS.get(service, [])
    missing = [var for var in required if not os.environ.get(var)]
    return (len(missing) == 0, missing)


def guide_setup(service: Service) -> bool:
    """Interactive guide to set up credentials for a service.
    
    Opens browser to token generation page, prompts user for values,
    and saves to .env file in the project root.
    
    Args:
        service: Service name to configure.
        
    Returns:
        True if setup completed successfully, False if user cancelled.
        
    Example:
        if not check_integration("jira")[0]:
            success = guide_setup("jira")
            if success:
                print("Jira configured!")
    """
    print(f"\n{'='*60}")
    print(f"🔧 Setting up {service.upper()} integration")
    print(f"{'='*60}\n")
    
    # Check current status
    ready, missing = check_integration(service)
    if ready:
        print(f"✅ {service.upper()} is already configured!")
        confirm = input("Reconfigure? (y/N): ").strip().lower()
        if confirm != "y":
            return True
    
    # Service-specific setup
    if service in ("jira", "confluence"):
        return _setup_atlassian(service)
    elif service == "github":
        return _setup_github()
    elif service == "databricks":
        return _setup_databricks()
    else:
        print(f"❌ Unknown service: {service}")
        return False


def _setup_atlassian(service: Service) -> bool:
    """Setup for Jira or Confluence (both use Atlassian API tokens)."""
    print(f"To use {service.upper()}, you need an Atlassian API token.\n")
    print("📋 What you'll need:")
    print("  1. Your Atlassian account email")
    print("  2. An API token (we'll help you generate one)\n")
    
    # Get URL
    print(f"Step 1: What's your {service.upper()} URL?")
    if service == "jira":
        print("  Example: https://capitalgroup.atlassian.net")
        url_var = "JIRA_URL"
        default_url = "https://capitalgroup.atlassian.net"
    else:
        print("  Example: https://capitalgroup.atlassian.net/wiki")
        url_var = "CONFLUENCE_URL"
        default_url = "https://capitalgroup.atlassian.net/wiki"
    
    url = input(f"  URL [{default_url}]: ").strip() or default_url
    
    # Get username
    print("\nStep 2: What's your Atlassian account email?")
    print("  Example: your.name@capgroup.com")
    username = input("  Email: ").strip()
    if not username:
        print("❌ Email is required")
        return False
    
    # Get API token
    print("\nStep 3: Generate an API token")
    print("  We'll open the Atlassian API token page in your browser.")
    print("  Click 'Create API token', give it a name (e.g., 'Catalyst'), and copy the token.\n")
    
    open_browser = input("  Open browser now? (Y/n): ").strip().lower()
    if open_browser != "n":
        token_url = TOKEN_URLS[service]
        try:
            webbrowser.open(token_url)
            print(f"  ✅ Opened {token_url}")
        except Exception as e:
            print(f"  ⚠️ Couldn't open browser: {e}")
            print(f"  Please visit manually: {token_url}")
    
    print("\nPaste your API token here:")
    api_token = getpass.getpass("  Token: ").strip()
    if not api_token:
        print("❌ API token is required")
        return False
    
    # Save to .env
    username_var = f"{service.upper()}_USERNAME"
    token_var = f"{service.upper()}_API_TOKEN"
    
    updates = {
        url_var: url,
        username_var: username,
        token_var: api_token,
    }
    
    _update_env_file(updates)
    print(f"\n✅ {service.upper()} configured!")
    print(f"  • {url_var}={url}")
    print(f"  • {username_var}={username}")
    print(f"  • {token_var}=<hidden>")
    
    return True


def _setup_github() -> bool:
    """Setup for GitHub (Personal Access Token)."""
    print("To use GitHub, you need a Personal Access Token (PAT).\n")
    print("📋 What you'll need:")
    print("  • A GitHub PAT with repo, read:org, and workflow scopes\n")
    
    print("We'll open the GitHub token creation page with the right scopes pre-selected.\n")
    
    open_browser = input("  Open browser now? (Y/n): ").strip().lower()
    if open_browser != "n":
        token_url = TOKEN_URLS["github"]
        try:
            webbrowser.open(token_url)
            print(f"  ✅ Opened {token_url}")
        except Exception as e:
            print(f"  ⚠️ Couldn't open browser: {e}")
            print(f"  Please visit manually: {token_url}")
    
    print("\nAfter generating your token, paste it here:")
    print("  (It should start with 'ghp_' or 'github_pat_')")
    token = getpass.getpass("  Token: ").strip()
    if not token:
        print("❌ Token is required")
        return False
    
    # Save to .env
    _update_env_file({"GITHUB_TOKEN": token})
    print("\n✅ GitHub configured!")
    print("  • GITHUB_TOKEN=<hidden>")
    
    return True


def _setup_databricks() -> bool:
    """Setup for Databricks (host + token + warehouse)."""
    print("To use Databricks, you need a workspace URL, personal access token, and warehouse ID.\n")
    print("📋 What you'll need:")
    print("  1. Databricks workspace URL")
    print("  2. Personal access token (User Settings → Access Tokens)")
    print("  3. SQL Warehouse ID (SQL → Warehouses → click warehouse → see URL)\n")
    
    # Get host
    print("Step 1: What's your Databricks workspace URL?")
    print("  Example: https://your-workspace.cloud.databricks.com")
    host = input("  URL: ").strip()
    if not host:
        print("❌ Workspace URL is required")
        return False
    
    # Get token
    print("\nStep 2: Generate a personal access token")
    print("  In Databricks: User Settings → Access Tokens → Generate New Token")
    token = getpass.getpass("  Token: ").strip()
    if not token:
        print("❌ Token is required")
        return False
    
    # Get warehouse ID
    print("\nStep 3: Find your SQL Warehouse ID")
    print("  In Databricks: SQL → Warehouses → click a warehouse")
    print("  The ID is in the URL: /sql/warehouses/<warehouse_id>")
    warehouse_id = input("  Warehouse ID: ").strip()
    if not warehouse_id:
        print("❌ Warehouse ID is required")
        return False
    
    # Save to .env
    updates = {
        "DATABRICKS_HOST": host,
        "DATABRICKS_TOKEN": token,
        "DATABRICKS_WAREHOUSE_ID": warehouse_id,
    }
    
    _update_env_file(updates)
    print("\n✅ Databricks configured!")
    print(f"  • DATABRICKS_HOST={host}")
    print("  • DATABRICKS_TOKEN=<hidden>")
    print(f"  • DATABRICKS_WAREHOUSE_ID={warehouse_id}")
    
    return True


def _update_env_file(updates: dict[str, str]) -> None:
    """Update or create .env file with new credentials.
    
    Args:
        updates: Dict of env var name → value to set.
    """
    # Find project root (look for plugin.json or pyproject.toml)
    current = Path.cwd()
    while current != current.parent:
        if (current / "plugin.json").exists() or (current / "pyproject.toml").exists():
            break
        current = current.parent
    else:
        # Fallback to cwd
        current = Path.cwd()
    
    env_file = current / ".env"
    
    # Read existing .env if it exists
    existing = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    existing[key.strip()] = value.strip()
    
    # Merge updates
    existing.update(updates)
    
    # Write back
    with open(env_file, "w") as f:
        f.write("# Catalyst DPLC credentials\n")
        f.write("# Generated by skills/clients/setup.py\n\n")
        
        # Group by service
        for service in ["jira", "confluence", "github", "databricks"]:
            service_vars = {k: v for k, v in existing.items() if k.startswith(service.upper())}
            if service_vars:
                f.write(f"# {service.upper()}\n")
                for key, value in service_vars.items():
                    f.write(f"{key}={value}\n")
                f.write("\n")
        
        # Write any other vars
        other_vars = {
            k: v for k, v in existing.items()
            if not any(k.startswith(s.upper()) for s in ["jira", "confluence", "github", "databricks"])
        }
        if other_vars:
            f.write("# Other\n")
            for key, value in other_vars.items():
                f.write(f"{key}={value}\n")
    
    # Set restrictive permissions (user read/write only)
    try:
        os.chmod(env_file, 0o600)
    except (OSError, AttributeError):
        # Windows or permission denied — continue anyway
        pass
    
    # Update environment for current process
    for key, value in updates.items():
        os.environ[key] = value
    
    print(f"\n💾 Saved to {env_file}")


if __name__ == "__main__":
    # CLI interface for testing
    if len(sys.argv) < 2:
        print("Usage: python -m skills.clients.setup <service>")
        print("Services: jira, confluence, github, databricks")
        sys.exit(1)
    
    service = sys.argv[1].lower()
    if service not in SERVICE_CREDENTIALS:
        print(f"Unknown service: {service}")
        print(f"Available: {', '.join(SERVICE_CREDENTIALS.keys())}")
        sys.exit(1)
    
    success = guide_setup(service)  # type: ignore
    sys.exit(0 if success else 1)
