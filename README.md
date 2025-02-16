# RepoRecon - Advanced GitHub Repository Reconnaissance Tool

## 🚀 Overview

**RepoRecon** is a powerful Python-based command-line tool designed to enhance security professionals' and developers' ability to search, download, and scan GitHub repositories efficiently. The tool seamlessly integrates with **Gitleaks** to detect and validate sensitive information, such as API keys, tokens, and credentials, ensuring your workflow remains secure and streamlined.

## ✨ Features

- 🔍 **Search GitHub Repositories** – Utilize the GitHub API to find repositories based on a keyword.
- 📥 **Download Repositories** – Selectively or automatically download repositories directly from search results.
- 🔒 **Secrets Scanning** – Perform automated scans using **Gitleaks** to uncover sensitive data.
- ✅ **Credential Validation** – Verify AWS keys, Azure credentials, GitHub tokens, Slack tokens, and more.
- 🎛️ **Flexible Operation Modes** – Choose between interactive and automated execution.
- 📜 **Custom Gitleaks Rules** – Enhance scanning with custom `rules.toml` configurations.

## ⚙️ Requirements

- 🐍 **Python 3.8 or higher**
- 🔍 **Gitleaks** installed on your system ([Installation Guide](https://github.com/zricethezav/gitleaks))
- 🔍 **Git** installed on your system ([Installation Guide](https://git-scm.com/downloads))

## 📦 Installation

### Install via PyPI:
```bash
pip install RepoRecon
```

### Install from Source:
```bash
# Step 1: Clone the Repository
git clone <repository_url>
cd RepoRecon

# Step 2: Install Dependencies
pip install -r requirements.txt

# Step 3: Install the Tool
python setup.py install
```
The installation process ensures that **Gitleaks** is installed if not already present.

## 🚀 Usage

### Basic Syntax:
```bash
RepoRecon <keyword> --token <github_token>
```
- `<keyword>`: The term to search for on GitHub.
- `<github_token>`: Your GitHub personal access token.

### Command-Line Options:

| Option | Description |
|--------|-------------|
| 📥 `--download` | Enables manual selection and downloading of repositories. |
| 📂 `--download-all` | Automatically downloads all repositories matching the keyword. |
| 🔍 `--gitleaks` | Scans downloaded repositories for secrets using **Gitleaks**. |
| 📁 `--destination <path>` | Specifies a directory to store downloaded repositories (default: `./downloaded_repos`). |
| 📜 `--rule-file <path>` | Defines a custom **Gitleaks** rule file for enhanced scanning. |

## 🔄 Example Workflows

### 1️⃣ Search and Display Results
```bash
RepoRecon "tesla" --token <your_github_token>
```
Displays a list of repositories related to the keyword **"tesla"**.

### 2️⃣ Download All Matching Repositories
```bash
RepoRecon "tesla" --token <your_github_token> --download-all
```
Automatically downloads all repositories that match the search criteria.

### 3️⃣ Scan Repositories with Gitleaks
```bash
RepoRecon "tesla" --token <your_github_token> --download-all --gitleaks
```
This command downloads and scans all matching repositories for secrets.

## 🔐 Supported Credential Validations

RepoRecon validates the following sensitive credentials:

- 🔑 AWS Credentials
- 🔑 Azure Credentials
- 🔑 Slack Tokens
- 🔑 Stripe API Keys
- 🔑 GitHub Personal Access Tokens
- 🔑 Heroku API Keys
- 🔑 Dropbox API Keys
- 🔑 Twilio API Keys

## 📜 Custom Gitleaks Rules

Enhance detection capabilities using a custom `rules.toml` file, allowing additional secret-detection patterns.

### Example: Running Gitleaks with Custom Rules
```bash
githubsearchtool "security" --token <your_github_token> --download-all --gitleaks --rule-file /path/to/rules.toml
```
Ensure the `rules.toml` file is correctly configured to match your detection requirements.

## 📌 Dependencies

The following Python packages are required (listed in `requirements.txt`):

- `boto3`
- `requests`
- `rich`
- `pyfiglet`
- `stripe`

## 📢 Notes

- Ensure **Gitleaks** and **git** are installed and accessible in your system's `PATH`.
- Use a **GitHub personal access token** with appropriate permissions to access the GitHub API.
- Make Sure that you are using the **rules.toml" file

## 🤝 Contributing

We welcome contributions! If you have enhancements or bug fixes, fork the repository and submit a pull request.

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## 🙏 Acknowledgments

Special thanks to the creators of **Gitleaks** and all open-source contributors who help improve security research tools like **RepoRecon**.
