---
name: api-gateway-authorizer-security
description: Secure Amazon API Gateway routes when a scanner reports missing authorization, choose Cognito/OIDC JWT or other business authorizers first, and use an always-allow Lambda authorizer only as an explicitly documented fallback for public routes.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# API Gateway Authorizer Security

Review and remediate API Gateway authorization findings without adding security theater merely to make a scanner pass.

## Authorizer Precedence Rule

Apply exactly one effective authorizer policy to each route:

1. If the route requires Cognito, OIDC JWT, IAM, or custom business authorization, use that real authorizer only.
2. If the route is intentionally public and organizational scanning policy requires an authorizer, an always-allow Lambda authorizer may be used only as the documented fallback.
3. Never replace, wrap, or supplement a real business authorizer with the fallback authorizer.

The fallback authorizer is a scanner-compatibility control, not authentication. Its name, documentation, route inventory, and review output must state that it grants public access.

## When to Apply

Use this skill when:

- A scanner flags an API Gateway route with no authorizer
- `cdk-nag` reports `AwsSolutions-APIG4` or a similar authorization finding
- A dedicated fallback Lambda authorizer is needed for intentionally public routes
- Public health, sign-in, OAuth callback, or webhook routes need a defensible exception
- API Gateway authorization is being designed or reviewed

## Workflow

### 1. Inventory Effective Route Authorization

Inspect both infrastructure source and the synthesized CloudFormation template. For every route or method, record:

| Route | Method | Exposure | Configured authorizer | Actual security check | Classification |
|---|---|---|---|---|---|
| `/example` | `GET` | Public internet | JWT, IAM, Lambda, or none | What is validated | Protected or intentionally public |

Do not infer protection from an authorizer attachment alone. Read the authorizer handler and its configuration.

Useful searches:

```bash
rg -n "addRoutes|addMethod|authorizer|authorizationType|isAuthorized|Effect.*Allow" .
npx cdk synth
rg -n "AuthorizationType|AuthorizerId|AuthorizerUri|IdentitySource" cdk.out
```

### 2. Identify and Classify Pass-Through Authorizers

Treat an authorizer as non-authenticating when any path can grant access without validating caller-controlled credentials. Common indicators include:

- Returning `isAuthorized: true` for every request
- Returning an Allow policy before token, signature, claim, or identity validation
- Catching validation errors and allowing the request
- Empty or irrelevant identity sources combined with no request validation
- Accepting unsigned JWTs or decoding claims without verifying the signature
- Validating only that a header exists
- Using an API key or CORS as authentication
- Logging full authorization headers, tokens, or request events

Report these routes as unauthenticated even if the synthesized template references an authorizer. A pass-through authorizer is acceptable only when all of the following are true:

- The route is explicitly classified as intentionally public
- No Cognito, OIDC JWT, IAM, or custom business authorizer is required
- The scanner or organizational policy does not accept an explicit public-route exception
- The fallback is attached only to the named public routes
- Compensating controls and the reason for the fallback are documented

### 3. Classify Each Route

Choose exactly one classification:

1. **Protected** — accesses user, tenant, administrative, or business data; mutates state; triggers paid or privileged operations.
2. **Intentionally public** — must be callable without an established identity, such as a minimal liveness endpoint, an OAuth callback, or a third-party webhook ingress.
3. **Unclear** — do not suppress the finding; ask for the route's trust boundary, caller, and data classification.

Assume a route is protected unless its public requirement is explicit and documented.

### 4. Remediate the Root Cause

For **protected** routes, prefer managed mechanisms in this order when they fit the caller:

- IAM authorization with SigV4 for AWS workloads
- API Gateway JWT or Cognito authorizers for standards-based user or service tokens
- A real Lambda authorizer only for authentication logic unsupported by managed authorizers
- Private API or resource-policy restrictions when network identity is part of the trust boundary

A real Lambda authorizer must deny by default, validate cryptographic credentials and required claims, scope access to the intended route, avoid secret logging, and handle caching without reusing authorization across unrelated routes or tenants.

For **intentionally public** routes:

- Prefer configuring the route as explicitly unauthenticated with a narrow, documented scanner exception
- If policy still requires an authorizer, attach the dedicated always-allow fallback authorizer only to these public routes
- Narrow the route to required methods and paths; avoid public catch-all proxies
- Keep responses and backend permissions minimal
- Add appropriate throttling, request-size/schema validation, access logging, alarms, and edge protections
- Add protocol-specific checks in the integration, such as OAuth `state`/PKCE validation or webhook signature verification
- Suppress only the exact scanner finding on the exact route, with a concrete reason and compensating controls

Never use fallback selection such as `businessAuthorizer ?? fallbackAuthorizer` for protected routes. A missing business authorizer must fail deployment or validation rather than silently making the route public.

See [remediation-patterns.md](./references/remediation-patterns.md) for CDK examples and route-specific controls.

### 5. Validate

Run the repository's normal validation plus the security scanner that raised the finding:

```bash
npm run build
npm test
npx cdk synth
```

Then verify in the synthesized template that:

- Every protected route has the intended authorization type and authorizer reference
- Every public route is narrow and intentionally configured
- Every pass-through authorizer attachment is limited to an explicitly catalogued public route
- No route with Cognito, OIDC JWT, IAM, or custom business authorization also uses the fallback
- Suppressions target only documented public routes
- Scanner output contains no unexplained authorization finding

## Required Review Output

Provide:

1. A route authorization inventory
2. Pass-through authorizer findings with file and line references
3. The protected/public decision for each affected route
4. Implemented or recommended remediation
5. Validation commands and results
6. Any fallback authorizer or narrowly scoped suppression and its justification

## Enforcement Rules

- Never treat the fallback authorizer as authentication or authorization
- Never attach the fallback to a route that requires or already has a business authorizer
- Never silently fall back when a required Cognito, OIDC JWT, IAM, or custom authorizer is missing
- Use the fallback only for explicitly catalogued public routes when scanner exceptions are unavailable
- Never describe API keys, CORS, obscurity, or throttling as authentication
- Never apply stack-wide or rule-wide suppression for a route-specific exception
- Never suppress a protected route's missing authentication
- Never log credentials or complete authorization events
- Never weaken a working authorizer to preserve compatibility without explicit approval
- Verify current AWS and scanner behavior before relying on service-specific capabilities

## References

- [Remediation patterns](./references/remediation-patterns.md)
- [API Gateway access control](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html)
- [API Gateway HTTP API access control](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control.html)
- [CDK Nag rules and suppressions](https://github.com/cdklabs/cdk-nag)
