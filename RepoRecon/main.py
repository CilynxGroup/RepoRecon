
import re
import subprocess
import os
import argparse
import boto3
import requests
from rich.console import Console
from rich.table import Table
import pyfiglet
import subprocess
import csv
from rich.table import Table
from rich.panel import Panel
from rich.box import DOUBLE
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import stripe
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.core.exceptions import AzureError
import shutil
import sys
import boto3
import botocore.exceptions
from rich.console import Console
from rich.panel import Panel
console = Console()
import boto3
import botocore.exceptions
from rich.console import Console
from rich.table import Table
from rich.box import DOUBLE
from rich.panel import Panel
console = Console()
import boto3
import botocore.exceptions
from rich.console import Console
from rich.table import Table
from rich.box import DOUBLE
from rich.panel import Panel
console = Console()


# Initialize console for colorful output
console = Console()
TOOL_NAME = "RepoRecon"

def print_tool_banner():
    """
    Print the tool's ASCII art banner.
    """
    ascii_art = pyfiglet.figlet_format(TOOL_NAME)
    console.print(f"[bold cyan]{ascii_art}[/bold cyan]")
    console.print("[bold green]Search everything GitHub has to offer with ease![/bold green]\n")

def search_github(keyword, token):
    """
    Search GitHub for everything related to the provided keyword, handling pagination.
    """
    headers = {"Authorization": f"token {token}"}
    base_url = "https://api.github.com/search"
    endpoints = {
        "repositories": f"{base_url}/repositories?q={keyword}",
    }

    results = {}
    for key, url in endpoints.items():
        all_items = []
        page = 1
        per_page = 100  # Maximum items per page allowed by GitHub
        max_results = 1000  # GitHub search API limit for total items

        while len(all_items) < max_results:
            paginated_url = f"{url}&per_page={per_page}&page={page}"
            response = requests.get(paginated_url, headers=headers)
            
            if response.status_code == 200:
                items = response.json().get("items", [])
                if not items:  # No more items to fetch
                    break
                all_items.extend(items)
                page += 1
            else:
                console.print(f"[red]Failed to fetch {key} on page {page}: {response.status_code} - {response.json().get('message')}[/red]")
                break

        results[key] = all_items[:max_results]  # Limit to max_results
    return results


def display_results(results):
    """
    Display the search results in a structured format.
    """
    if "repositories" in results and results["repositories"]:
        table = Table(title="Repositories", show_lines=True)
        table.add_column("Index", style="cyan", no_wrap=True)
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Stars", style="cyan")
        table.add_column("URL", style="green")
        for idx, repo in enumerate(results["repositories"], start=1):
            table.add_row(str(idx), repo["name"], str(repo["stargazers_count"]), repo["html_url"])
        console.print(table)
    else:
        console.print("[red]No repositories found for the provided keyword.[/red]")


console = Console()

def download_repository(repo_url, destination_dir, token=None):
    """
    Clone a repository from its URL into the specified destination directory.
    If the directory already exists, clone it with a unique name.
    """
    try:
        repo_name = repo_url.split("/")[-1]
        base_destination = os.path.join(destination_dir, repo_name)
        destination = base_destination

        
        # Add token for private repositories
        if token:
            repo_url = repo_url.replace("https://", f"https://{token}@")
        
        # Ensure the destination directory is unique
        counter = 1
        while os.path.exists(destination):
            destination = f"{base_destination}{counter}"
            counter += 1

        # Clone the repository into the unique directory
        subprocess.run(["git", "clone", "--quiet", repo_url, destination], check=True)
        return destination

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error downloading repository {repo_name}: {e}[/red]")
        return None


