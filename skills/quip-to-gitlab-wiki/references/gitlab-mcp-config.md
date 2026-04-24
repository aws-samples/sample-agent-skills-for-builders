# Claude Code GitLab MCP Server Setup

## Overview

The GitLab MCP (Model Context Protocol) server enables AI assistants to interact with GitLab repositories, issues, merge requests, and other GitLab resources through a standardized interface. This guide covers enterprise-level setup for teams using AWS GitLab (`gitlab.aws.dev`).

## Prerequisites

- Node.js 20+
- GitLab instance access (https://gitlab.aws.dev/)
- GitLab Personal Access Token with appropriate permissions
- Midway cookie

## Installation

### 1. GitLab Personal Access Token Setup

1. Go to GitLab → User Settings → Access Tokens: https://gitlab.aws.dev/-/user_settings/personal_access_tokens
2. Create new token with required scopes
3. Copy the token (you won't see it again)

**Required scopes:**
- `api` — Full API access
- `read_user` — Read user information
- `read_repository` — Read repository content
- `write_repository` — Write repository content (for file operations)

### 2. Midway Cookie

After Midway successfully logs in, it saves cookies to: `~/.midway/cookie`

**Note:** Enterprise GitLab requires both AUTH COOKIE and PERSONAL ACCESS TOKEN to authenticate.

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
        "GITLAB_API_URL": "https://gitlab.aws.dev/api/v4",
        "GITLAB_READ_ONLY_MODE": "false",
        "USE_GITLAB_WIKI": "false",
        "USE_MILESTONE": "false",
        "USE_PIPELINE": "false",
        "GITLAB_AUTH_COOKIE_PATH": "~/.midway/cookie"
      }
    }
  }
}
```

**Tips:**
- Do not commit TOKEN information to the repository — use environment variables
- Save `GITLAB_PERSONAL_ACCESS_TOKEN` as an env var (e.g., in `~/.bashrc` or `~/.zshrc`)
- Set `USE_GITLAB_WIKI` to `"true"` if wiki operations are needed

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

Wiki push uses git over SSH (not MCP). Configure `~/.ssh/config`:

```
Host ssh.gitlab.aws.dev
    User git
    IdentityFile ~/.ssh/aws_id_ecdsa
    CertificateFile ~/.ssh/aws_id_ecdsa-cert.pub
    IdentitiesOnly yes
```

Certificate must be valid — check with `ssh-keygen -L -f ~/.ssh/aws_id_ecdsa-cert.pub`. Refresh with `mwinit` if expired.
