# API Gateway Authorization Remediation Patterns

Use these patterns after classifying each route as protected or intentionally public. Adapt names and commands to the repository.

## Protected HTTP API Route with JWT Authorization

Prefer API Gateway's managed JWT authorizer when the caller presents standards-based JWTs.

```typescript
import { HttpMethod } from 'aws-cdk-lib/aws-apigatewayv2';
import { HttpJwtAuthorizer } from 'aws-cdk-lib/aws-apigatewayv2-authorizers';

const authorizer = new HttpJwtAuthorizer(
  'UserJwtAuthorizer',
  issuerUrl,
  { jwtAudience: [audience] },
);

httpApi.addRoutes({
  path: '/api/orders/{proxy+}',
  methods: [HttpMethod.ANY],
  integration: ordersIntegration,
  authorizer,
});
```

Verify issuer, audience, token lifetime, and application-level tenant or permission checks. Authentication does not replace authorization inside the application.

## Protected Route with IAM Authorization

Use IAM for AWS workload callers that can sign requests with SigV4.

```typescript
import { AuthorizationType, LambdaIntegration } from 'aws-cdk-lib/aws-apigateway';

orders.addMethod('POST', new LambdaIntegration(handler), {
  authorizationType: AuthorizationType.IAM,
});
```

Grant `execute-api:Invoke` only to the required principals and route ARNs.

## Real Lambda Authorizer Requirements

Use a Lambda authorizer only when managed JWT, Cognito, or IAM authorization cannot express the required protocol. Its implementation must:

1. Extract credentials from declared identity sources
2. Verify a signature or another cryptographic proof
3. Validate issuer, audience, expiry, and route-specific claims where applicable
4. Deny malformed, missing, expired, or unverifiable credentials
5. Fail closed on dependency and parsing errors
6. Return access scoped to the intended route and principal
7. Avoid logging raw credentials and sensitive claims
8. Include every security-relevant value in the cache key, or disable caching deliberately

Prefer a native JWT authorizer over recreating JWT verification in Lambda.

## Intentionally Public HTTP API Route

Omitting the authorizer is correct when the route is intentionally public and the exception is documented.

```typescript
import { HttpMethod } from 'aws-cdk-lib/aws-apigatewayv2';

httpApi.addRoutes({
  path: '/health',
  methods: [HttpMethod.GET],
  integration: healthIntegration,
});
```

Prefer this explicit public configuration when the scanner and organizational policy support a narrow exception.

## Always-Allow Fallback Authorizer

Use this compatibility pattern only for routes already classified as intentionally public and only when scanning policy requires every route to reference an authorizer. Never attach it to a route requiring Cognito, OIDC JWT, IAM, or custom business authorization.

```typescript
import type {
  APIGatewayRequestAuthorizerEventV2,
  APIGatewaySimpleAuthorizerResult,
} from 'aws-lambda';

export async function handler(
  _event: APIGatewayRequestAuthorizerEventV2,
): Promise<APIGatewaySimpleAuthorizerResult> {
  return {
    isAuthorized: true,
    context: { authorizationMode: 'public-route-fallback' },
  };
}
```

Do not log the event because it can contain credentials supplied accidentally by callers.

Attach the dedicated fallback only through an explicit public-route definition:

```typescript
import { Duration } from 'aws-cdk-lib';
import { HttpMethod } from 'aws-cdk-lib/aws-apigatewayv2';
import {
  HttpLambdaAuthorizer,
  HttpLambdaResponseType,
} from 'aws-cdk-lib/aws-apigatewayv2-authorizers';

const publicRouteFallbackAuthorizer = new HttpLambdaAuthorizer(
  'PublicRouteFallbackAuthorizer',
  fallbackHandler,
  {
    identitySource: [],
    responseTypes: [HttpLambdaResponseType.SIMPLE],
    resultsCacheTtl: Duration.seconds(0),
  },
);

httpApi.addRoutes({
  path: '/health',
  methods: [HttpMethod.GET],
  integration: healthIntegration,
  authorizer: publicRouteFallbackAuthorizer,
});
```

Do not implement a generic `businessAuthorizer ?? publicRouteFallbackAuthorizer` expression. That pattern can turn a protected route public when its required authorizer is accidentally missing. Define protected and public routes separately and test their synthesized authorization types.

## Narrow CDK Nag Suppression for a Public REST Method

Suppress a finding only after documenting why the method must be public and which controls reduce its risk.

```typescript
import {
  AuthorizationType,
  LambdaIntegration,
} from 'aws-cdk-lib/aws-apigateway';
import { NagSuppressions } from 'cdk-nag';

const method = healthResource.addMethod(
  'GET',
  new LambdaIntegration(healthHandler),
  { authorizationType: AuthorizationType.NONE },
);

NagSuppressions.addResourceSuppressions(method, [
  {
    id: 'AwsSolutions-APIG4',
    reason:
      'Public liveness endpoint returns no sensitive data; GET-only routing, throttling, access logging, and alarms limit abuse.',
  },
]);
```

Use the rule ID emitted by the project's scanner. Confirm the suppression applies only to the generated method resource. Do not suppress the rule on the whole API or stack.

## Controls by Public Route Type

### Health and Liveness

- Return only status required by the load balancer or monitor
- Avoid dependency details, versions, stack traces, and configuration data
- Use `GET` only and a dedicated least-privilege integration
- Apply throttling, access logs, error alarms, and edge protections appropriate to exposure

### OAuth Start and Callback

- Generate unpredictable, short-lived, single-use `state`
- Bind `state` to the initiating browser session and intended redirect
- Require PKCE where the OAuth flow supports it
- Validate the provider, redirect URI, authorization code, and callback errors
- Never treat the callback's public reachability as proof of user identity

### Webhooks

- Verify the provider's signature exactly as documented, including timestamp and replay protection
- Validate the signature against the unmodified request bytes when required
- Reject old, duplicate, malformed, or unsigned events
- Restrict event types and payload size
- Acknowledge quickly and process asynchronously when possible

### Public Read-Only APIs

- Confirm the data is intentionally public and contains no tenant-specific fields
- Use explicit resources and methods instead of a catch-all proxy
- Apply caching, quotas or throttling, request validation, and abuse monitoring as appropriate

## Scanner Exception Checklist

Every exception should identify:

- The exact route and method
- The business or protocol reason authentication cannot be required
- The data returned and operations performed
- The compensating controls
- The scanner rule and smallest suppressible resource
- The owner and review condition for removing the exception

If any item is unknown, leave the finding open.

## Authorizer Selection Checklist

For every route, evaluate in this order:

1. Does it require Cognito or OIDC JWT authorization? Attach the JWT authorizer only.
2. Does it require IAM or custom business authorization? Attach that authorizer only.
3. Is it explicitly public? Prefer no authorizer plus a narrow scanner exception.
4. Is an authorizer still mandatory under scanning policy? Attach the public-route fallback and document that it always allows.
5. Is the classification unclear? Do not attach the fallback.