def validate_azure_credentials(client_id, tenant_id, client_secret):
    """
    Validate Azure credentials using the Azure SDK for Python.
    """
    try:
        if not client_id or not tenant_id or not client_secret:
            console.print("[bold red]-[/bold red] ❌ Azure credentials are incomplete. Validation skipped.")
            return False
        console.print("[bold green]+[/bold green] 🔑 Azure credentials Detected")
        console.print("[bold green]+[/bold green] 🔍 Validating Azure credentials...")

        # Authenticate using the provided credentials
        credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        subscription_client = SubscriptionClient(credential)

        # Try listing subscriptions to validate credentials
        subscriptions = list(subscription_client.subscriptions.list())

        if subscriptions:
            console.print("[bold green]+[/bold green] ✅ Azure credentials validation succeeded!")
            return True
        else:
            console.print("[bold red]-[/bold red] ❌ Azure credentials are incomplete. Validation skipped.")
            return False

    except AzureError as e:
        # Handle specific Azure SDK errors
        error_message = str(e)
        if "invalid_client" in error_message:
           console.print("[bold red]-[/bold red] ❌ Azure credentials are incomplete. Validation skipped.")
        elif "invalid_tenant" in error_message:
           console.print("[bold red]-[/bold red] ❌ Azure credentials are incomplete. Validation skipped.")
        else:
            console.print("[bold red]-[/bold red] ❌ Azure credentials are incomplete. Validation skipped.")
        return False

    except Exception as e:
        console.print("[bold red]-[/bold red] ❌ Azure credentials are incomplete. Validation skipped.")
        return False

def validate_slack_token(token):
    """
    Validate Slack API token by attempting to make a basic request to Slack's API.
    """
    try:
        if not token:
            console.print("[bold red]-[/bold red] ❌ Slack API token is incomplete. Validation skipped.")
            return False
        console.print("[bold green]+[/bold green] 🔑 Slack credentials Detected")
        console.print("[bold green]+[/bold green] 🔍 Validating Slack API token...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://slack.com/api/auth.test", headers=headers)

        if response.status_code == 200 and response.json().get("ok"):
            console.print("[bold green]+[/bold green] ✅ Slack API token Detected!")
            return True
        else:
            console.print("[bold red]-[/bold red] ❌ Slack API token is incomplete. Validation skipped.")
            return False
    except Exception as e:
        console.print("[bold red]-[/bold red] ❌ Slack API token is incomplete. Validation skipped.")
        return False
def validate_heroku_api_key(api_key):
    """
    Validate Heroku API key by attempting to list apps using the Heroku API.
    """
    try:
        
        if not api_key:
            console.print("[bold red]-[/bold red] ❌ Heroku API key is incomplete. Validation skipped.")
            return False

        console.print("[bold green]+[/bold green] 🔑 Heroku API key Detected")
        console.print("[bold green]+[/bold green] 🔍 Validating Slack API token...")
    
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/vnd.heroku+json; version=3"}
        response = requests.get("https://api.heroku.com/apps", headers=headers)

        if response.status_code == 200:
            console.print("[bold green]+[/bold green] ✅ Heroku API key is valid!")
            return True
        else:
            console.print("[bold red]-[/bold red] ❌ Heroku API key is incomplete. Validation skipped.")
            return False
    except Exception as e:
        console.print("[bold red]-[/bold red] ❌ Heroku API key is incomplete. Validation skipped.")
        return False
def validate_stripe_api_key(api_key):
    
    """
    Validate Stripe API key by attempting to retrieve account details using Stripe's API.
    """
    try:
       

        if not api_key:
            console.print("[yellow]Stripe API key is incomplete. Validation skipped.[/yellow]")
            return False

        console.print("[green] + Stripe API key Detected[/green]")
        console.print("+ [blue]Validating Stripe API token...[/blue]")

        # Set the Stripe API key
        stripe.api_key = api_key

        # Make a call to retrieve the account information
        account = stripe.Account.retrieve()
        console.print(
            f"[green]+ Stripe API key is valid![/green]\n"
            f"[cyan]Account Name: {account.get('business_profile', {}).get('name', 'Unknown')}[/cyan]\n"
            f"[magenta]Email: {account.get('email', 'Unknown')}[/magenta]"
        )
        return True

    except stripe.error.AuthenticationError:
        console.print(
            "[red]- Stripe API key validation failed![/red]\n"
            "[red]- Reason: Invalid API key.[/red]\n"
            "[red]- Suggestion: Verify the API key.[/red]"
        )
        return False
    except Exception as e:
        console.print(f"[red]- Stripe API key validation failed![/red]\n[blue]Reason: {str(e)}[/blue]")
        return False
