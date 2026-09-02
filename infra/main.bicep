targetScope = 'resourceGroup'

@description('Azure region for all regional resources.')
param location string = resourceGroup().location

@description('Short, globally unique application name. Use lowercase letters and numbers.')
@minLength(3)
@maxLength(20)
param appName string

@description('Deployment environment name.')
@allowed([
  'dev'
  'test'
  'prod'
])
param environmentName string = 'dev'

@description('Container image for the backend API, including tag or digest.')
param backendImage string

@description('Validated OIDC issuer URL for backend JWT authentication.')
param authIssuer string

@description('OIDC audience expected by the backend API.')
param authAudience string

@description('OIDC JWKS URL used to validate backend JWT signatures.')
param authJwksUrl string

@description('Monthly cost-management budget in USD.')
param monthlyBudgetUsd int = 15000

@secure()
@description('Initial administrator password for Azure SQL.')
param sqlAdminPassword string

@secure()
@description('Application database connection URL. Store and supply from a secret manager.')
param databaseUrl string

@secure()
@description('Application Redis connection URL. Store and supply from a secret manager.')
param redisUrl string

@secure()
@description('Azure Service Bus connection string. Store and supply from a secret manager.')
param serviceBusConnectionString string

var resourcePrefix = '${appName}-${environmentName}'
var logWorkspaceName = '${resourcePrefix}-logs'
var sqlServerName = '${resourcePrefix}-sql'
var sqlDatabaseName = '${resourcePrefix}-db'
var redisName = '${resourcePrefix}-cache'
var serviceBusName = '${resourcePrefix}-bus'
var containerAppsEnvironmentName = '${resourcePrefix}-aca'
var staticWebAppName = '${resourcePrefix}-web'
var costCeilingLabel = string(monthlyBudgetUsd)

resource logWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: environmentName == 'prod' ? 30 : 7
  }
  tags: {
    environment: environmentName
    monthlyCostCeilingUsd: costCeilingLabel
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${resourcePrefix}-appi'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logWorkspace.id
  }
}

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: 'retailadmin'
    administratorLoginPassword: sqlAdminPassword
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: environmentName == 'prod' ? 'GP_Gen5_2' : 'Basic'
    tier: environmentName == 'prod' ? 'GeneralPurpose' : 'Basic'
  }
  properties: {
    zoneRedundant: environmentName == 'prod'
  }
}

resource redis 'Microsoft.Cache/Redis@2023-04-01' = {
  name: redisName
  location: location
  properties: {
    sku: {
      name: environmentName == 'prod' ? 'Premium' : 'Basic'
      family: environmentName == 'prod' ? 'P' : 'C'
      capacity: environmentName == 'prod' ? 1 : 0
    }
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
    }
  }
  zones: environmentName == 'prod' ? [
    '1'
    '2'
    '3'
  ] : null
}

resource serviceBus 'Microsoft.ServiceBus/namespaces@2024-01-01' = {
  name: serviceBusName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    publicNetworkAccess: 'Disabled'
    minimumTlsVersion: '1.2'
  }
}

resource eventQueue 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = {
  parent: serviceBus
  name: 'inventory-events'
  properties: {
    maxDeliveryCount: 10
    deadLetteringOnMessageExpiration: true
    requiresDuplicateDetection: true
    duplicateDetectionHistoryTimeWindow: 'PT10M'
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logWorkspace.properties.customerId
        sharedKey: logWorkspace.listKeys().primarySharedKey
      }
    }
    zoneRedundant: environmentName == 'prod'
  }
}

resource backendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${resourcePrefix}-api'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'sql-admin-password'
          value: sqlAdminPassword
        }
          {
            name: 'database-url'
            value: databaseUrl
          }
          {
            name: 'redis-url'
            value: redisUrl
          }
          {
            name: 'service-bus-connection-string'
            value: serviceBusConnectionString
          }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: backendImage
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/healthz'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/readyz'
                port: 8000
              }
              initialDelaySeconds: 15
              periodSeconds: 15
            }
          ]
          env: [
            {
              name: 'APP_ENVIRONMENT'
              value: environmentName
            }
            {
              name: 'APP_AUTH_ISSUER'
              value: authIssuer
            }
            {
              name: 'APP_AUTH_AUDIENCE'
              value: authAudience
            }
            {
              name: 'APP_AUTH_JWKS_URL'
              value: authJwksUrl
            }
            {
              name: 'APP_SERVICE_BUS_QUEUE_NAME'
              value: eventQueue.name
            }
            {
              name: 'APP_DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'APP_REDIS_URL'
              secretRef: 'redis-url'
            }
            {
              name: 'APP_SERVICE_BUS_CONNECTION_STRING'
              secretRef: 'service-bus-connection-string'
            }
          ]
          resources: {
            cpu: 1
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: environmentName == 'prod' ? 2 : 1
        maxReplicas: environmentName == 'prod' ? 10 : 2
      }
    }
  }
}

resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: environmentName == 'prod' ? 'Standard' : 'Free'
    tier: environmentName == 'prod' ? 'Standard' : 'Free'
  }
  properties: {}
}

