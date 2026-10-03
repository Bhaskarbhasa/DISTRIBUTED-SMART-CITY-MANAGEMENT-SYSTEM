# Security Model

## JWT Implementation
Stateless authentication using JWTs. Tokens contain user roles and expire in 15 minutes.

## RBAC
Roles include: Admin, Operator, Viewer, Device.

## Device Authentication
Devices authenticate using pre-shared keys or X.509 certificates to get a token.

## Zero Trust
Every microservice validates the incoming JWT, even if the request came from the internal API Gateway.