def validate_dropbox_api_key(api_key):
    """
    Validate Dropbox API key by making a basic API request to Dropbox's API.
    """
    try:
        if not api_key:
            console.print("[yellow]Dropbox API key is incomplete. Validation skipped.[/yellow]")
            return False

        console.print("[green]+ Dropbox API key Detected[/green]")
        console.print("+ [blue]Validating Dropbox API token...[/blue]")
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post("https://api.dropboxapi.com/2/check/user", headers=headers)

        if response.status_code == 200:
            console.print("[green]+ Dropbox API key is valid![/green]")
            return True
        else:
            console.print(
                "[red]- Dropbox API key validation failed![/red]\n"
                f"[red]- Reason: {response.json().get('error_summary', 'Unknown error')}[/red]"
            )
            return False
    except Exception as e:
        console.print(f"[red]- Dropbox API key validation failed![/red]\n[blue]Reason: {str(e)}[/blue]")
        return False
def validate_twilio_api_key(api_key, auth_token):
    """
    Validate Twilio API key by making a basic API request to Twilio's API.
    """
    try:
        if not api_key or not auth_token:
            console.print("[yellow]Twilio API key or auth token is incomplete. Validation skipped.[/yellow]")
            return False

        console.print("[green]Twilio API key Detected [/green]")
        console.print("+ [blue]Validating Twilio API token...[/blue]")
        url = "https://api.twilio.com/2010-04-01/Accounts.json"
        response = requests.get(url, auth=(api_key, auth_token))

        if response.status_code == 200:
            console.print("[green]+ Twilio API key is valid![/green]")
            return True
        else:
            console.print(
                "[red]- Twilio API key validation failed![/red]\n"
                f"[red]- Reason: {response.json().get('message', 'Unknown error')}[/red]"
            )
            return False
    except Exception as e:
        console.print(f"[red]- Twilio API key validation failed![/red]\n[yellow]Reason: {str(e)}[/yellow]")
        return False
