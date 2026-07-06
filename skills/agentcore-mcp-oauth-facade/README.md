# AgentCore MCP OAuth Facade Skill

Production-tested patterns for putting a stateless OAuth + MCP protocol
facade in front of Bedrock AgentCore Gateway/Runtime, so strict MCP clients
(Claude Code, Cursor, Amazon Quick, mcp-remote) can connect: OAuth discovery
and fake DCR over Cognito, dual session-id handling, tools/list pagination
aggregation, tool-name prefix rewriting, and Gateway schema limits.

## Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill agentcore-mcp-oauth-facade
```

See [SKILL.md](./SKILL.md) for the architecture and adoption checklist. The
`references/` directory contains deep dives on OAuth discovery/DCR, MCP
session bridging, and Gateway pagination/schema constraints.
