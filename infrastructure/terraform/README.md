# Terraform Deployment Guide

## Prerequisites

1. **Install Terraform**
   - Download from: https://www.terraform.io/downloads
   - Verify: `terraform version`

2. **Install Azure CLI**
   - Download from: https://docs.microsoft.com/cli/azure/install-azure-cli
   - Verify: `az --version`

3. **Login to Azure**
   ```bash
   az login
   az account set --subscription "Your-Subscription-ID"
   ```

## Deployment Steps

### 1. Initialize Terraform
```bash
cd infrastructure/terraform
terraform init
```

### 2. Review the Plan
```bash
terraform plan -out=tfplan
```

### 3. Apply the Configuration
```bash
terraform apply tfplan
```

Or combine plan and apply:
```bash
terraform apply -auto-approve
```

### 4. View Outputs
```bash
terraform output
```

## Configuration

### Environment Variables
Create a `terraform.tfvars` file:
```hcl
environment = "dev"
location    = "eastus"
project_name = "responsibleai"

tags = {
  Project     = "Responsible AI Agent"
  Environment = "dev"
  ManagedBy   = "Terraform"
  Owner       = "your-email@microsoft.com"
}
```

### Different Environments
```bash
# Development
terraform apply -var="environment=dev"

# Staging
terraform apply -var="environment=staging"

# Production
terraform apply -var="environment=prod"
```

## Resource Provisioning

This Terraform configuration creates:

1. **Resource Group** - Container for all resources
2. **Storage Account** - For Azure Functions and report storage
3. **Cosmos DB** - NoSQL database for submissions and reviews
4. **Azure OpenAI** - GPT-4 for AI-powered reviews
5. **Key Vault** - Secure secret storage
6. **Application Insights** - Monitoring and telemetry
7. **Function App** - Backend API (Python)
8. **Web App** - Frontend application (Node.js/Next.js)

## Post-Deployment Configuration

### 1. Deploy Azure OpenAI Model
```bash
# Note: You need Azure OpenAI access approval first
# Apply at: https://aka.ms/oai/access

# Create GPT-4 deployment
az cognitiveservices account deployment create \
  --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw openai_endpoint | cut -d'/' -f3 | cut -d'.' -f1) \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-name "Standard" \
  --sku-capacity 10
```

### 2. Deploy Backend Functions
```bash
cd ../../backend
func azure functionapp publish $(cd ../infrastructure/terraform && terraform output -raw function_app_name)
```

### 3. Deploy Frontend
```bash
cd ../frontend
npm run build

# Using Azure CLI
az webapp deployment source config-zip \
  --resource-group $(cd ../infrastructure/terraform && terraform output -raw resource_group_name) \
  --name $(cd ../infrastructure/terraform && terraform output -raw frontend_app_name) \
  --src build.zip
```

## Monitoring and Management

### View Logs
```bash
# Function App logs
az webapp log tail --name $(terraform output -raw function_app_name) --resource-group $(terraform output -raw resource_group_name)

# Frontend logs
az webapp log tail --name $(terraform output -raw frontend_app_name) --resource-group $(terraform output -raw resource_group_name)
```

### Scale Function App
```bash
az functionapp plan update \
  --resource-group $(terraform output -raw resource_group_name) \
  --name asp-responsibleai-dev \
  --sku B1
```

## Cleanup

### Destroy All Resources
```bash
terraform destroy -auto-approve
```

### Selective Destroy
```bash
# Remove specific resource
terraform destroy -target=azurerm_linux_web_app.frontend
```

## Troubleshooting

### Common Issues

1. **Azure OpenAI Not Available**
   - Apply for access at https://aka.ms/oai/access
   - Change region if not available in selected location

2. **Name Already Exists**
   - Storage and Key Vault names must be globally unique
   - Modify `project_name` in variables

3. **Insufficient Permissions**
   - Ensure you have Contributor role on subscription
   - Check Azure AD permissions for Key Vault

### State Management

```bash
# View current state
terraform show

# List resources
terraform state list

# Refresh state
terraform refresh
```

## Security Best Practices

1. **Never commit secrets** - Use Key Vault for all secrets
2. **Enable RBAC** - Use managed identities where possible
3. **Network Security** - Configure firewall rules for production
4. **Monitoring** - Set up alerts in Application Insights
5. **Backup** - Enable backup for Cosmos DB and Storage

## Cost Optimization

- Use **Consumption Plan** for Function Apps (pay-per-use)
- Use **Serverless Cosmos DB** for variable workloads
- Set up **Azure Budget alerts**
- Review costs: https://portal.azure.com/#blade/Microsoft_Azure_CostManagement

## Additional Resources

- [Terraform Azure Provider Docs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Functions Terraform](https://learn.microsoft.com/azure/azure-functions/functions-infrastructure-as-code)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