def validate_github_personal_access_token(token):
    """
    Validate GitHub Personal Access Token by making a basic API request.
    """
    try:
        if not token:
            console.print("[yellow]GitHub token is incomplete. Validation skipped.[/yellow]")
            return False

        console.print("[green]+ GitHub Personal Access Token Detected[/green]")
        console.print("+ [blue]Validating  GitHub Personal Access Token...[/blue]")
        headers = {"Authorization": f"token {token}"}
        response = requests.get("https://api.github.com/user", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            console.print(
                f"[green]+ GitHub token is valid![/green]\n"
                f"[cyan]User: {user_data.get('login', 'Unknown')}[/cyan]\n"
                f"[magenta]Email: {user_data.get('email', 'Unknown')}[/magenta]"
            )
            return True
        else:
            console.print(
                "[red]- GitHub token validation failed![/red]\n"
                f"[red]- Reason: {response.json().get('message', 'Unknown error')}[/red]"
            )
            return False
    except Exception as e:
        console.print(f"[red]- GitHub token validation failed![/red]\n[blue]Reason: {str(e)}[/blue]")
        return False


console = Console()

def extract_value(findings, key, repo_path):
    
    """
    Extracts the value of a specific key and its associated full file path from the Gitleaks findings using regex.
    """
    try:
        results = []
        current_file = None
        findings_lines = findings.splitlines()

        for line in findings_lines:
            # Detect file location in the findings
            file_match = re.search(r"File:\s*([\w./\\-]+)", line)
            if file_match:
                relative_file_path = file_match.group(1).strip()
                current_file = os.path.join(repo_path, relative_file_path)  # Combine repo path with relative file path

            # Match formats like "key: value" or "key = value"
            pattern = rf"{re.escape(key)}\s*[:=]\s*(.+)"
            match = re.search(pattern, line)
            
            if match and current_file:
                value = match.group(1).strip()
                results.append((current_file, value))  # Correct tuple order: (file_path, secret)
        
        return results

    except Exception as e:
        console.print(f"[red]Error extracting value for key '{key}': {e}[/red]")
        return []

def validate_aws_credentials(access_key, secret_key):
    """
    Validates AWS credentials using STS get_caller_identity.
    Returns True if the credentials are valid, otherwise False.
    """
    console.print(
            Panel(
                "[green]AWS Access and Secret keys Detected!.[/green]",
                title="AWS Credential Validation",
                style="green",
            ))
    console.print(
            Panel(
                "[green]Validating AWS keys[/green]",
                title="AWS Credential Validation",
                style="green",
            ))
    try:
        client = boto3.client(
            "sts",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1"
        )
        response = client.get_caller_identity()
        console.print(
            Panel(
                f"[green]✅ AWS Credentials are Valid![/green]\n"
                f"[cyan]Identity:[/cyan] {response}",
                title="AWS Credential Validation",
                style="green",
            )
        )
        return True
    except botocore.parsers.ResponseParserError:
        console.print(
            Panel(
                "[red]❌ Invalid credentials or AWS returned an unexpected empty response.[/red]",
                title="AWS Credential Validation",
                style="red",
            )
        )
        return False
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        console.print(
            Panel(
                f"[red]❌ Credentials validation failed. Error code: {error_code}[/red]",
                title="AWS Credential Validation",
                style="red",
            )
        )
        return False
    except Exception as e:
        console.print(
            Panel(
                f"[red]❌ Unexpected error: {str(e)}[/red]",
                title="AWS Credential Validation",
                style="red",
            )
        )
        return False



def extract_multiple_values(findings, keys, repo_path):
    """
    Extract values (secrets, file paths, rule IDs) from Gitleaks findings.
    Also extracts GitHub links if available.
    """
    results = []
    
    for key in keys:
        key_results = extract_value(findings, key, repo_path)  # Extract values for each key
        if key_results:
            results.extend(key_results)

    # Extract the GitHub link from findings (searching for "Link:")
    link = "N/A"  # Default value if no link is found
    findings_lines = findings.splitlines()

    for line in findings_lines:
        if line.startswith("Link:"):
            link = line.split("Link:", 1)[1].strip()
            break  # Stop after finding the first link

    # Append GitHub link to each result
    final_results = []
    for item in results:
        file_path, secret = item  # Extracted file path and secret
        final_results.append((link, file_path, secret))  # Include the GitHub link

    return final_results


def extract_all_values(text, keywords):
    """
    Extract all occurrences of keywords and their values from the given text.
    """
    values = set()  # Use a set to avoid duplicates
    for keyword in keywords:
        for line in text.splitlines():
            if keyword in line:
                # Extract the value after the keyword
                match = re.search(rf"{keyword}[^:\r\n]*[:=\s]+([^\s]+)", line, re.IGNORECASE)
                if match:
                    values.add(match.group(1).strip())
    return list(values)

# Regex to match ANSI escape sequences
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

def remove_ansi_escape_sequences(text):
    return ANSI_ESCAPE.sub('', text)

def parse_gitleaks_text_output(output):
    """
    Parse the plain text gitleaks output and extract exactly four fields:
       (RuleID, Link, File, Secret)
    Records are assumed to be separated by a blank line.
    """
    secrets = []
    records = output.split("\n\n")
    for record in records:
        if not record.strip():
            continue

        rule = "N/A"
        link = "N/A"
        file_field = "N/A"
        secret = "N/A"

        for line in record.splitlines():
            line = line.strip()
            if line.startswith("RuleID:"):
                parts = line.split(":", 1)
                rule = parts[1].strip() if len(parts) > 1 else "N/A"
            elif line.startswith("Link:"):
                parts = line.split(":", 1)
                link = parts[1].strip() if len(parts) > 1 else "N/A"
            elif line.startswith("File:"):
                parts = line.split(":", 1)
                file_field = parts[1].strip() if len(parts) > 1 else "N/A"
            elif line.startswith("Finding"):
                parts = line.split(":", 1)
                secret = parts[1].strip() if len(parts) > 1 else "N/A"

        # Remove any ANSI escape codes from the extracted fields.
        rule = remove_ansi_escape_sequences(rule)
        link = remove_ansi_escape_sequences(link)
        file_field = remove_ansi_escape_sequences(file_field)
        secret = remove_ansi_escape_sequences(secret)

        secrets.append((rule, link, file_field, secret))
    return secrets

def export_secrets_to_csv(secrets, filename='detected_secrets.csv'):
    """
    Append parsed secret records to a CSV file.
    If a record has more than 4 items, only the first four will be used.
    """
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['RuleID', 'Link', 'File', 'Secret'])
        for record in secrets:
            # If the record is not a tuple or list, skip it.
            if not isinstance(record, (tuple, list)):
                continue
            # Only take the first four elements (pad if needed).
            row = list(record[:4])
            while len(row) < 4:
                row.append("N/A")
            writer.writerow(row)
