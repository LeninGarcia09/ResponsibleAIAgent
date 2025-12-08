# System Card - RAI Tools Navigator

**Version:** 1.0.0  
**Date:** January 2025  
**Owner:** Lenin Garcia (lesalgad@microsoft.com)

---

## Model/System Overview

### Name
RAI Tools Navigator

### Description
An AI-powered conversational assistant that helps users discover, understand, and select appropriate Microsoft Responsible AI (RAI) tools and frameworks for their AI projects.

### Type
Retrieval-Augmented Generation (RAG) system with conversational AI interface

### Primary Use Case
Providing guidance on Microsoft's responsible AI toolkit to developers, data scientists, and AI practitioners

---

## Technical Specifications

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│   Next.js UI    │────▶│   Flask Backend  │────▶│  Azure OpenAI     │
│   (React 18)    │◀────│   (Python 3.11)  │◀────│  (GPT-4o)         │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Knowledge Base  │
                        │  (JSON Catalog)  │
                        └──────────────────┘
```

### Components

| Component | Technology | Version |
|-----------|------------|---------|
| Frontend | Next.js + React | 14.2.18 / 18 |
| Backend | Python + Flask | 3.11 / 3.0 |
| AI Model | Azure OpenAI GPT-4o | Latest |
| Deployment | Azure Container Apps | N/A |
| Authentication | Azure Managed Identity | N/A |

### Knowledge Base

| Category | Tool Count | Description |
|----------|------------|-------------|
| Governance & Control | 4 | Deployment safety, access control, threat detection |
| Content Safety | 6 | Text/image moderation, prompt shielding, jailbreak detection |
| Evaluation & Testing | 4 | Model evaluation, red teaming, benchmarking |
| Fairness & Bias | 1 | Fairness assessment and mitigation |
| Explainability | 1 | Model interpretation and explanation |
| Privacy | 5 | Differential privacy, adversarial ML, data protection |

---

## Intended Use

### Primary Users
- Software developers building AI applications
- Data scientists evaluating AI models
- AI/ML practitioners implementing responsible AI practices
- Product managers understanding RAI tool options

### Supported Tasks
1. Discovering relevant RAI tools for specific scenarios
2. Understanding tool capabilities and limitations
3. Comparing tools across RAI pillars
4. Getting implementation guidance and prerequisites
5. Learning about responsible AI principles

### Out-of-Scope Uses
- Medical, legal, or financial advice
- Production system configuration (guidance only)
- Automated decision-making without human oversight
- Processing of personal or sensitive data

---

## Training and Data

### Base Model
- **Model:** GPT-4o via Azure OpenAI Service
- **Provider:** Microsoft/OpenAI
- **Training Data:** As documented by OpenAI (general web corpus, books, etc.)

### RAG Knowledge Base
- **Source:** Curated Microsoft documentation and tool specifications
- **Format:** Structured JSON catalog (schema v2.2.0)
- **Updates:** Manual curation by tool owner
- **Last Updated:** January 2025

### Fine-Tuning
- No custom fine-tuning applied
- System relies on prompt engineering and RAG

---

## Performance Characteristics

### Response Quality
| Metric | Target | Notes |
|--------|--------|-------|
| Relevance | High | Responses should directly address user queries |
| Accuracy | Medium-High | Information based on curated knowledge base |
| Completeness | Medium | May not cover all edge cases |
| Latency | <5 seconds | Typical response time target |

### Known Limitations
1. Limited to tools in the curated catalog
2. May not reflect real-time updates to Microsoft documentation
3. Can produce plausible but incorrect information (hallucination)
4. No access to user's specific codebase or environment
5. English language only

---

## Safety and Responsible AI

### Content Safety Measures
- System prompt constraints to focus on RAI topics
- Refusal to generate harmful content
- Scope limitation to Responsible AI domain

### Human Oversight
- All recommendations require human validation
- Not designed for autonomous decision-making
- Users encouraged to verify with official documentation

### Fairness Considerations
- Training data reflects internet biases
- Tool recommendations are knowledge-base-driven, not personalized
- No user profiling or discriminatory filtering

### Privacy Protections
- No persistent storage of conversations
- No personal data collection requirements
- Azure-managed data handling

---

## Evaluation Results

### Testing Approach
| Test Type | Description | Status |
|-----------|-------------|--------|
| Functional | API endpoint testing | Passed |
| Integration | Frontend-backend communication | Passed |
| RAG Quality | Knowledge retrieval accuracy | Ongoing |
| Safety | Content safety filtering | Ongoing |
| User Acceptance | Pilot user feedback | In Progress |

### Metrics Tracked
- Response relevance (qualitative)
- System availability
- Error rates
- User feedback scores

---

## Deployment Information

### Current Status
**Pilot** - Limited release for testing and feedback

### Environments

| Environment | URL Pattern | Status |
|-------------|-------------|--------|
| Development | rai-frontend-dev.*.azurecontainerapps.io | Active |
| Production | rai-frontend.*.azurecontainerapps.io | Planned |

### Access Control
- Deployment via Azure Container Apps
- Azure Managed Identity for service-to-service auth
- No user authentication in pilot (network-level control)

---

## Ethical Considerations

### Potential Benefits
- Democratizes access to RAI knowledge
- Accelerates responsible AI adoption
- Reduces barrier to understanding complex tools

### Potential Risks
- Over-reliance on AI recommendations
- Incomplete or outdated information
- Misinterpretation of guidance

### Mitigations
- Clear disclaimers about AI-generated content
- Links to official documentation
- Encouragement of human review
- Regular knowledge base updates

---

## Maintenance and Updates

### Update Frequency
| Component | Frequency | Responsibility |
|-----------|-----------|----------------|
| Knowledge Base | As needed | Tool Owner |
| Frontend/Backend | As needed | Tool Owner |
| AI Model | Azure-managed | Microsoft |

### Feedback Mechanism
- Email: lesalgad@microsoft.com
- In-app feedback (planned)

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Jan 2025 | Initial pilot release |

---

## Contact and Ownership

**Tool Owner:** Lenin Garcia  
**Email:** lesalgad@microsoft.com  
**Organization:** Microsoft

---

## Related Documentation

- [Transparency Note](./TRANSPARENCY_NOTE.md)
- [Terms of Use](./TERMS_OF_USE.md)
- [Privacy Statement](./PRIVACY_STATEMENT.md)
- [README](../README.md)
- [Deployment Guide](../DEPLOYMENT.md)

---

*Last Updated: January 2025*
