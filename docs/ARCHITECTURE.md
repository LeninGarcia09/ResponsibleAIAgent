# System Architecture Documentation

**Responsible AI Agent Platform**  
Version 2.0.0 | December 2025

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Response Structure](#response-structure)

## System Overview

The Responsible AI Agent Platform uses a layered architecture with adaptive prompt engineering to provide context-aware RAI guidance.

### Design Principles
1. **Layered Architecture**: Clear separation between presentation, application, and service layers
2. **Graceful Degradation**: Fallback paths ensure system functions even when components fail
3. **Progressive Disclosure**: UI presents information hierarchically
4. **Context-Aware Processing**: Adapts response depth based on input completeness
5. **Stateless Design**: Each request is independent

## Architecture Patterns

### 1. Adaptive Response Pattern
- Input completeness score (0-100) determines response depth
- Four levels: MINIMAL, BASIC, DETAILED, COMPREHENSIVE
- Implementation: `response_adapter.py:assess_and_configure()`

### 2. Graceful Degradation Pattern
- Try Adaptive System → Try Legacy AI → Use Static Recommendations
- Availability flags: ADAPTIVE_SYSTEM_AVAILABLE, KNOWLEDGE_AVAILABLE, DYNAMIC_RESOURCES_AVAILABLE

### 3. Augmentation Pattern
- AI Response → Calculate Fallback Risks → Merge → Add Dynamic Resources
- Critical: Risk scores merge BEFORE checking DYNAMIC_RESOURCES_AVAILABLE flag (commit 297c379)

### 4. Scenario-Based Personalization
- 8 curated scenarios with tailored guidance
- Token-based scoring with SCENARIO_KEYWORD_HINTS
- Injects scenario-specific context (risk profile, tools, stakeholders)

## Component Design

### Core Components
1. **app.py**: Flask API server (13 endpoints)
2. **adaptive_prompt_builder.py**: Context-aware prompt generation
3. **response_adapter.py**: Input assessment, priority mapping
4. **knowledge_loader.py**: RAI tools catalog integration
5. **dynamic_resources.py**: Real-time research & repos
6. **test-ui.html**: Standalone UI

## Data Flow

User Input → submit_review() → generate_recommendations_adaptive() 
→ Azure OpenAI → augment_with_dynamic_resources() → Response → UI Rendering

**Time**: ~5-8 seconds end-to-end

## Response Structure

Complete response includes:
- risk_scores (always populated via merge)
- recommendations_by_pillar (6 RAI principles)
- quick_start_guide (week 1 checklist, roadmap, stakeholders)
- reference_architecture (Azure services, repos, docs)
- tiered_recommendations (critical/high/recommended/nice-to-have)
- _adaptive_metadata (depth, completeness score, suggestions)

## Extensibility

### Adding a New Scenario
1. Update `rai_tools_catalog.json`
2. Add keyword hints to SCENARIO_KEYWORD_HINTS
3. Add stakeholders to SCENARIO_STAKEHOLDERS
4. Add project type mapping (optional)

**Document Version**: 2.0.0  
**Last Updated**: December 13, 2025
