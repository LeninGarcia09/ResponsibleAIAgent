# Deployment Script for Responsible AI Agent
# This script automates the deployment process to Azure

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment = 'dev',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipInfrastructure,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBackend,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESPONSIBLE AI AGENT DEPLOYMENT" -ForegroundColor Cyan
Write-Host "  Environment: $Environment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Azure CLI
try {
    $azVersion = az --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✓ Azure CLI installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Azure CLI not found. Please install: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

# Check Terraform
if (-not $SkipInfrastructure) {
    try {
        $tfVersion = terraform version 2>$null
        if ($LASTEXITCODE -ne 0) { throw }
        Write-Host "✓ Terraform installed" -ForegroundColor Green
    } catch {
        Write-Host "✗ Terraform not found. Please install: https://www.terraform.io/downloads" -ForegroundColor Red
        exit 1
    }
}

# Check Azure Functions Core Tools
if (-not $SkipBackend) {
    try {
        $funcVersion = func --version 2>$null
        if ($LASTEXITCODE -ne 0) { throw }
        Write-Host "✓ Azure Functions Core Tools installed" -ForegroundColor Green
    } catch {
        Write-Host "! Azure Functions Core Tools not found. Install with:" -ForegroundColor Yellow
        Write-Host "  npm install -g azure-functions-core-tools@4" -ForegroundColor Yellow
    }
}

# Check login status
Write-Host "`nChecking Azure login status..." -ForegroundColor Yellow
$accountInfo = az account show 2>$null | ConvertFrom-Json
if (-not $accountInfo) {
    Write-Host "✗ Not logged into Azure. Running 'az login'..." -ForegroundColor Yellow
    az login
    $accountInfo = az account show | ConvertFrom-Json
}
Write-Host "✓ Logged in as: $($accountInfo.user.name)" -ForegroundColor Green
Write-Host "✓ Subscription: $($accountInfo.name)" -ForegroundColor Green

# 1. Deploy Infrastructure
if (-not $SkipInfrastructure) {
    Write-Host "`n[1/3] Deploying Azure Infrastructure..." -ForegroundColor Cyan
    
    Push-Location "$PSScriptRoot\infrastructure\terraform"
    
    Write-Host "  Initializing Terraform..." -ForegroundColor Yellow
    terraform init
    
    Write-Host "  Planning deployment..." -ForegroundColor Yellow
    terraform plan -var="environment=$Environment" -out=tfplan
    
    Write-Host "  Applying infrastructure..." -ForegroundColor Yellow
    terraform apply tfplan
    
    Write-Host "  Getting outputs..." -ForegroundColor Yellow
    $functionAppName = terraform output -raw function_app_name
    $frontendAppName = terraform output -raw frontend_app_name
    $resourceGroupName = terraform output -raw resource_group_name
    
    Pop-Location
    
    Write-Host "✓ Infrastructure deployed successfully" -ForegroundColor Green
} else {
    Write-Host "`n[1/3] Skipping infrastructure deployment" -ForegroundColor Yellow
    
    # Try to get existing values
    Push-Location "$PSScriptRoot\infrastructure\terraform"
    $functionAppName = terraform output -raw function_app_name 2>$null
    $frontendAppName = terraform output -raw frontend_app_name 2>$null
    $resourceGroupName = terraform output -raw resource_group_name 2>$null
    Pop-Location
}

# 2. Deploy Backend (Azure Functions)
if (-not $SkipBackend -and $functionAppName) {
    Write-Host "`n[2/3] Deploying Backend (Azure Functions)..." -ForegroundColor Cyan
    
    Push-Location "$PSScriptRoot\backend"
    
    Write-Host "  Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    
    Write-Host "  Publishing to Azure..." -ForegroundColor Yellow
    func azure functionapp publish $functionAppName --python
    
    Pop-Location
    
    Write-Host "✓ Backend deployed successfully" -ForegroundColor Green
} else {
    Write-Host "`n[2/3] Skipping backend deployment" -ForegroundColor Yellow
}

# 3. Deploy Frontend (Next.js)
if (-not $SkipFrontend -and $frontendAppName) {
    Write-Host "`n[3/3] Deploying Frontend..." -ForegroundColor Cyan
    
    Push-Location "$PSScriptRoot\frontend"
    
    Write-Host "  Installing npm dependencies..." -ForegroundColor Yellow
    npm install --silent
    
    Write-Host "  Building frontend..." -ForegroundColor Yellow
    npm run build
    
    Write-Host "  Deploying to Azure..." -ForegroundColor Yellow
    # Create deployment package
    Compress-Archive -Path .next\* -DestinationPath deploy.zip -Force
    
    # Deploy using Azure CLI
    az webapp deployment source config-zip `
        --resource-group $resourceGroupName `
        --name $frontendAppName `
        --src deploy.zip
    
    Remove-Item deploy.zip
    
    Pop-Location
    
    Write-Host "✓ Frontend deployed successfully" -ForegroundColor Green
} else {
    Write-Host "`n[3/3] Skipping frontend deployment" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

if ($functionAppName) {
    Write-Host "Backend API: https://$functionAppName.azurewebsites.net" -ForegroundColor White
}
if ($frontendAppName) {
    Write-Host "Frontend:    https://$frontendAppName.azurewebsites.net" -ForegroundColor White
}

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Deploy GPT-4 model to Azure OpenAI" -ForegroundColor White
Write-Host "2. Configure Microsoft Graph API for email (optional)" -ForegroundColor White
Write-Host "3. Set up monitoring alerts in Application Insights" -ForegroundColor White
Write-Host "4. Test the application end-to-end" -ForegroundColor White

Write-Host "`nFor more information, see:" -ForegroundColor Yellow
Write-Host "  infrastructure/terraform/README.md" -ForegroundColor White
