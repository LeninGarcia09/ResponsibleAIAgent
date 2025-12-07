# RAI Knowledge Update Log

This file tracks all updates to the RAI Agent knowledge base.

## Update Process

1. Identify update source (Ignite, Build, new tool release, regulation change)
2. Update relevant JSON file(s)
3. Validate with: `python knowledge_loader.py`
4. Add entry to this log
5. Commit and deploy

---

## 2025-12-06 - Ignite 2025 Major Update (v2.0.0)

**Source**: Microsoft Ignite 2025 (November 18-21, 2025)

**Key Changes**:

### New Tools Added
- **Microsoft Foundry Control Plane** (Public Preview)
  - Unified governance, security, and observability
  - Entra Agent ID integration
  - Microsoft Defender runtime protection
  - Microsoft Purview data governance
  
- **Microsoft Agent 365** (Public Preview)
  - Enterprise agent management
  - Agent Registry
  - Threat protection for agents

- **Foundry IQ** (Public Preview)
  - RAG as dynamic reasoning
  - Multi-source retrieval
  - Permission-aware access

- **GitHub + Defender Integration** (Public Preview)
  - AI-suggested security fixes
  - Code-to-cloud tracking

### Rebranding
- Azure AI Foundry → **Microsoft Foundry**
- Updated all documentation references

### Model Updates
- Anthropic Claude models now available
- Cohere models added
- 11,000+ models in catalog

### Files Updated
- [x] `rai_tools_catalog.json`
- [x] `microsoft_references.json`
- [x] `regulatory_frameworks.json`
- [x] `code_examples.json`

---

## Scheduled Reviews

| Date | Focus | Status |
|------|-------|--------|
| 2026-03-01 | Q1 tool version updates | Pending |
| 2026-05-01 | Microsoft Build 2026 | Pending |
| 2026-06-01 | EU AI Act full enforcement | Pending |
| 2026-11-01 | Microsoft Ignite 2026 | Pending |
