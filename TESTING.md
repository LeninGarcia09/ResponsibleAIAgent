# Testing Guide - Responsible AI Agent

## ✅ Testing Status Summary

### Backend Components
- ✅ **Python Dependencies**: Installed successfully
- ✅ **Configuration Module**: Working
- ✅ **Data Models**: All models validated
- ✅ **Azure Client Modules**: Imported successfully
- ✅ **Function Structures**: All 3 functions present and valid
- ⏳ **Azure Functions Runtime**: Requires Azure Functions Core Tools
- ⏳ **Azure Service Connections**: Requires Azure credentials

### Frontend Components
- ⏳ **Not yet tested** - Next phase

---

## 🧪 Backend Testing

### Prerequisites Installed
- Python 3.13.7 ✅
- Required Python packages ✅

### Test Results

#### 1. Configuration Test
```bash
cd backend
python test_backend.py
```

**Result**: ✅ PASSED
- Config module loads correctly
- Default settings applied
- Environment variables ready for Azure credentials

#### 2. Data Models Test
**Result**: ✅ PASSED
- All 7 Responsible AI Principles defined
- All 6 Security Check Types defined
- Models can be instantiated
- Pydantic validation working

#### 3. Azure Clients Test
**Result**: ✅ PASSED (without credentials)
- Client initialization functions imported
- Ready for Azure credential configuration
- Will connect when credentials provided

#### 4. Function Structure Test
**Result**: ✅ PASSED
- SubmitReview function ✅
- ProcessReview function ✅
- GenerateReport function ✅

---

## 🚀 Next Steps for Full Testing

### Step 1: Install Azure Functions Core Tools

#### Option A: Using npm (Recommended)
```powershell
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

#### Option B: Using Chocolatey
```powershell
choco install azure-functions-core-tools-4
```

#### Option C: Using MSI Installer
Download from: https://aka.ms/functions-core-tools-4

### Step 2: Configure Azure Credentials

Edit `backend/local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    
    // Azure OpenAI (Required for AI Review)
    "AZURE_OPENAI_ENDPOINT": "https://your-instance.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "your-key-here",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
    
    // Cosmos DB (Required for data storage)
    "COSMOS_DB_ENDPOINT": "https://your-account.documents.azure.com:443/",
    "COSMOS_DB_KEY": "your-key-here",
    
    // Blob Storage (Required for reports)
    "STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=...",
    
    // Microsoft Graph (Optional - for emails)
    "GRAPH_API_CLIENT_ID": "your-client-id",
    "GRAPH_API_CLIENT_SECRET": "your-secret",
    "GRAPH_API_TENANT_ID": "your-tenant-id"
  }
}
```

### Step 3: Test Locally Without Azure (Mock Mode)

For testing the application flow without Azure services:

1. **Comment out Azure service calls** in the functions
2. **Use in-memory storage** for testing
3. **Mock AI responses** for review engine

Or create a test mode configuration:

```python
# In shared/config.py
use_mock_services = os.getenv("USE_MOCK_SERVICES", "false").lower() == "true"
```

### Step 4: Start Azure Functions Locally

```powershell
cd backend
func start
```

Expected output:
```
Azure Functions Core Tools
Core Tools Version: 4.x.x
Function Runtime Version: 4.x.x

Functions:
  SubmitReview: [POST] http://localhost:7071/api/submit-review
  ProcessReview: [POST] http://localhost:7071/api/process-review
  GenerateReport: [POST] http://localhost:7071/api/generate-report
```

### Step 5: Test API Endpoints

#### Test SubmitReview
```powershell
$body = @{
    submitter_email = "test@microsoft.com"
    submitter_name = "Test User"
    project_name = "Test AI Project"
    project_description = "Testing the review system"
    ai_capabilities = @("NLP", "Computer Vision")
    data_sources = @("User Data")
    user_impact = "Medium"
    deployment_stage = "Development"
    fairness_assessment = "We have implemented bias testing"
    data_encryption_method = "AES-256"
    access_control_mechanism = "RBAC"
    compliance_certifications = @("SOC2")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7071/api/submit-review" -Method POST -Body $body -ContentType "application/json"
```

Expected response:
```json
{
  "message": "Submission received successfully",
  "submission_id": "uuid-here",
  "status": "pending"
}
```

---

## 📊 Test Coverage

### ✅ Completed Tests
1. Module imports and dependencies
2. Configuration loading
3. Data model validation
4. Function structure verification

### ⏳ Pending Tests
1. Azure Functions runtime execution
2. API endpoint integration tests
3. Azure service connectivity
4. End-to-end submission workflow
5. Report generation
6. Email notifications
7. Frontend application

---

## 🐛 Troubleshooting

### Issue: Import errors when running functions
**Solution**: Ensure you're in the `backend` directory and Python path is set correctly

### Issue: Azure Functions Core Tools not found
**Solution**: Install using npm or chocolatey (see Step 1 above)

### Issue: "Module not found" errors
**Solution**: 
```powershell
cd backend
pip install -r requirements.txt --upgrade
```

### Issue: Connection refused to Azure services
**Solution**: 
1. Check `local.settings.json` has correct credentials
2. Verify network connectivity
3. Confirm Azure resources are provisioned

---

## 📝 Test Checklist

Use this checklist to track your testing progress:

- [x] Python environment setup
- [x] Dependencies installed
- [x] Configuration module works
- [x] Data models validated
- [x] Azure clients imported
- [x] Function structures verified
- [ ] Azure Functions Core Tools installed
- [ ] Local function runtime started
- [ ] SubmitReview endpoint tested
- [ ] ProcessReview endpoint tested
- [ ] GenerateReport endpoint tested
- [ ] Frontend dependencies installed
- [ ] Frontend dev server started
- [ ] End-to-end workflow tested
- [ ] Azure deployment tested

---

## 📧 Need Help?

- Review the main [README.md](../README.md)
- Check [Azure Functions documentation](https://docs.microsoft.com/azure/azure-functions/)
- Verify [Azure OpenAI setup](https://learn.microsoft.com/azure/ai-services/openai/)

---

**Last Updated**: December 2, 2025
**Test Environment**: Windows with PowerShell
**Python Version**: 3.13.7
