using './main.bicep'

param appName = 'retailreplenishment'
param environmentName = 'dev'
param backendImage = 'REPLACE_WITH_REGISTRY/retail-replenishment-api:REPLACE_WITH_TAG'
param authIssuer = 'https://login.microsoftonline.com/REPLACE_WITH_TENANT/v2.0'
param authAudience = 'REPLACE_WITH_API_APPLICATION_ID'
param authJwksUrl = 'https://login.microsoftonline.com/REPLACE_WITH_TENANT/discovery/v2.0/keys'
// Replace before deployment; use Key Vault or a deployment secret in CI.
param sqlAdminPassword = 'REPLACE_WITH_SECRET_FROM_KEY_VAULT'
param databaseUrl = 'REPLACE_WITH_DATABASE_URL_FROM_SECRET_STORE'
param redisUrl = 'REPLACE_WITH_REDIS_URL_FROM_SECRET_STORE'
param serviceBusConnectionString = 'REPLACE_WITH_SERVICE_BUS_CONNECTION_STRING_FROM_SECRET_STORE'
