# Responsible AI Agent - System Architecture

## Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [System Architecture Diagram](#system-architecture-diagram)
- [Environments](#environments)
- [Project Structure](#project-structure)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [Knowledge Base System](#knowledge-base-system)
- [API Reference](#api-reference)
- [Data Flow](#data-flow)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security Architecture](#security-architecture)
- [Configuration](#configuration)
- [Scaling & Performance](#scaling--performance)
- [Future Enhancements](#future-enhancements)

---

## Overview

The **Responsible AI Agent** is an enterprise-grade web application that helps teams evaluate AI projects against Microsoft's Responsible AI principles. It provides intelligent assessments, actionable recommendations, and comprehensive tooling guidance powered by Azure OpenAI GPT-4o.

### Key Features
- **Basic Review**: Quick AI project assessment with instant recommendations
- **Comprehensive Review**: 10-section wizard for deep-dive analysis
- **RAI Tools Catalog**: Curated collection of Microsoft's Responsible AI tools
- **Use Case Scenarios**: 8 real-world implementation patterns with step-by-step guidance
- **Knowledge Base**: Externalized, version-controlled RAI knowledge

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.2.18 | React framework with App Router |
| **React** | 18.3.1 | UI component library |
| **TypeScript** | 5.x | Type-safe JavaScript |
| **CSS Modules** | - | Scoped component styling |
| **Node.js** | 20.x | Runtime environment |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11 | Core programming language |
| **Flask** | 3.0+ | Web framework |
| **Gunicorn** | 23.0+ | Production WSGI server |
| **Azure OpenAI SDK** | 1.x | AI integration |
| **Azure Identity** | - | Managed Identity auth |

### Infrastructure
| Service | Purpose |
|---------|---------|
| **Azure Container Apps** | Serverless container hosting |
| **Azure Container Registry** | Docker image storage |
| **Azure OpenAI** | GPT-4o AI model hosting |
| **Azure Entra ID** | Identity and access management |
| **GitHub Actions** | CI/CD automation |

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 Azure Cloud                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │                    Azure Container Apps Environment                      │  │
│   │                           (rai-env)                                      │  │
│   │  ┌──────────────────────┐         ┌──────────────────────┐             │  │
│   │  │   Frontend Service   │  HTTPS  │   Backend Service    │             │  │
│   │  │   (Next.js 14)       │────────▶│   (Flask + Gunicorn) │             │  │
│   │  │   Port: 3000         │         │   Port: 8080         │             │  │
│   │  │                      │         │                      │             │  │
│   │  │  ┌────────────────┐  │         │  ┌────────────────┐  │             │  │
│   │  │  │  React 18 UI   │  │         │  │ Knowledge Base │  │             │  │
│   │  │  │  TypeScript    │  │         │  │ (JSON Files)   │  │             │  │
│   │  │  │  CSS Modules   │  │         │  │                │  │             │  │
│   │  │  └────────────────┘  │         │  └────────────────┘  │             │  │
│   │  └──────────────────────┘         └──────────┬───────────┘             │  │
│   └──────────────────────────────────────────────│──────────────────────────┘  │
│                                                  │                              │
│                                                  │ Managed Identity             │
│                                                  │ (DefaultAzureCredential)     │
│                                                  ▼                              │
│   ┌──────────────────────────────────────────────────────────────┐            │
│   │                    Azure OpenAI Service                       │            │
│   │                    (rai-openai-7538)                          │            │
│   │                                                               │            │
│   │    ┌─────────────────┐    ┌─────────────────┐                │            │
│   │    │   GPT-4o        │    │  Content Safety │                │            │
│   │    │   Deployment    │    │  Filters        │                │            │
│   │    └─────────────────┘    └─────────────────┘                │            │
│   │                                                               │            │
│   └──────────────────────────────────────────────────────────────┘            │
│                                                                                  │
│   ┌─────────────────────┐     ┌─────────────────────┐                         │
│   │  Azure Container    │     │   Azure Entra ID     │                         │
│   │  Registry (ACR)     │     │   (OIDC Auth)        │                         │
│   │  raisimpleacr       │     │                      │                         │
│   └─────────────────────┘     └─────────────────────┘                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │   GitHub Actions    │
                              │   CI/CD Pipeline    │
                              │                     │
                              │  ┌───────────────┐  │
                              │  │ Build & Test  │  │
                              │  │ Deploy to ACA │  │
                              │  └───────────────┘  │
                              └─────────────────────┘
```

---

## Environments

| Environment | Branch | Frontend URL | Backend URL |
|-------------|--------|--------------|-------------|
| **Production** | `master` | [rai-frontend.graymoss-a8a3aef8.westus3.azurecontainerapps.io](https://rai-frontend.graymoss-a8a3aef8.westus3.azurecontainerapps.io) | [rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io](https://rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io/api) |
| **Development** | `dev` | [rai-frontend-dev.blackdesert-120a609f.westus3.azurecontainerapps.io](https://rai-frontend-dev.blackdesert-120a609f.westus3.azurecontainerapps.io) | [rai-backend-dev.blackdesert-120a609f.westus3.azurecontainerapps.io](https://rai-backend-dev.blackdesert-120a609f.westus3.azurecontainerapps.io/api) |

### Deployment Workflow

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

---

## Project Structure

```
ResponsibleAIAgent/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml              # Main CI/CD pipeline
│       └── pr-validation.yml      # PR checks
│
├── backend/                        # Python Flask API
│   ├── knowledge/                  # Externalized knowledge base
│   │   ├── rai_tools_catalog.json    # RAI tools & use cases
│   │   ├── microsoft_references.json  # Documentation links
│   │   ├── regulatory_frameworks.json # Compliance info
│   │   ├── code_examples.json        # Code snippets
│   │   └── README.md                 # Knowledge docs
│   ├── app.py                      # Flask application
│   ├── knowledge_loader.py         # Knowledge management
│   ├── rai_system_prompt.py        # AI system prompt
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Container build
│
├── frontend/                       # Next.js React UI
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── page.tsx              # Home page
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── catalog/              # RAI Tools Catalog
│   │   │   ├── submit/               # Review submission
│   │   │   └── reviews/              # Review history
│   │   └── lib/
│   │       └── api.ts              # API client
│   ├── next.config.js              # Next.js config
│   ├── package.json                # Node dependencies
│   └── Dockerfile                  # Container build
│
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md             # This file
│   ├── SYSTEM_PROMPT.md            # AI prompt docs
│   └── CONTRIBUTING.md             # Contributor guide
│
├── infrastructure/                 # IaC templates
└── evaluation/                     # AI evaluation scripts
```

---

## Frontend Architecture

### Technology Details
- **Framework**: Next.js 14.2.18 with App Router
- **UI Library**: React 18.3.1
- **Language**: TypeScript 5.x
- **Styling**: CSS Modules (component-scoped styles)
- **API Client**: Custom fetch-based client (`src/lib/api.ts`)

### Pages Structure

| Route | File | Description |
|-------|------|-------------|
| `/` | `app/page.tsx` | Home page with navigation |
| `/submit` | `app/submit/page.tsx` | Review submission forms (Basic/Comprehensive) |
| `/catalog` | `app/catalog/page.tsx` | RAI Tools Catalog with 3 tabs |
| `/reviews` | `app/reviews/page.tsx` | Review history display |

### Catalog Page Tabs

1. **Use Cases** (Default): 8 real-world AI implementation scenarios
2. **Tools & Services**: Curated Microsoft RAI tools by category
3. **Resources**: Documentation, references, and learning materials

### Key Components

```typescript
// API Client (src/lib/api.ts)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api'

class APIClient {
  // Submit basic review
  async submitReview(data: AIReviewSubmission): Promise<SubmissionResponse>
  
  // Submit comprehensive review
  async submitAdvancedReview(data: AdvancedReviewSubmission): Promise<SubmissionResponse>
  
  // Health check
  async healthCheck(): Promise<any>
}
```

---

## Backend Architecture

### Technology Details
- **Framework**: Flask 3.0+ (lightweight Python web framework)
- **WSGI Server**: Gunicorn 23.0+ (production-grade)
- **AI SDK**: Azure OpenAI Python SDK 1.x
- **Authentication**: Azure Identity (Managed Identity)

### Application Structure

```python
# Main Flask App (app.py)
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

app = Flask(__name__)
CORS(app)

# Azure OpenAI with Managed Identity
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_ad_token_provider=token_provider,
    api_version=AZURE_OPENAI_API_VERSION
)
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `app.py` | Flask routes, OpenAI integration |
| `rai_system_prompt.py` | AI system prompt definition |
| `knowledge_loader.py` | Knowledge base management |

---

## Knowledge Base System

The knowledge base uses **externalized JSON files** for easy updates without code changes.

### Files

| File | Purpose | Version |
|------|---------|---------|
| `rai_tools_catalog.json` | Tools, use cases, recommendations | 2.1.0 |
| `microsoft_references.json` | Documentation links | 2.0.0 |
| `regulatory_frameworks.json` | Compliance information | 1.0.0 |
| `code_examples.json` | Implementation snippets | 1.0.0 |

### Knowledge Loader

```python
# knowledge_loader.py
class KnowledgeLoader:
    @property
    def tools_catalog(self) -> Dict[str, Any]
    
    @property
    def microsoft_references(self) -> Dict[str, Any]
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]
    def get_tools_by_category(self, category: str) -> List[Dict]
    def get_use_case_recommendation(self, use_case: str) -> Dict
```

### Use Cases (8 Scenarios)

1. Customer Service Chatbot
2. Autonomous AI Agent
3. Loan Approval System
4. Content Generation Platform
5. Healthcare AI Diagnosis
6. RAG Knowledge Assistant
7. AI Image Generation
8. Multi-Agent System

---

## API Reference

### Base URLs
- **Development**: `https://rai-backend-dev.blackdesert-120a609f.westus3.azurecontainerapps.io/api`
- **Production**: `https://rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io/api`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/submit-review` | Basic AI review |
| `POST` | `/submit-advanced-review` | Comprehensive review |
| `GET` | `/tools` | Get RAI tools catalog |
| `GET` | `/knowledge-status` | Knowledge base status |

### Request/Response Examples

**POST /submit-review**
```json
{
  "project_name": "Customer Support AI",
  "project_description": "AI chatbot for customer inquiries",
  "ai_capabilities": ["NLP", "Sentiment Analysis"],
  "deployment_stage": "prototype",
  "industry": "retail"
}
```

**Response**
```json
{
  "submission_id": "uuid-here",
  "ai_powered": true,
  "overall_assessment": {
    "summary": "...",
    "maturity_level": "developing",
    "key_strengths": [...],
    "critical_gaps": [...]
  },
  "quick_start_guide": {...},
  "recommendations": [...]
}
```

---

## Data Flow

```
1. User submits project details via Frontend
                    │
                    ▼
2. Frontend sends POST to Backend API (/submit-review)
                    │
                    ▼
3. Backend builds prompt with:
   ├── System Prompt (RAI expertise)
   ├── User's project details
   ├── Knowledge Base context
   └── Response format instructions
                    │
                    ▼
4. Backend calls Azure OpenAI (GPT-4o)
   via Managed Identity authentication
                    │
                    ▼
5. Azure OpenAI returns JSON recommendations
                    │
                    ▼
6. Backend parses, validates, enriches response
                    │
                    ▼
7. Frontend displays:
   ├── Overall assessment with risk scores
   ├── Quick-start guide with checklists
   ├── Prioritized recommendations
   └── Reference links and tools
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

**Trigger Events**:
- Push to `master` → Deploy to Production
- Push to `dev` → Deploy to Development
- Pull Request → Build & Test only

### Pipeline Jobs

```yaml
jobs:
  setup:        # Determine environment (dev/prod)
  build-backend:
    - Checkout code
    - Setup Python 3.11
    - Install dependencies
    - Run linting (flake8)
    - Run tests (pytest)
    
  build-frontend:
    - Checkout code
    - Setup Node.js 20
    - Install dependencies
    - Run linting (ESLint)
    - Build application
    
  deploy:
    - Azure Login (OIDC/Federated Identity)
    - ACR Login
    - Build & Push Docker images
    - Deploy to Azure Container Apps
    - Health check verification
```

### Authentication

- **Method**: Azure Federated Identity (OIDC)
- **App ID**: `e88350d6-fc6b-4b9a-9d23-4b92c566e767`
- **Subjects**: `repo:YourOrg/ResponsibleAIAgent:ref:refs/heads/dev` and `master`

---

## Security Architecture

### Authentication Layers

| Layer | Method | Details |
|-------|--------|---------|
| GitHub → Azure | OIDC | Federated Identity, no stored secrets |
| Backend → Azure OpenAI | Managed Identity | DefaultAzureCredential |
| Frontend → Backend | HTTPS | TLS encryption |

### Content Safety

The system implements multiple safety layers:
1. **Prompt Shields**: Jailbreak/injection detection
2. **Azure AI Content Safety**: Input/output filtering
3. **Groundedness Detection**: Hallucination prevention

### No Secrets in Code
- All authentication uses Managed Identity
- No API keys stored in environment variables
- OIDC tokens for CI/CD

---

## Configuration

### Backend Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Model deployment name (gpt-4o) |
| `AZURE_OPENAI_API_VERSION` | No | API version (default: 2024-08-01-preview) |

### Frontend Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Backend API URL (set at build time) |

### Build-time Configuration

Frontend API URL is set during CI/CD build:
```yaml
- name: Build application
  run: npm run build
  env:
    NEXT_PUBLIC_API_BASE_URL: ${{ needs.setup.outputs.backend_url }}/api
```

---

## Scaling & Performance

### Container Resources

| Setting | Value | Notes |
|---------|-------|-------|
| Min Replicas | 0 | Scale to zero when idle |
| Max Replicas | 1 | Adjust for production load |
| CPU | 0.5 cores | Per container |
| Memory | 1 GB | Per container |

### Performance Optimizations

- **Knowledge Caching**: KnowledgeLoader caches JSON files in memory
- **Lazy Loading**: Knowledge files loaded on first access
- **Response Streaming**: (Future) Stream AI responses for faster perceived performance

---

## Future Enhancements

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| Azure AD Auth | High | User authentication for frontend |
| Cosmos DB | Medium | Store review history |
| Application Insights | Medium | Full observability |
| Response Streaming | Medium | Stream AI responses |
| Multi-language | Low | i18n support |
| Custom Domains | Low | Branded URLs |

---

## Related Documentation

- [System Prompt Documentation](./SYSTEM_PROMPT.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Quick Start Guide](../QUICKSTART.md)

---

*Last Updated: December 2025*
*Version: 2.1.0*
