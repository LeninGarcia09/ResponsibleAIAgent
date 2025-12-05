# 🚀 Complete Deployment Guide

## Overview

This guide covers deploying the Responsible AI Agent to Azure, from infrastructure provisioning to application deployment.

## Prerequisites

### Required Tools
- ✅ **Azure CLI** - [Install](https://docs.microsoft.com/cli/azure/install-azure-cli)
- ✅ **Terraform** - [Install](https://www.terraform.io/downloads)
- ✅ **Node.js 18+** - [Install](https://nodejs.org/)
- ✅ **Python 3.11+** - [Install](https://www.python.org/)
- ✅ **Azure Functions Core Tools** - `npm install -g azure-functions-core-tools@4`

### Azure Requirements
- **Azure Subscription** with Contributor access
- **Azure OpenAI Access** - [Apply here](https://aka.ms/oai/access)
- **Entra ID** (formerly Azure AD) for authentication

## Deployment Options

### Option 1: Automated Deployment (Recommended)

```powershell
# Deploy everything to dev environment
.\deploy.ps1 -Environment dev

# Deploy to production
.\deploy.ps1 -Environment prod

# Deploy only infrastructure
.\deploy.ps1 -SkipBackend -SkipFrontend

# Deploy only backend
.\deploy.ps1 -SkipInfrastructure -SkipFrontend

# Deploy only frontend
.\deploy.ps1 -SkipInfrastructure -SkipBackend
```

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Login to Azure
```powershell
az login
az account set --subscription "Your-Subscription-Name"
az account show
```

#### Step 2: Deploy Infrastructure
```powershell
cd infrastructure\terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="environment=dev" -out=tfplan

# Apply
terraform apply tfplan

# Save outputs
terraform output > outputs.txt
```

#### Step 3: Configure Azure OpenAI
```powershell
# Get resource group and OpenAI name from Terraform outputs
$rgName = terraform output -raw resource_group_name
$openaiName = terraform output -raw openai_endpoint | Split-Path -Leaf | Split-Path -Parent

# Create GPT-4 deployment
az cognitiveservices account deployment create `
  --resource-group $rgName `
  --name $openaiName `
  --deployment-name gpt-4 `
  --model-name gpt-4 `
  --model-version "0613" `
  --model-format OpenAI `
  --sku-name "Standard" `
  --sku-capacity 10
```

#### Step 4: Deploy Backend
```powershell
cd ..\..\backend

# Install dependencies
pip install -r requirements.txt

# Get Function App name
cd ..\infrastructure\terraform
$funcAppName = terraform output -raw function_app_name
cd ..\..\backend

# Deploy
func azure functionapp publish $funcAppName --python
```

#### Step 5: Deploy Frontend
```powershell
cd ..\frontend

# Install dependencies
npm install

# Build
npm run build

# Get app name
cd ..\infrastructure\terraform
$frontendName = terraform output -raw frontend_app_name
$rgName = terraform output -raw resource_group_name
cd ..\..\frontend

# Package and deploy
Compress-Archive -Path .next\* -DestinationPath deploy.zip -Force
az webapp deployment source config-zip `
  --resource-group $rgName `
  --name $frontendName `
  --src deploy.zip
```

## Post-Deployment Configuration

### 1. Verify Deployment

```powershell
# Check Function App
az functionapp show --name $funcAppName --resource-group $rgName --query "state"

# Check Web App
az webapp show --name $frontendName --resource-group $rgName --query "state"

# Test API endpoint
$funcUrl = "https://$funcAppName.azurewebsites.net/api/submit-review"
Invoke-WebRequest -Uri $funcUrl -Method GET
```

### 2. Configure Application Settings

```powershell
# Update Function App settings
az functionapp config appsettings set `
  --name $funcAppName `
  --resource-group $rgName `
  --settings `
    "EMAIL_FROM=noreply@yourdomain.com" `
    "ENABLE_EMAIL_NOTIFICATIONS=true"

# Update Frontend settings
az webapp config appsettings set `
  --name $frontendName `
  --resource-group $rgName `
  --settings `
    "NEXT_PUBLIC_API_BASE_URL=https://$funcAppName.azurewebsites.net/api"
```

### 3. Set Up Microsoft Graph API (Optional for Email)

```powershell
# Create app registration
$appName = "ResponsibleAI-EmailSender"
$app = az ad app create --display-name $appName | ConvertFrom-Json

# Add Microsoft Graph permissions
az ad app permission add `
  --id $app.appId `
  --api 00000003-0000-0000-c000-000000000000 `
  --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Role

# Create client secret
$secret = az ad app credential reset --id $app.appId --append | ConvertFrom-Json

# Update Function App with Graph API settings
az functionapp config appsettings set `
  --name $funcAppName `
  --resource-group $rgName `
  --settings `
    "GRAPH_API_CLIENT_ID=$($app.appId)" `
    "GRAPH_API_TENANT_ID=$($secret.tenant)" `
    "GRAPH_API_CLIENT_SECRET=$($secret.password)"
```

### 4. Configure Custom Domain (Optional)

```powershell
# Add custom domain to Function App
az functionapp config hostname add `
  --webapp-name $funcAppName `
  --resource-group $rgName `
  --hostname api.yourdomain.com

# Add custom domain to Web App
az webapp config hostname add `
  --webapp-name $frontendName `
  --resource-group $rgName `
  --hostname app.yourdomain.com

# Enable HTTPS
az webapp update `
  --name $frontendName `
  --resource-group $rgName `
  --https-only true
```

## Monitoring and Maintenance

### View Logs

```powershell
# Function App logs (live tail)
az webapp log tail --name $funcAppName --resource-group $rgName

# Frontend logs
az webapp log tail --name $frontendName --resource-group $rgName

# View in Application Insights
az monitor app-insights query `
  --app $(terraform output -raw application_insights_name) `
  --analytics-query "requests | top 10 by timestamp desc"
```

### Set Up Alerts

```powershell
# Create action group for notifications
az monitor action-group create `
  --name "ResponsibleAI-Alerts" `
  --resource-group $rgName `
  --short-name "RAI-Alert" `
  --email-receiver "admin@yourdomain.com"

# Create alert for failed requests
az monitor metrics alert create `
  --name "High-Error-Rate" `
  --resource-group $rgName `
  --scopes "/subscriptions/.../functionApps/$funcAppName" `
  --condition "count failedRequests > 10" `
  --description "Alert when error rate is high" `
  --action "ResponsibleAI-Alerts"
```

### Scale Resources

```powershell
# Scale Function App (if using non-consumption plan)
az functionapp plan update `
  --name asp-responsibleai-dev `
  --resource-group $rgName `
  --sku B2 `
  --number-of-workers 2

# Scale Frontend
az webapp scale `
  --name $frontendName `
  --resource-group $rgName `
  --instance-count 2
```

## Troubleshooting

### Common Issues

#### 1. "Azure OpenAI is not available in this region"
**Solution:** Change the region in `variables.tf` to one where Azure OpenAI is available:
- East US
- South Central US
- West Europe

#### 2. "Name already taken" for Storage/Key Vault
**Solution:** These names must be globally unique. Update `project_name` in variables.

#### 3. Function App deployment fails
**Solution:** 
```powershell
# Check logs
az webapp log download --name $funcAppName --resource-group $rgName --log-file logs.zip

# Restart the app
az functionapp restart --name $funcAppName --resource-group $rgName
```

#### 4. Frontend shows API connection error
**Solution:** Update CORS settings on Function App:
```powershell
az functionapp cors add `
  --name $funcAppName `
  --resource-group $rgName `
  --allowed-origins "https://$frontendName.azurewebsites.net"
```

### Debug Commands

```powershell
# Check Function App configuration
az functionapp config appsettings list `
  --name $funcAppName `
  --resource-group $rgName

# Test Cosmos DB connection
az cosmosdb check-name-exists --name cosmos-responsibleai-dev

# Verify Key Vault secrets
az keyvault secret list --vault-name kv-responsibleai-dev

# Check deployment history
az deployment group list --resource-group $rgName
```

## Rollback

### Rollback Deployment

```powershell
# Rollback to previous deployment
az functionapp deployment slot swap `
  --name $funcAppName `
  --resource-group $rgName `
  --slot staging

# Or redeploy previous version
git checkout <previous-commit>
.\deploy.ps1 -Environment dev
```

### Rollback Infrastructure

```powershell
cd infrastructure\terraform

# Import existing state
terraform import azurerm_resource_group.main /subscriptions/.../resourceGroups/...

# Revert to previous configuration
git checkout HEAD~1 main.tf

# Apply
terraform apply -var="environment=dev"
```

## Cleanup

### Remove Everything

```powershell
cd infrastructure\terraform
terraform destroy -var="environment=dev" -auto-approve
```

### Selective Cleanup

```powershell
# Remove only frontend
terraform destroy -target=azurerm_linux_web_app.frontend

# Remove only backend
terraform destroy -target=azurerm_linux_function_app.main
```

## Cost Optimization

### Estimated Monthly Costs (Dev Environment)
- **Azure Functions** (Consumption): $0-20/month
- **Cosmos DB** (Serverless): $1-50/month
- **Storage Account**: $1-10/month
- **Azure OpenAI** (Pay-as-you-go): $10-100/month
- **App Service** (B1): ~$13/month
- **Application Insights**: $0-5/month

**Total: ~$25-200/month** depending on usage

### Cost-Saving Tips
1. Use Consumption plan for Functions (scales to zero)
2. Use Serverless Cosmos DB for variable workloads
3. Set up auto-shutdown for non-prod environments
4. Enable diagnostic logs only when needed
5. Review costs weekly: [Azure Cost Management](https://portal.azure.com/#blade/Microsoft_Azure_CostManagement)

## Security Checklist

- [ ] Enable Azure AD authentication
- [ ] Configure managed identities for all services
- [ ] Restrict network access with firewall rules
- [ ] Enable Azure Key Vault for all secrets
- [ ] Set up Azure Policy for compliance
- [ ] Enable diagnostic logging
- [ ] Configure backup for Cosmos DB
- [ ] Review IAM permissions regularly
- [ ] Enable Azure Defender for Cloud
- [ ] Set up Azure Monitor alerts

## Next Steps

1. ✅ **Test the deployment** - Visit your frontend URL
2. 🔐 **Set up authentication** - Configure Entra ID
3. 📧 **Configure emails** - Set up Microsoft Graph API
4. 📊 **Add monitoring** - Configure Application Insights dashboards
5. 🚀 **Go live** - Deploy to production environment

---

For more help:
- **Azure Documentation**: https://docs.microsoft.com/azure
- **Terraform Azure Provider**: https://registry.terraform.io/providers/hashicorp/azurerm
- **Project README**: [README.md](../README.md)
