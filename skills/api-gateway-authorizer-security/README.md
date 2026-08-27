# API Gateway Authorizer Security

An agent skill for reviewing and remediating Amazon API Gateway authorization findings while keeping real business authorizers separate from an explicitly documented public-route fallback.

Use it to:

- Limit always-allow Lambda authorizers to explicitly public fallback routes
- Choose managed JWT, Cognito, IAM, or real custom authorization for protected routes
- Prevent the fallback from replacing or supplementing a business authorizer
- Secure intentionally public health, OAuth callback, and webhook routes
- Add narrow, justified scanner suppressions with compensating controls

## Install

```bash
npx skills add aws-samples/sample-agent-skills-for-builders --skill api-gateway-authorizer-security
```

## Example Prompts

```text
Review this API Gateway for pass-through Lambda authorizers.
Use the fallback authorizer only on public routes without business authorization.
Document a safe exception for this public OAuth callback route.
```

See [SKILL.md](./SKILL.md) for the complete workflow.
