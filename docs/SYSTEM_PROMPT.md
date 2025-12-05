# System Prompt Documentation

## Overview

The system prompt defines the AI agent's persona, expertise, and behavior when reviewing AI projects for Responsible AI compliance. It's the core "brain" of the application.

## Location

```
backend/rai_system_prompt.py
```

## Format

The prompt is written in **Markdown format** embedded in a Python triple-quoted string. This provides:
- Human readability
- Easy version control (diff-friendly)
- Clear structure with headers

## Structure

### 1. Core Identity
```markdown
# Microsoft Responsible AI Review Agent

You are an expert Responsible AI (RAI) advisor at Microsoft...
```

Establishes the agent as a Microsoft RAI expert.

### 2. Response Guidelines
- Be Specific and Actionable
- Reference Microsoft Tools
- Prioritize Recommendations (Critical, High, Medium, Low)
- Consider Context
- Include URLs

### 3. Microsoft RAI Principles (6 Pillars)

| Principle | Key Focus |
|-----------|-----------|
| **Fairness** | Bias detection, demographic parity, Fairlearn |
| **Reliability & Safety** | Error handling, human oversight, Content Safety |
| **Privacy & Security** | Data minimization, PII protection, Presidio |
| **Inclusiveness** | Accessibility, multi-language, diverse users |
| **Transparency** | AI disclosure, explanations, Model Cards |
| **Accountability** | Governance, audit trails, Azure Purview |

### 4. LLM-Specific Requirements (CRITICAL)

For any LLM/GPT/Chatbot project, the agent MUST recommend:

1. **Prompt Shields** - Jailbreak detection (CRITICAL)
2. **Azure AI Content Safety** - Input/output filtering (CRITICAL)
3. **Groundedness Detection** - Hallucination prevention (HIGH)
4. **Azure OpenAI Content Filtering** - Built-in safety (CRITICAL)
5. **Azure AI Evaluation SDK** - Testing framework (HIGH)

### 5. Domain-Specific Guidelines

Tailored advice for:
- **Healthcare** - HIPAA, FDA, clinical validation
- **Finance** - Fair lending, explainability, SOX
- **HR** - Title VII, EEOC, adverse impact
- **Customer Service** - AI disclosure, escalation paths

### 6. Deployment Stage Guidelines

Stage-appropriate focus:
- **Development** - Design docs, data assessment, tool integration
- **Testing** - Adversarial testing, fairness metrics, user testing
- **Production** - Monitoring, incident response, kill switch

### 7. Quick-Start Guidance (NEW)

For basic reviews, provides:
- Week One Checklist (5-7 tasks)
- Getting Started Resources
- 30-Day Roadmap
- Quick Reference Card
- Templates & Checklists

### 8. Official Microsoft Resources

Curated URLs for:
- Core documentation
- Fairness & bias tools
- Interpretability
- Privacy & data protection
- Content safety & LLM security
- Governance & compliance

## Response Format

The agent is instructed to return JSON:

```json
{
  "overall_assessment": {
    "summary": "...",
    "maturity_level": "Initial | Developing | Defined | Managed | Optimizing",
    "key_strengths": [],
    "critical_gaps": []
  },
  "quick_start_guide": {
    "week_one_checklist": [],
    "essential_tools": [],
    "thirty_day_roadmap": {},
    "quick_reference": {},
    "templates_and_checklists": []
  },
  "recommendations": [],
  "summary": {},
  "next_steps": [],
  "reference_links": {}
}
```

## Modifying the Prompt

### Best Practices

1. **Version Control**: Always commit changes with descriptive messages
2. **Test Changes**: Use Azure AI Foundry evaluation before deploying
3. **Incremental Updates**: Make small, focused changes
4. **Document Changes**: Update this file when modifying the prompt

### Key Files

| File | Purpose |
|------|---------|
| `rai_system_prompt.py` | Main system prompt |
| `SYSTEM_PROMPT` | Core identity and guidelines |
| `USER_PROMPT_TEMPLATE` | How user input is formatted |
| `RESPONSE_FORMAT_INSTRUCTIONS` | Expected JSON structure |
| `DOMAIN_GUIDELINES` | Industry-specific advice |
| `DEPLOYMENT_STAGE_GUIDELINES` | Stage-specific focus |

### Testing Prompt Changes

1. **Local Testing**:
   ```bash
   cd backend
   python rai_system_prompt.py  # Prints example prompt
   ```

2. **Azure AI Foundry Evaluation** (recommended):
   - Create test cases covering different project types
   - Evaluate for consistency, accuracy, and helpfulness
   - Compare before/after metrics

3. **Manual Testing**:
   - Submit test projects via the UI
   - Verify recommendations match expectations
   - Check all required tools are recommended for LLM projects

## Contributing

When contributing prompt improvements:

1. Create a feature branch
2. Make changes to `rai_system_prompt.py`
3. Update this documentation
4. Test with sample projects
5. Submit PR with before/after examples

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 2025 | Initial prompt with RAI principles |
| 2.0 | Dec 2025 | Added mandatory LLM security requirements |
| 3.0 | Dec 2025 | Added quick-start guidance for basic reviews |

## Related Files

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [README.md](../README.md) - Project overview
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
