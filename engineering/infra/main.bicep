@description('Deployment prefix')
param namePrefix string
@description('Existing container image reachable by Container Apps; configure registry access before deployment.')
param containerImage string
@description('Region for infrastructure')
param location string = resourceGroup().location
@description('Microsoft Entra tenant ID')
param entraTenantId string
@description('API registered audience identifier')
param entraApiAudience string
@description('Azure OpenAI endpoint')
param azureOpenAiEndpoint string
@description('Chat model deployment name')
param chatDeployment string
@description('Embedding model deployment name')
param embeddingDeployment string
@description('Azure AI Search endpoint')
param searchEndpoint string
@description('Durable PostgreSQL database URL (supply via a trusted deployment secret source)')
@secure()
param databaseUrl string

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${namePrefix}-logs'
  location: location
  properties: {
    sku: {name: 'PerGB2018'}
    retentionInDays: 30
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${namePrefix}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${namePrefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
  }
}

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-api'
  location: location
  identity: {type: 'SystemAssigned'}
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      secrets: [{name: 'postgres-url', value: databaseUrl}]
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [{
        name: 'enterprise-api'
        image: containerImage
        resources: {cpu: json('0.5'), memory: '1Gi'}
        env: [
          {name: 'ENVIRONMENT', value: 'production'}
          {name: 'RUN_SCHEMA_CREATE', value: 'false'}
          {name: 'DATABASE_URL', secretRef: 'postgres-url'}
          {name: 'ENTRA_TENANT_ID', value: entraTenantId}
          {name: 'ENTRA_API_AUDIENCE', value: entraApiAudience}
          {name: 'AZURE_OPENAI_ENDPOINT', value: azureOpenAiEndpoint}
          {name: 'AZURE_OPENAI_CHAT_DEPLOYMENT', value: chatDeployment}
          {name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT', value: embeddingDeployment}
          {name: 'AZURE_SEARCH_ENDPOINT', value: searchEndpoint}
          {name: 'ENABLE_METRICS_ENDPOINT', value: 'false'}
          {name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: insights.properties.ConnectionString}
        ]
        probes: [{
          type: 'Liveness'
          httpGet: {path: '/health/live',port: 8080}
          initialDelaySeconds: 15
          periodSeconds: 20
        }]
      }]
      scale: {minReplicas: 1,maxReplicas: 3}
    }
  }
}

output apiUrl string = 'https://${api.properties.configuration.ingress.fqdn}'
output identityPrincipalId string = api.identity.principalId
