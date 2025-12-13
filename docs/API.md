# API Documentation

**Responsible AI Agent Platform**  
Version 2.0.0 | December 2025

## Base URL

**Development**: `https://rai-backend-dev.greendesert-a8db4829.westus2.azurecontainerapps.io`  
**Local**: `http://localhost:8080`

## Authentication

- **Azure Managed Identity**: Backend uses DefaultAzureCredential for Azure OpenAI
- **CORS**: Configured for all origins in development (restrict in production)
- **No API Keys Required**: Public endpoints for testing

## Core Endpoints

### 1. Health Check

`GET /api/health`

Check backend health and system status.

**Response**:
`json
{
  "status": "healthy",
  "timestamp": "2025-12-13T10:30:00Z",
  "adaptive_system": true,
  "knowledge_loader": true,
  "dynamic_resources": true,
  "azure_openai": "connected"
}
`

### 2. Submit Review (PRIMARY)

`POST /api/submit-review`

Submit project for AI-powered RAI review.

**Request Body**:
`json
{
  "project_name": "Patient Care AI Assistant",
  "project_description": "An AI-powered chatbot...",
  "industry": "Healthcare",
  "technology_type": "LLM/Generative AI",
  "deployment_stage": "Planning",
  "sensitive_data": "Patient names, appointment details",
  "ai_capabilities": ["personal_data", "decisions"]
}
`

**Response**: See complete schema in ARCHITECTURE.md

**Time**: 5-8 seconds

### 3. Submit Advanced Review

`POST /api/submit-advanced-review`

Comprehensive review with detailed questionnaire data.

**Request Body**: Extended fields including bias_testing, monitoring_plan, etc.

### 4. Assess Input

`POST /api/assess-input`

Assess input completeness without generating recommendations.

**Response**:
`json
{
  "completeness_score": 65,
  "response_depth": "detailed",
  "suggestions": ["Specify deployment stage", "List AI capabilities"]
}
`

## Reference Data Endpoints

### 5. Tools Catalog

`GET /api/tools`

List all RAI tools in catalog.

### 6. References

`GET /api/references`

Get reference architectures.

### 7. GitHub Repos

`GET /api/github-repos?project_type=llm&use_case=healthcare`

Discover relevant GitHub repositories.

## Knowledge Management

### 8. Knowledge Status

`GET /api/knowledge/status`

Check knowledge loader health.

### 9. Reload Knowledge

`POST /api/knowledge/reload`

Reload tools catalog from disk.

### 10. Get Recommendations

`POST /api/knowledge/recommendations`

Get scenario-specific tool recommendations.

**Request**:
`json
{
  "scenario_id": "customer-chatbot",
  "project_type": "llm"
}
`

## Error Responses

All endpoints return standard error format:

`json
{
  "error": "Error message description",
  "details": "Optional additional context"
}
`

**Status Codes**:
- 200: Success
- 400: Bad request (missing required fields)
- 500: Internal server error

## Rate Limits

- Enforced at Azure Container Apps level
- Development: No hard limits
- Production: TBD

## Examples

### PowerShell
`powershell
curl.exe -X POST https://rai-backend-dev.greendesert-a8db4829.westus2.azurecontainerapps.io/api/submit-review `
  -H "Content-Type: application/json" `
  --data-binary '@test_request.json'
`

### cURL (bash)
`ash
curl -X POST https://rai-backend-dev.greendesert-a8db4829.westus2.azurecontainerapps.io/api/submit-review \
  -H "Content-Type: application/json" \
  -d '{\"project_name\":\"Test\",\"project_description\":\"Healthcare AI\"}'
`

### JavaScript
`javascript
const response = await fetch('https://rai-backend-dev.greendesert-a8db4829.westus2.azurecontainerapps.io/api/submit-review', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    project_name: 'Test',
    project_description: 'Healthcare AI'
  })
});
const data = await response.json();
`

**Document Version**: 2.0.0  
**Last Updated**: December 13, 2025
