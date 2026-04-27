# Claude Code GitLab MCP Server Setup

## Overview

The GitLab MCP (Model Context Protocol) server enables AI assistants to interact with GitLab repositories, issues, merge requests, and other GitLab resources through a standardized interface. This guide works for both gitlab.com and self-hosted/enterprise GitLab instances — replace `gitlab.example.com` in the examples below with your own GitLab hostname.

## Prerequisites

- Node.js 20+
- GitLab instance access (e.g., https://gitlab.example.com/ or https://gitlab.com/)
- GitLab Personal Access Token with appropriate permissions
- Auth cookie file (only if your enterprise GitLab enforces SSO/cookie auth in addition to the PAT)

## Installation

### 1. GitLab Personal Access Token Setup

1. Go to GitLab → User Settings → Access Tokens: `https://<your-gitlab-host>/-/user_settings/personal_access_tokens`
2. Create new token with required scopes
3. Copy the token (you won't see it again)

**Required scopes:**
- `api` — Full API access
- `read_user` — Read user information
- `read_repository` — Read repository content
- `write_repository` — Write repository content (for file operations)

### 2. Auth Cookie (enterprise GitLab only)

Some enterprise GitLab deployments sit behind SSO and require a browser auth cookie in addition to the
personal access token. If that is the case, export the cookie from your authenticated browser session
(or use your org's SSO tooling) and save it to a local file — for example `~/.gitlab/cookie`.

If your GitLab instance only requires a PAT, you can skip this step and omit `GITLAB_AUTH_COOKIE_PATH`
from the config below.

### 3. MCP Client Configuration

Add to `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "GitLab": {
      "command": "npx",
      "args": ["-y", "@zereight/mcp-gitlab"],
      "env": {
        "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_PERSONAL_ACCESS_TOKEN}",
        "GITLAB_API_URL": "https://gitlab.example.com/api/v4",
        "GITLAB_READ_ONLY_MODE": "false",
        "USE_GITLAB_WIKI": "false",
        "USE_MILESTONE": "false",
        "USE_PIPELINE": "false",
        "GITLAB_AUTH_COOKIE_PATH": "~/.gitlab/cookie"
      }
    }
  }
}
```

**Tips:**
- Do not commit TOKEN information to the repository — use environment variables
- Save `GITLAB_PERSONAL_ACCESS_TOKEN` as an env var (e.g., in `~/.bashrc` or `~/.zshrc`)
- Set `USE_GITLAB_WIKI` to `"true"` if wiki operations are needed
- Replace `gitlab.example.com` with your GitLab hostname (or `gitlab.com` for the SaaS instance)

### 4. Verify

```bash
$ claude mcp list
Checking MCP server health...
GitLab: npx -y @zereight/mcp-gitlab - ✓ Connected
```

## Available GitLab MCP Tools

Provides operations for:
- Repository Management
- File Operations
- Branch Management
- Issues Management
- Merge Request Operations
- Code Review Operations

Full list: https://github.com/zereight/gitlab-mcp?tab=readme-ov-file#tools-%EF%B8%8F

## SSH Config for Wiki Repo Push

Wiki push uses git over SSH (not MCP). Configure `~/.ssh/config` with your GitLab SSH host and key:

```
Host ssh.gitlab.example.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

If your enterprise GitLab uses short-lived SSH certificates, add `CertificateFile` as well and refresh
the certificate with your org's tooling whenever it expires.