console = Console()
def run_gitleaks(repo_path, rule_file):
    """
    Run Gitleaks against the specified repository and process its findings.
    Known secrets (AWS, Azure, Slack, etc.) are extracted and displayed in tables.
    Any remaining (general) secrets that do not match these services are printed via general_secret.
    """
    try:
        result = subprocess.run(
            ["gitleaks", "detect", "-s", repo_path, "-v", "--no-banner", f"-c={rule_file}"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        

        if result.returncode == 0:
            # No sensitive data found; remove the repository.
            delete_repository(repo_path)

            
        elif result.returncode == 1:
            findings = result.stdout.strip()
            
            secrets = parse_gitleaks_text_output(findings)
            
            if secrets:
            #   for secret in secrets:
                    #print(secret)
                export_secrets_to_csv(secrets)
            else:
                print("No secrets were parsed from the gitleaks output.")

            # Define keyword lists for various services.
            aws_access_keys = [
                "AWS_ACCESS_KEY_ID", "aws_access_key", "Access Key",
                "awsAccessKeyId", "accessKeyId", "access_key_id", "AWS_KEY",
                "awsKey", "AWSAccessKey", "aws_access_key_id"
            ]
            aws_secret_keys = [
                "AWS_SECRET_ACCESS_KEY", "aws_secret_access", "Secret Key",
                "awsSecretAccessKey", "secret_key", "AWS_SECRET",
                "awsSecret", "AWSSecretKey", "secretAccessKey", "aws_secret_access_key"
            ]
            azure_client_ids = [
                "AZURE_CLIENT_ID", "azure_client_id", "Client ID",
                "azureClientId", "client_id", "\"client_id\""
            ]
            azure_tenant_ids = [
                "AZURE_TENANT_ID", "azure_tenant_id", "Tenant ID",
                "azureTenantId", "tenant_id", "\"tenant_id\""
            ]
            azure_client_secrets = [
                "AZURE_CLIENT_SECRET", "azure_client_secret", "Client Secret",
                "azureClientSecret", "client_secret", "\"client_secret\""
            ]
            slack_tokens = [
                "SLACK_API_TOKEN", "slack_api_token", "Slack API Token",
                "xoxb-", "xoxp-", "xoxa-", "slack_token", "Bot Token", "user_token"
            ]
            heroku_api_keys = [
                "HEROKU_API_KEY", "heroku_api_key", "API Key",
                "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
            ]
            stripe_api_keys = [
                "STRIPE_API_KEY", "stripe_api_key", "sk_live_", "sk_test_",
                "(sk_live_[0-9a-zA-Z]{24})"
            ]
            github_personal_access_tokens = ["ghp_"]
            twilio_api_keys = ["SK", "Key SID"]
            dropbox_api_keys = ["sl.", "API Key"]

            # Extract secrets for each service.
            slack_token_list = extract_multiple_values(findings, slack_tokens, repo_path)
            heroku_api_key_list = extract_multiple_values(findings, heroku_api_keys, repo_path)
            stripe_api_key_list = extract_multiple_values(findings, stripe_api_keys, repo_path)
            github_tokens_list = extract_multiple_values(findings, github_personal_access_tokens, repo_path)
            twilio_api_key_list = extract_multiple_values(findings, twilio_api_keys, repo_path)
            dropbox_api_key_list = extract_multiple_values(findings, dropbox_api_keys, repo_path)
            aws_access_key_list = extract_multiple_values(findings, aws_access_keys, repo_path)
            aws_secret_key_list = extract_multiple_values(findings, aws_secret_keys, repo_path)
            azure_client_id_list = extract_multiple_values(findings, azure_client_ids, repo_path)
            azure_tenant_id_list = extract_multiple_values(findings, azure_tenant_ids, repo_path)
            azure_client_secret_list = extract_multiple_values(findings, azure_client_secrets, repo_path)

            # Group AWS and Azure credentials.
            aws_detected = set(zip(aws_access_key_list, aws_secret_key_list))
            azure_detected = set(zip(azure_client_id_list, azure_tenant_id_list, azure_client_secret_list))

            credentials_found = False

            # Display known secrets per service.
            if slack_token_list:
                credentials_found = True
                slack_table = Table(title="Detected Slack Token Keys", box=DOUBLE, show_lines=True)
                slack_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
                slack_table.add_column("File", style="cyan")
                slack_table.add_column("API Key", style="green")
                for link, file_path, token in slack_token_list:
                    slack_table.add_row(link, file_path, token)
                    validate_slack_token(token)
                console.print(slack_table)
                

            if heroku_api_key_list:
                credentials_found = True
                heroku_table = Table(title="Detected Heroku API Keys", box=DOUBLE, show_lines=True)
                heroku_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
                heroku_table.add_column("File", style="cyan")
                heroku_table.add_column("API Key", style="green")
                #print(heroku_api_key_list)
                for link, api_key, filepath in heroku_api_key_list:
                    heroku_table.add_row(link, api_key, filepath if api_key else "N/A")
                    validate_heroku_api_key(api_key)
                console.print(heroku_table)
                
            

            if stripe_api_key_list:
                credentials_found = True
                stripe_table = Table(title="Detected Stripe API Keys", box=DOUBLE, show_lines=True)
                stripe_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
                stripe_table.add_column("File", style="cyan")
                stripe_table.add_column("API Key", style="green")
                
                for link, filepath, api_key in stripe_api_key_list:
                    stripe_table.add_row(link, filepath, api_key if api_key else "N/A")
                    validate_stripe_api_key(api_key)
                console.print(stripe_table)
                
            if github_tokens_list:
                credentials_found = True
                github_table = Table(title="Detected GitHub Personal Access Tokens", box=DOUBLE, show_lines=True)
                github_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
                github_table.add_column("File", style="cyan")
                github_table.add_column("Token", style="green")
                for link, token, filepath in github_tokens_list:
                    github_table.add_row(link, filepath, token if token else "N/A")
                    validate_github_personal_access_token(token)
                console.print(github_table)

            if twilio_api_key_list:
                credentials_found = True
                twilio_table = Table(title="Detected Twilio API Keys", box=DOUBLE, show_lines=True)
                twilio_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
                twilio_table.add_column("File", style="cyan")
                twilio_table.add_column("API Key", style="green")
                for link, api_key, filepath in twilio_api_key_list:
                    twilio_table.add_row(link,filepath, api_key if api_key else "N/A")
                    # Replace "your_auth_token" with an actual token or retrieve it dynamically.
                    validate_twilio_api_key(api_key, "your_auth_token")
                console.print(twilio_table)

            if dropbox_api_key_list:
                credentials_found = True
                dropbox_table = Table(title="Detected Dropbox API Keys", box=DOUBLE, show_lines=True)
                dropbox_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
                dropbox_table.add_column("File", style="cyan")
                dropbox_table.add_column("API Key", style="green")
                for link, api_key, filepath in dropbox_api_key_list:
                    dropbox_table.add_row(link ,filepath, api_key if api_key else "N/A")
                    validate_dropbox_api_key(api_key)
                console.print(dropbox_table)

            if aws_detected:
                credentials_found = True
                aws_table = Table(title="Detected AWS Credentials", box=DOUBLE, show_lines=True)
                aws_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
                aws_table.add_column("File", style="cyan")
                aws_table.add_column("Access Key", style="green")
                aws_table.add_column("Secret Key", style="green")
                #print(aws_detected)
                for ((link, access_filepath, access_key), (link,secret_filepath, secret_key)) in aws_detected:
                    if access_key and secret_key:
                        aws_table.add_row(
                            link,
                            access_filepath or secret_filepath,
                            access_key,
                            secret_key
                        )
                        validate_aws_credentials(access_key, secret_key)
                console.print(aws_table)
                #export_secrets_to_csv(aws_detected)

            if azure_detected:
                credentials_found = True
                azure_table = Table(title="Detected Azure Credentials", box=DOUBLE, show_lines=True)
                azure_table.add_column("Link", style="cyan",no_wrap=False, overflow="fold")
                azure_table.add_column("File", style="cyan")
                azure_table.add_column("Client ID", style="green")
                azure_table.add_column("Tenant ID", style="green")
                azure_table.add_column("Client Secret", style="green")
                for ((link, client_id, client_filepath), (link ,tenant_id, tenant_filepath), (link, client_secret, secret_filepath)) in azure_detected:
                    if client_id and tenant_id and client_secret:
                        azure_table.add_row(
                            link,
                            client_filepath or tenant_filepath or secret_filepath,
                            client_id,
                            tenant_id,
                            client_secret
                        )
                        validate_azure_credentials(tenant_id, client_id, client_secret)
                console.print(azure_table)

            # Collect all known secret values from the extractions.
            known_secrets = set()
            
            for secret_list in [
                slack_token_list, heroku_api_key_list, stripe_api_key_list,
                github_tokens_list, twilio_api_key_list, dropbox_api_key_list
            ]:
                for link,secret,filepath in secret_list:
                    if secret:
                        known_secrets.add(secret)
            #print(aws_access_key_list)
            for x,secret, _ in aws_access_key_list:
                if secret:
                    known_secrets.add(secret)
            for link,secret, _ in aws_secret_key_list:
                if secret:
                    known_secrets.add(secret)
            for link,secret, _ in azure_client_id_list:
                if secret:
                    known_secrets.add(secret)
            for link, secret, _ in azure_tenant_id_list:
                if secret:
                    known_secrets.add(secret)
            for link,secret, _ in azure_client_secret_list:
                if secret:
                    known_secrets.add(secret)

            # Filter out lines in the gitleaks output that contain any known secret.
            unknown_lines = []
            for line in findings.splitlines():
                if not any(known_secret in line for known_secret in known_secrets):
                    unknown_lines.append(line)

            # Print general (unclassified) secrets if found.
            if unknown_lines:
                general_secret("\n".join(unknown_lines), repo_path)
            # If no known credentials were identified at all, treat entire output as general secrets.
            elif not credentials_found:
                general_secret(findings, repo_path)
            else:
                console.print(Panel(
                    "[red]Please ensure to use gitleaks rules.toml file[/red]",
                    title="Generic Secrets",
                    box=DOUBLE
                ))
            
                
    except FileNotFoundError:
        console.print("[red]❌ Gitleaks is not installed or not in PATH. Please install Gitleaks and try again.[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error running Gitleaks: {e}[/red]")

def general_secret(gitleak_findings, filepath):
    """
    Reads gitleaks output from standard input, parses each finding block,
    and prints the secret along with its corresponding RuleID.
    """
    
    input_text = gitleak_findings
    lines = input_text.splitlines()
    findings = []
    block = []

    for line in lines:
        if not line.strip():
            if block:
                secret = None
                rule = None
                link = None
                for b in block:
                    if b.startswith("Finding:"):
                        secret = b.split("Finding:", 1)[1].strip()
                    elif b.startswith("RuleID:"):
                        rule = b.split("RuleID:", 1)[1].strip()
                    elif b.startswith("Link:"):
                        link = b.split("Link:", 1)[1].strip()
                if secret and rule and link:
                    # Append a tuple with a consistent structure: (link, secret, rule, filepath)
                    findings.append((link, secret, rule, filepath))
                block = []
        else:
            block.append(line)

    # Process any remaining block not terminated by a blank line.
    if block:
        secret = None
        rule = None
        link = None
        for b in block:
            if b.startswith("Finding:"):
                secret = b.split("Finding:", 1)[1].strip()
            elif b.startswith("RuleID:"):
                rule = b.split("RuleID:", 1)[1].strip()
            elif b.startswith("Link:"):
                link = b.split("Link:", 1)[1].strip()
        if secret and rule and link:
            findings.append((link, secret, rule, filepath))
            
    # Assuming Table, DOUBLE, and console are imported from the rich library.
    general_secret_table = Table(title="General Secret Detected by Gitleaks", box=DOUBLE, show_lines=True)
    general_secret_table.add_column("Link", style="cyan", no_wrap=False, overflow="fold")
    general_secret_table.add_column("Secret", style="green")
    general_secret_table.add_column("Type", style="green")
    general_secret_table.add_column("File", style="green")
    
    if not findings:
        print("No valid findings found.")
    else:
        # Unpack tuple (link, secret, rule, filepath) for each finding.
        for link, secret, rule, file in findings:
            general_secret_table.add_row(link, secret, rule, file)
        console.print(general_secret_table)


def delete_repository(repo_path):
    """
    Delete the specified repository folder.
    """
    try:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            #console.print(f"[yellow]🗑️ Deleted repository: {repo_path}[/yellow]")
        else:
            console.print(f"[red]⚠️ Repository not found: {repo_path}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error deleting repository: {e}[/red]")
def main():
    """
    Main function to handle arguments and run the tool.
    """
    print_tool_banner()
    
    parser = argparse.ArgumentParser(description="GitHub Search Tool with Download and Gitleaks Integration")
    parser.add_argument("keyword", help="Keyword to search on GitHub")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--download", action="store_true", help="Enable manual download option for repositories")
    parser.add_argument("--download-all", action="store_true", help="Download all found repositories automatically")
    parser.add_argument("--gitleaks", action="store_true", help="Run Gitleaks on downloaded repositories")
    parser.add_argument("--destination", default="./downloaded_repos", help="Directory to save downloaded repositories")
    parser.add_argument("--rule-file", required=True, help="Path to the Gitleaks rule file")
    parser.add_argument('--csv', action='store_true', help='Save detected secrets to a CSV file')
    args = parser.parse_args()
    
    results = search_github(args.keyword, args.token)
    display_results(results)
    os.makedirs(args.destination, exist_ok=True)
    
    if args.download_all:
        console.print("[bold cyan]Downloading all repositories...[/bold cyan]")
        for repo in results["repositories"]:
            repo_path = download_repository(repo["html_url"], args.destination, args.token)
            if repo_path and args.gitleaks:
                run_gitleaks(repo_path, args.rule_file)
    elif args.download:
        console.print("[bold yellow]Enter the indices of the repositories to download (e.g., 1,3,5):[/bold yellow]")
        indices = input("Indices: ").strip()
        if indices:
            indices = [int(i.strip()) for i in indices.split(",") if i.strip().isdigit()]
            for idx in indices:
                if 1 <= idx <= len(results["repositories"]):
                    repo_url = results["repositories"][idx - 1]["html_url"]
                    repo_path = download_repository(repo_url, args.destination, args.token)
                    if repo_path and args.gitleaks:
                        run_gitleaks(repo_path, args.rule_file)

    if args.gitleaks and not (args.download or args.download_all):
        console.print("[bold red]Gitleaks requires repositories to be downloaded first. Use --download or --download-all.[/bold red]")

if __name__ == "__main__":
    main()
