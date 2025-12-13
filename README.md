# 🤖 Responsible AI Agent Platform

> **AI-powered guidance for building trustworthy, safe, and beneficial AI systems**

An intelligent recommendation engine that provides context-aware responsible AI (RAI) guidance using Azure OpenAI, adaptive prompt engineering, and dynamic resource augmentation. Built to accelerate responsible AI adoption by providing actionable, project-specific recommendations aligned with Microsoft's RAI principles.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Azure](https://img.shields.io/badge/Azure-Container%20Apps-blue)](https://azure.microsoft.com/en-us/services/container-apps/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#%EF%B8%8F-architecture)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Documentation](#-documentation)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🎯 Overview

The Responsible AI Agent Platform helps organizations build AI systems that are trustworthy, safe, and beneficial. It provides:

- **Adaptive Recommendations**: Context-aware guidance that adjusts depth based on input completeness (quick review → comprehensive assessment)
- **Scenario-Based Personalization**: 8 curated scenarios (Healthcare AI, Financial Risk, Biometric, Children's Data, etc.) with tailored tool recommendations
- **Real-Time Research**: Bing-grounded latest updates on Microsoft RAI tools and frameworks
- **Progressive Disclosure UI**: Executive summary with collapsible detailed sections for better information hierarchy

### Core Philosophy

✅ **Enable, Don't Block**: Accelerate responsible AI adoption, not create barriers  
✅ **Shift-Left Approach**: Address RAI concerns early to reduce time-to-market  
✅ **Context-Appropriate Rigor**: Right level of guidance based on project risk  

---

## ✨ Key Features

### 🎨 Adaptive Prompt System
- **Input Assessment**: Scores completeness (0-100) to determine response depth
- **Dynamic Prompts**: Builds context-aware system/user prompts for Azure OpenAI
- **4 Depth Levels**: Minimal (quick guidance) → Basic → Detailed → Comprehensive

### 🧠 Knowledge Integration
- **RAI Tools Catalog**: 8 scenario-based tool recommendations from `rai_tools_catalog.json`
- **Scenario Detection**: Token-based scoring with keyword hints
- **Stakeholder Mapping**: Context-appropriate governance roles

### 🌐 Dynamic Resources
- **Latest Research**: Bing-grounded search for Microsoft RAI updates
- **GitHub Discovery**: Real-time reference implementation repos
- **Tool Versions**: Latest Microsoft RAI toolbox activity

### 📊 Risk Assessment
- **Fallback Scoring**: Rule-based heuristics ensure UI always populated
- **6 RAI Principles**: Fairness, Reliability & Safety, Privacy & Security, Inclusiveness, Transparency, Accountability
- **Critical Factors**: Detailed risk drivers (negative) and mitigating factors (positive)

### 🎯 Tiered Recommendations
- **🚫 Critical Blockers**: Must fix before production
- **⚠️ Highly Recommended**: Significant gaps, strong encouragement
- **✅ Recommended**: Best practices
- **💡 Nice to Have**: Optimizations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                Frontend: test-ui.html (Standalone)               │
│            Next.js 14 (localhost blocked by security)            │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          Backend: Flask API (Azure Container Apps)               │
│                                                                   │
│  POST /api/submit-review                                         │
│         ↓                                                         │
│  generate_recommendations_adaptive()                             │
│         ├─→ Input Assessment (completeness scoring)              │
│         ├─→ Scenario Detection (8 scenarios)                     │
│         ├─→ Adaptive Prompt Building                             │
│         └─→ Azure OpenAI API (gpt-4o)                            │
│         ↓                                                         │
│  augment_with_dynamic_resources()                                │
│         ├─→ Risk Score Merging (ALWAYS)                          │
│         ├─→ Bing-Grounded Research (if available)                │
│         ├─→ GitHub Repo Discovery (if available)                 │
│         └─→ Reference Architecture Population                    │
│         ↓                                                         │
│  Enhanced Response → Frontend                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│ Azure OpenAI │   │ Knowledge Loader │   │  Bing Search │
│   gpt-4o     │   │ rai_tools_catalog│   │  (grounding) │
└──────────────┘   └──────────────────┘   └──────────────┘
```

### Data Flow

1. **User Input** → `test-ui.html` form (project name, description, industry, etc.)
2. **API Request** → `POST /api/submit-review` with JSON payload
3. **Adaptive Engine** → `generate_recommendations_adaptive()` assesses input, builds prompts
4. **AI Generation** → Azure OpenAI returns structured JSON recommendations
5. **Augmentation** → `augment_with_dynamic_resources()` merges risk scores, fetches latest research
6. **Response** → Complete JSON with risk_scores, recommendations_by_pillar, quick_start_guide, reference_architecture
7. **UI Rendering** → `displayResults()` creates progressive disclosure view

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **app.py** | Flask API server, 13 endpoints | `backend/app.py` |
| **adaptive_prompt_builder.py** | Context-aware prompt generation | `backend/adaptive_prompt_builder.py` |
| **response_adapter.py** | Input assessment, priority mapping | `backend/response_adapter.py` |
| **knowledge_loader.py** | RAI tools catalog integration | `backend/knowledge_loader.py` |
| **dynamic_resources.py** | Real-time research & repos | `backend/dynamic_resources.py` |
| **test-ui.html** | Standalone UI (bypasses localhost security) | `test-ui.html` |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Azure Subscription** with Azure OpenAI access
- **Azure CLI** ([Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- **Git**

### Local Development Setup

#### 1. Clone Repository
```powershell
git clone https://github.com/LeninGarcia09/ResponsibleAIAgent.git
cd ResponsibleAIAgent
```

#### 2. Configure Backend
```powershell
cd backend
pip install -r requirements.txt

# Copy environment template
cp ../.env.development.example .env

# Edit .env with your Azure OpenAI credentials:
# AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT=gpt-4o
# AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

#### 3. Run Backend Locally
```powershell
# From backend/ directory
python app.py
# Server starts on http://localhost:8080
```

#### 4. Test with Standalone UI
```powershell
# Open test-ui.html in browser
start ../test-ui.html

# Or use curl to test API directly:
curl -X POST http://localhost:8080/api/submit-review `
  -H "Content-Type: application/json" `
  -d '{\"project_name\":\"Test AI\",\"project_description\":\"A healthcare AI assistant\",\"industry\":\"Healthcare\"}'
```

### Testing the Deployed Backend

The backend is already deployed to Azure Container Apps:

```powershell
# Health check
curl https://rai-backend-dev.greendesert-a8db4829.westus2.azurecontainerapps.io/api/health

# Submit review
curl -X POST https://rai-backend-dev.greendesert-a8db4829.westus2.azurecontainerapps.io/api/submit-review `
  -H "Content-Type: application/json" `
  --data-binary '@test_request.json'
```

---

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check, returns system status |
| `/api/submit-review` | POST | **PRIMARY**: Submit project for RAI review |
| `/api/submit-advanced-review` | POST | Comprehensive review with detailed questionnaire |
| `/api/assess-input` | POST | Assess input completeness without generating recommendations |

### Reference Data Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tools` | GET | List all RAI tools in catalog |
| `/api/references` | GET | Get reference architectures |
| `/api/reference-architectures` | GET | Detailed architecture guidance |
| `/api/github-repos` | GET | Discover relevant GitHub repos |

### Knowledge Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/knowledge/status` | GET | Knowledge loader health status |
| `/api/knowledge/reload` | POST | Reload tools catalog |
| `/api/knowledge/recommendations` | POST | Get scenario-specific tool recommendations |

### Example: Submit Review

**Request:**
```json
POST /api/submit-review
Content-Type: application/json

{
  "project_name": "Patient Care AI Assistant",
  "project_description": "An AI-powered chatbot that helps patients schedule appointments and get medical information",
  "industry": "Healthcare",
  "technology_type": "LLM/Generative AI",
  "deployment_stage": "Planning",
  "sensitive_data": "Patient names, appointment details",
  "ai_capabilities": ["personal_data", "decisions"]
}
```

**Response:**
```json
{
  "project_name": "Patient Care AI Assistant",
  "risk_scores": {
    "overall_score": 75,
    "risk_level": "High Risk",
    "risk_summary": "Healthcare AI with patient data requires comprehensive safety controls",
    "principle_scores": {
      "fairness": 70,
      "reliability": 65,
      "privacy": 60,
      "inclusiveness": 75,
      "transparency": 70,
      "accountability": 65
    },
    "critical_factors": {
      "score_drivers_negative": [
        "Healthcare context increases risk",
        "Personal data handling",
        "Production deployment planned"
      ],
      "score_drivers_positive": [
        "Planning stage allows early mitigation"
      ]
    }
  },
  "recommendations_by_pillar": {
    "reliability_safety": {
      "pillar_name": "Reliability & Safety",
      "recommendations": [
        {
          "title": "Implement Azure AI Content Safety",
          "priority": "🚫 CRITICAL_BLOCKER",
          "why_needed": "Healthcare chatbot must prevent harmful medical advice...",
          "what_happens_without": "Patients could receive dangerous misinformation...",
          "tool": {
            "name": "Azure AI Content Safety",
            "url": "https://azure.microsoft.com/en-us/products/ai-services/ai-content-safety"
          }
        }
      ]
    }
  },
  "quick_start_guide": {
    "week_one_checklist": [...],
    "30_day_roadmap": [...],
    "key_stakeholders": [...]
  },
  "reference_architecture": {
    "description": "Azure AI + Content Safety architecture for Healthcare AI applications",
    "azure_services": ["Azure OpenAI", "Azure AI Content Safety", "Azure Health Data Services"],
    "repos": [...]
  }
}
```

Full API documentation: [docs/API.md](./docs/API.md)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Detailed system design, data flow, component interactions |
| [docs/API.md](./docs/API.md) | Complete API reference with request/response schemas |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Azure deployment guide with infrastructure details |
| [QUICKSTART.md](./QUICKSTART.md) | Getting started tutorial |
| [TESTING.md](./TESTING.md) | Test strategy and pytest suite |

---

## 🚢 Deployment

### Current Production Deployment

**Environment:** Azure Container Apps (West US 2)  
**FQDN:** `rai-backend-dev.greendesert-a8db4829.westus2.azurecontainerapps.io`  
**Container Registry:** `ca41bef18c00acr.azurecr.io`  
**Current Image:** `rai-backend-dev:297c379` (includes risk_scores merge fix)

### Deploy to Azure Container Apps

```powershell
# 1. Build Docker image
cd backend
docker build -t rai-backend:latest .

# 2. Push to Azure Container Registry
az acr login --name <your-acr-name>
docker tag rai-backend:latest <your-acr-name>.azurecr.io/rai-backend:latest
docker push <your-acr-name>.azurecr.io/rai-backend:latest

# 3. Update Container App
az containerapp update \
  -n rai-backend-dev \
  -g ResponsibleAIAgent \
  --image <your-acr-name>.azurecr.io/rai-backend:latest \
  --set-env-vars \
    "AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/" \
    "AZURE_OPENAI_DEPLOYMENT=gpt-4o" \
    "AZURE_OPENAI_API_VERSION=2024-08-01-preview"
```

### Infrastructure as Code

See [infrastructure/](./infrastructure/) for Terraform/Bicep templates.

Full deployment guide: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 🧪 Testing

### Run Pytest Suite
```powershell
cd backend
pytest test_backend.py -v

# Expected output: 9 passing tests
# - test_config_settings_loads
# - test_model_instantiation
# - test_function_directories_present
# - test_finding_model_defaults
# - test_azure_client_factories_importable
```

### Manual Testing
```powershell
# Test health endpoint
curl http://localhost:8080/api/health

# Test full review flow
python backend/manual_checks.py
```

---

## 🤝 Contributing

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Add inline comments for complex logic
   - Update relevant documentation
   - Write/update tests

3. **Test Locally**
   ```bash
   pytest backend/test_backend.py
   python backend/app.py  # Manual testing
   ```

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request** to `dev` branch

### Code Style

- **Python**: Follow PEP 8, use type hints
- **Documentation**: Inline comments for complex logic, docstrings for all functions
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📝 License

MIT License - See [LICENSE](./LICENSE) for details

---

## 🙏 Acknowledgments

- **Microsoft Responsible AI Team** for RAI principles and tools
- **Azure OpenAI** for GPT-4 capabilities
- **Azure Container Apps** for serverless deployment

---

## 📧 Contact

**Maintainer:** Lenin Garcia  
**Repository:** [LeninGarcia09/ResponsibleAIAgent](https://github.com/LeninGarcia09/ResponsibleAIAgent)  
**Issues:** [GitHub Issues](https://github.com/LeninGarcia09/ResponsibleAIAgent/issues)

---

### 🔗 Quick Links

- [Microsoft Responsible AI](https://www.microsoft.com/en-us/ai/responsible-ai)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [Azure Container Apps](https://azure.microsoft.com/en-us/services/container-apps/)
- [Microsoft RAI Toolbox](https://github.com/microsoft/responsible-ai-toolbox)

---

**Version 2.0.0** | December 2025 | Built with ❤️ for responsible AI
