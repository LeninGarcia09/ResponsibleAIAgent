# Responsible AI Agent - Architecture

## Overview

The Responsible AI Agent is a web application that helps teams evaluate AI projects against responsible AI principles. It uses Azure OpenAI to provide intelligent assessments and recommendations.

## Environments

| Environment | Branch | Purpose | URLs |
|-------------|--------|---------|------|
| **Production** | `master` | Stable release | [Frontend](https://rai-frontend.graymoss-a8a3aef8.westus3.azurecontainerapps.io) / [API](https://rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io/api) |
| **Development** | `dev` | Testing & new features | [Frontend](https://rai-frontend-dev.blackdesert-120a609f.westus3.azurecontainerapps.io) / [API](https://rai-backend-dev.blackdesert-120a609f.westus3.azurecontainerapps.io/api) |

## Deployment Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Feature   │────▶│     Dev     │────▶│    Master   │
│   Branch    │     │   Branch    │     │   Branch    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │     DEV     │     │ PRODUCTION  │
                    │ Environment │     │ Environment │
                    └─────────────┘     └─────────────┘
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Azure Cloud                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐       ┌──────────────────┐                   │
│  │  Azure Container │       │  Azure Container │                   │
│  │  Apps (Frontend) │──────▶│  Apps (Backend)  │                   │
│  │  Next.js 14      │       │  Flask + Gunicorn│                   │
│  │  Port: 3000      │       │  Port: 8080      │                   │
│  └──────────────────┘       └────────┬─────────┘                   │
│                                      │                              │
│                                      │ Managed Identity             │
│                                      ▼                              │
│                          ┌──────────────────────┐                  │
│                          │  Azure OpenAI        │                  │
│                          │  GPT-4o Deployment   │                  │
│                          │  East US             │                  │
│                          └──────────────────────┘                  │
│                                                                      │
│  ┌──────────────────┐                                              │
│  │  Azure Container │                                              │
│  │  Registry (ACR)  │                                              │
│  └──────────────────┘                                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### Frontend (Next.js 14)
- **Location**: `frontend/`
- **Technology**: Next.js 14.2.18, React 18.3.1, TypeScript
- **Purpose**: User interface for submitting AI projects for review
- **Key Features**:
  - Basic Review (quick assessment)
  - Comprehensive Review (10-section wizard)
  - RAI Tools Catalog
  - Quick-Start Guide display

### Backend (Flask)
- **Location**: `backend/`
- **Technology**: Flask 3.1.2, Gunicorn, Azure OpenAI SDK
- **Purpose**: API layer that processes reviews and communicates with Azure OpenAI
- **Authentication**: Managed Identity (no API keys needed)
- **Key Endpoints**:
  - `POST /api/submit-review` - Basic review
  - `POST /api/submit-advanced-review` - Comprehensive review
  - `GET /api/health` - Health check
  - `GET /api/tools` - List RAI tools

### System Prompt
- **Location**: `backend/rai_system_prompt.py`
- **Purpose**: Defines the AI agent's behavior and expertise
- **Format**: Markdown embedded in Python
- **See**: [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md)

## Data Flow

```
1. User submits project details via Frontend
                    │
                    ▼
2. Frontend sends POST to Backend API
                    │
                    ▼
3. Backend builds prompt with:
   - System Prompt (RAI expertise)
   - User's project details
   - Domain-specific guidelines
   - Deployment stage guidelines
                    │
                    ▼
4. Backend calls Azure OpenAI (GPT-4o)
   via Managed Identity
                    │
                    ▼
5. Azure OpenAI returns JSON recommendations
                    │
                    ▼
6. Backend parses and returns to Frontend
                    │
                    ▼
7. Frontend displays:
   - Overall assessment
   - Quick-start guide
   - Prioritized recommendations
   - Reference links
```

## Security Architecture

### Authentication
- **Frontend → Backend**: HTTPS (no auth currently - add Azure AD for production)
- **Backend → Azure OpenAI**: Managed Identity (DefaultAzureCredential)
- **No API keys** stored in code or environment variables for OpenAI

### Content Safety
The system prompt instructs the AI to always recommend:
- Prompt Shields for jailbreak detection
- Azure AI Content Safety for input/output filtering
- Groundedness Detection for hallucination prevention

## Deployment

### Container Registry
- **Registry**: `raisimpleacr.azurecr.io`
- **Backend Image**: `rai-backend:v6`
- **Frontend Image**: `rai-frontend:v7`

### Container Apps Environment
- **Environment**: `rai-env`
- **Region**: West US 3
- **Backend URL**: https://rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io
- **Frontend URL**: https://rai-frontend.graymoss-a8a3aef8.westus3.azurecontainerapps.io

### Azure OpenAI
- **Resource**: `rai-openai-7538`
- **Region**: East US
- **Deployment**: `gpt-4o`
- **API Version**: `2024-08-01-preview`

## Configuration

### Environment Variables

**Backend**:
| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name (gpt-4o) |
| `AZURE_OPENAI_API_VERSION` | API version |

**Frontend**:
| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL |

## Scaling

- **Min replicas**: 0 (scale to zero when idle)
- **Max replicas**: 1 (adjust for production)
- **Resources per container**: 0.5 CPU, 1Gi memory

## Future Enhancements

1. **Authentication**: Add Azure AD authentication
2. **Database**: Store review history in Cosmos DB
3. **Evaluation**: Integrate Azure AI Foundry for prompt testing
4. **CI/CD**: GitHub Actions for automated deployments
5. **Monitoring**: Application Insights integration
