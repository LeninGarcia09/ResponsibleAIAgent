"""
Tiered Recommendation System for World-Class RAI Reviews

This module provides a structured tiered approach to tool recommendations:
- Tier 1: NON-NEGOTIABLE (Required) - Tools/practices that MUST be implemented
- Tier 2: HIGHLY RECOMMENDED - Critical for production-ready systems
- Tier 3: RECOMMENDED - Best practices for mature implementations
- Tier 4: OPTIONAL - Nice-to-have for advanced/enterprise scenarios

Uses Jinja2 for dynamic template rendering of context-aware recommendations.

Version: 1.0.0
Last Updated: December 2025
"""

from jinja2 import Environment, BaseLoader
from typing import Dict, List, Any, Optional
from enum import Enum
import json


class RecommendationTier(Enum):
    """Tier levels for recommendations with clear business context."""
    NON_NEGOTIABLE = 1  # Required - Cannot deploy without these
    HIGHLY_RECOMMENDED = 2  # Critical for production readiness
    RECOMMENDED = 3  # Best practices for maturity
    OPTIONAL = 4  # Nice-to-have for enterprise


# Tier definitions with context
TIER_DEFINITIONS = {
    RecommendationTier.NON_NEGOTIABLE: {
        "label": "🚨 NON-NEGOTIABLE (Required)",
        "short_label": "Required",
        "color": "#d13438",
        "description": "These tools/practices are MANDATORY. Your AI system cannot be deployed without them.",
        "business_context": "Failure to implement these will result in regulatory non-compliance, security breaches, or critical system failures.",
        "timeline_guidance": "Must be implemented BEFORE any production deployment",
        "risk_if_skipped": "Critical - Deployment blockers, legal liability, safety incidents"
    },
    RecommendationTier.HIGHLY_RECOMMENDED: {
        "label": "⚠️ HIGHLY RECOMMENDED",
        "short_label": "Highly Recommended",
        "color": "#ffb900",
        "description": "Critical for production-ready systems. Skipping these creates significant risk.",
        "business_context": "These address major risk factors and are expected by enterprise customers and auditors.",
        "timeline_guidance": "Should be implemented within the first production release cycle",
        "risk_if_skipped": "High - Operational issues, audit failures, customer trust erosion"
    },
    RecommendationTier.RECOMMENDED: {
        "label": "✅ RECOMMENDED",
        "short_label": "Recommended",
        "color": "#107c10",
        "description": "Best practices for mature AI implementations. These differentiate good from great.",
        "business_context": "Demonstrates responsible AI maturity and positions you as an industry leader.",
        "timeline_guidance": "Plan for implementation within 3-6 months post-launch",
        "risk_if_skipped": "Medium - Technical debt, missed optimization opportunities"
    },
    RecommendationTier.OPTIONAL: {
        "label": "💡 OPTIONAL (Nice-to-Have)",
        "short_label": "Optional",
        "color": "#0078d4",
        "description": "Advanced capabilities for enterprise/specialized scenarios.",
        "business_context": "These provide competitive advantages and advanced governance capabilities.",
        "timeline_guidance": "Consider based on business requirements and resources",
        "risk_if_skipped": "Low - May limit advanced features or scale"
    }
}


# Context-aware tier assignment rules
TIER_RULES = {
    # Project context factors that escalate tier requirements
    "escalation_factors": {
        "high_risk_domain": ["healthcare", "finance", "legal", "law_enforcement", "employment", "education", "critical_infrastructure"],
        "pii_handling": True,
        "user_facing": True,
        "autonomous_decisions": True,
        "eu_ai_act_high_risk": True,
        "real_time_decisions": True,
        "vulnerable_populations": True
    },
    
    # Tool-to-tier mappings by use case
    "tool_tiers": {
        # Content Safety - tier varies by context
        "Azure AI Content Safety": {
            "default": RecommendationTier.HIGHLY_RECOMMENDED,
            "escalate_to_required_if": ["user_facing", "llm_chatbot", "content_generation"],
            "context_reason": {
                "user_facing": "Any user-facing AI MUST have content safety filters to prevent harmful outputs",
                "llm_chatbot": "LLM/Chatbots can generate unpredictable content - content safety is non-negotiable",
                "content_generation": "Generated content requires safety gates before user exposure"
            }
        },
        
        # PII Protection
        "Presidio": {
            "default": RecommendationTier.RECOMMENDED,
            "escalate_to_required_if": ["pii_handling", "healthcare", "finance"],
            "context_reason": {
                "pii_handling": "Any system processing PII MUST have detection and protection mechanisms",
                "healthcare": "HIPAA requires PII/PHI protection - Presidio provides this capability",
                "finance": "Financial data protection is regulatory requirement"
            }
        },
        
        # Fairness
        "Fairlearn": {
            "default": RecommendationTier.RECOMMENDED,
            "escalate_to_required_if": ["employment", "credit_decisions", "education", "high_impact_decisions"],
            "context_reason": {
                "employment": "Employment decisions MUST be assessed for demographic bias per EEOC guidelines",
                "credit_decisions": "Credit scoring requires fairness analysis per fair lending laws",
                "education": "Educational AI affecting student outcomes requires fairness assessment",
                "high_impact_decisions": "Any high-impact decision system requires bias analysis"
            }
        },
        
        # Explainability
        "InterpretML": {
            "default": RecommendationTier.RECOMMENDED,
            "escalate_to_required_if": ["healthcare", "finance", "legal", "eu_ai_act_high_risk"],
            "context_reason": {
                "healthcare": "Clinical decisions require explainability for medical professionals",
                "finance": "Adverse action notices require explanations per fair lending laws",
                "legal": "Legal AI must provide reasoning for professional review",
                "eu_ai_act_high_risk": "EU AI Act requires explainability for high-risk systems"
            }
        },
        
        # Evaluation
        "Azure AI Evaluation SDK": {
            "default": RecommendationTier.HIGHLY_RECOMMENDED,
            "escalate_to_required_if": ["llm_chatbot", "agent_system", "production"],
            "context_reason": {
                "llm_chatbot": "LLM outputs must be systematically evaluated for quality and safety",
                "agent_system": "AI agents require comprehensive evaluation before deployment",
                "production": "Production systems require ongoing evaluation frameworks"
            }
        },
        
        # Red Teaming
        "PyRIT": {
            "default": RecommendationTier.RECOMMENDED,
            "escalate_to_required_if": ["llm_chatbot", "agent_system", "high_risk_domain"],
            "context_reason": {
                "llm_chatbot": "LLMs must be red-teamed for jailbreaks and prompt injection",
                "agent_system": "Agents with tool access require adversarial testing",
                "high_risk_domain": "High-risk domains require security testing before deployment"
            }
        },
        
        # Governance
        "Microsoft Foundry Control Plane": {
            "default": RecommendationTier.OPTIONAL,
            "escalate_to_required_if": ["enterprise", "multi_agent", "regulated_industry"],
            "context_reason": {
                "enterprise": "Enterprise deployments need centralized governance",
                "multi_agent": "Multi-agent systems require unified control and observability",
                "regulated_industry": "Regulated industries need audit-ready governance"
            }
        },
        
        # Prompt Engineering
        "Prompt Shields": {
            "default": RecommendationTier.HIGHLY_RECOMMENDED,
            "escalate_to_required_if": ["llm_chatbot", "user_facing", "external_data"],
            "context_reason": {
                "llm_chatbot": "Chatbots are vulnerable to prompt injection - shields are essential",
                "user_facing": "User-facing LLMs must protect against malicious prompts",
                "external_data": "Systems processing external data need injection protection"
            }
        },
        
        # Groundedness
        "Groundedness Detection": {
            "default": RecommendationTier.RECOMMENDED,
            "escalate_to_required_if": ["rag_system", "healthcare", "legal", "finance"],
            "context_reason": {
                "rag_system": "RAG systems must verify response grounding to prevent hallucinations",
                "healthcare": "Medical information must be factually grounded",
                "legal": "Legal information must be verified against sources",
                "finance": "Financial advice must be based on factual data"
            }
        }
    }
}


# Jinja2 template for system prompt enhancement
TIERED_SYSTEM_PROMPT_TEMPLATE = """
## Tiered Recommendation Framework

For this project review, apply the following tiered approach to ALL recommendations:

### Tier Classification System

{% for tier, definition in tier_definitions.items() %}
**{{ definition.label }}**
- {{ definition.description }}
- Business Context: {{ definition.business_context }}
- Timeline: {{ definition.timeline_guidance }}
- Risk if Skipped: {{ definition.risk_if_skipped }}

{% endfor %}

### Context-Specific Tier Assignments

Based on this project's characteristics:
{% for characteristic in project_characteristics %}
- **{{ characteristic.name }}**: {{ characteristic.impact }}
{% endfor %}

The following tools/practices MUST be classified at the indicated tiers:

{% for tool, tier_info in tool_tier_assignments.items() %}
**{{ tool }}**: {{ tier_info.tier_label }}
- Reason: {{ tier_info.reason }}
{% endfor %}

### Required JSON Structure for Recommendations

Each recommendation MUST include:
```json
{
    "tier": "NON_NEGOTIABLE | HIGHLY_RECOMMENDED | RECOMMENDED | OPTIONAL",
    "tier_label": "🚨 NON-NEGOTIABLE (Required) | ⚠️ HIGHLY RECOMMENDED | ✅ RECOMMENDED | 💡 OPTIONAL",
    "tier_reason": "Specific reason why this tier was assigned for THIS project",
    "skip_risk": "What happens if this is not implemented",
    "implementation_deadline": "Before production | First release cycle | 3-6 months | As needed"
}
```

### Recommendation Ordering

ALWAYS order recommendations by tier:
1. First list ALL NON-NEGOTIABLE items
2. Then ALL HIGHLY RECOMMENDED items  
3. Then ALL RECOMMENDED items
4. Finally OPTIONAL items

Within each tier, order by impact (highest impact first).
"""


def get_project_characteristics(project_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Analyze project data to identify characteristics that affect tier assignments."""
    characteristics = []
    
    # Technology type analysis
    tech_type = project_data.get("technology_type", "").lower()
    if any(t in tech_type for t in ["llm", "chatbot", "gpt", "language model", "generative"]):
        characteristics.append({
            "name": "LLM/Generative AI",
            "impact": "Escalates content safety, prompt protection, and evaluation to NON-NEGOTIABLE"
        })
    
    if any(t in tech_type for t in ["agent", "autonomous", "agentic"]):
        characteristics.append({
            "name": "AI Agent/Autonomous System",
            "impact": "Escalates red teaming, guardrails, and governance to HIGHLY RECOMMENDED or NON-NEGOTIABLE"
        })
    
    # Industry analysis
    industry = project_data.get("industry", "").lower()
    if any(i in industry for i in ["health", "medical", "clinical", "pharma"]):
        characteristics.append({
            "name": "Healthcare Domain",
            "impact": "EU AI Act HIGH RISK - escalates explainability, fairness, and PII protection to NON-NEGOTIABLE"
        })
    elif any(i in industry for i in ["finance", "bank", "insurance", "credit"]):
        characteristics.append({
            "name": "Financial Services",
            "impact": "Regulatory requirements - escalates fairness, explainability, and audit trails to NON-NEGOTIABLE"
        })
    elif any(i in industry for i in ["legal", "law"]):
        characteristics.append({
            "name": "Legal Domain",
            "impact": "Professional liability - escalates explainability and groundedness to NON-NEGOTIABLE"
        })
    
    # Data types analysis
    data_types = project_data.get("data_types", "").lower()
    if any(d in data_types for d in ["pii", "personal", "ssn", "health", "financial", "biometric"]):
        characteristics.append({
            "name": "Handles PII/Sensitive Data",
            "impact": "Privacy regulations - escalates Presidio and data protection to NON-NEGOTIABLE"
        })
    
    # Target users analysis
    target_users = project_data.get("target_users", "").lower()
    if any(u in target_users for u in ["external", "customer", "consumer", "public"]):
        characteristics.append({
            "name": "External/Customer Facing",
            "impact": "User safety priority - escalates content safety and guardrails to NON-NEGOTIABLE"
        })
    
    if any(u in target_users for u in ["child", "minor", "student", "patient", "vulnerable"]):
        characteristics.append({
            "name": "Vulnerable Populations",
            "impact": "Heightened duty of care - escalates ALL safety measures to higher tiers"
        })
    
    # Deployment stage
    stage = project_data.get("deployment_stage", "").lower()
    if "production" in stage or "deployed" in stage:
        characteristics.append({
            "name": "Production System",
            "impact": "Live system - ALL non-negotiable and highly recommended items are URGENT"
        })
    
    # Additional context analysis
    additional = project_data.get("additional_context", "").lower()
    if any(term in additional for term in ["autonomous", "decision", "automated"]):
        characteristics.append({
            "name": "Automated Decision Making",
            "impact": "Human oversight requirements - escalates transparency and explainability"
        })
    
    return characteristics


def get_tool_tier_assignments(project_data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Determine tier assignments for tools based on project context."""
    assignments = {}
    
    # Get project characteristics for analysis
    tech_type = project_data.get("technology_type", "").lower()
    industry = project_data.get("industry", "").lower()
    data_types = project_data.get("data_types", "").lower()
    target_users = project_data.get("target_users", "").lower()
    
    for tool_name, tool_config in TIER_RULES["tool_tiers"].items():
        tier = tool_config["default"]
        reason = "Standard recommendation for this type of project"
        
        # Check escalation conditions
        escalation_conditions = tool_config.get("escalate_to_required_if", [])
        context_reasons = tool_config.get("context_reason", {})
        
        for condition in escalation_conditions:
            condition_lower = condition.lower()
            
            # Check if condition matches project characteristics
            matched = False
            matched_reason = ""
            
            if condition_lower == "user_facing" and any(u in target_users for u in ["external", "customer", "consumer", "public"]):
                matched = True
                matched_reason = context_reasons.get(condition, "User-facing system requires this tool")
            elif condition_lower == "llm_chatbot" and any(t in tech_type for t in ["llm", "chatbot", "gpt", "language"]):
                matched = True
                matched_reason = context_reasons.get(condition, "LLM/Chatbot requires this tool")
            elif condition_lower == "agent_system" and any(t in tech_type for t in ["agent", "autonomous", "agentic"]):
                matched = True
                matched_reason = context_reasons.get(condition, "Agent system requires this tool")
            elif condition_lower == "pii_handling" and any(d in data_types for d in ["pii", "personal", "ssn", "health"]):
                matched = True
                matched_reason = context_reasons.get(condition, "PII handling requires this tool")
            elif condition_lower == "healthcare" and any(i in industry for i in ["health", "medical", "clinical"]):
                matched = True
                matched_reason = context_reasons.get(condition, "Healthcare domain requires this tool")
            elif condition_lower == "finance" and any(i in industry for i in ["finance", "bank", "insurance"]):
                matched = True
                matched_reason = context_reasons.get(condition, "Financial services require this tool")
            elif condition_lower in industry.lower():
                matched = True
                matched_reason = context_reasons.get(condition, f"{condition} domain requires this tool")
            
            if matched:
                tier = RecommendationTier.NON_NEGOTIABLE
                reason = matched_reason
                break
        
        tier_def = TIER_DEFINITIONS[tier]
        assignments[tool_name] = {
            "tier": tier.name,
            "tier_label": tier_def["label"],
            "reason": reason
        }
    
    return assignments


def build_tiered_system_prompt(project_data: Dict[str, Any]) -> str:
    """Build the tiered recommendation section of the system prompt using Jinja2."""
    env = Environment(loader=BaseLoader())
    template = env.from_string(TIERED_SYSTEM_PROMPT_TEMPLATE)
    
    # Convert tier definitions for template
    tier_defs = {tier.name: definition for tier, definition in TIER_DEFINITIONS.items()}
    
    # Get project-specific assignments
    characteristics = get_project_characteristics(project_data)
    tool_assignments = get_tool_tier_assignments(project_data)
    
    rendered = template.render(
        tier_definitions=tier_defs,
        project_characteristics=characteristics,
        tool_tier_assignments=tool_assignments
    )
    
    return rendered


# Enhanced JSON schema for tiered recommendations
TIERED_JSON_SCHEMA = """
### Enhanced Recommendation Structure with Tiers

Your response MUST use this exact JSON structure:

```json
{
    "tiered_recommendations": {
        "non_negotiable": [
            {
                "id": "unique-id",
                "tier": "NON_NEGOTIABLE",
                "tier_label": "🚨 NON-NEGOTIABLE (Required)",
                "title": "Brief title",
                "principle": "RAI Principle this addresses",
                "issue": "What gap or risk this addresses",
                "recommendation": "Specific action to take",
                "tier_reason": "WHY this is non-negotiable for THIS specific project",
                "skip_risk": "Specific consequences if not implemented",
                "implementation_deadline": "Before production",
                "tools": [
                    {
                        "name": "Tool name",
                        "url": "https://...",
                        "purpose": "How it solves the issue",
                        "install": "pip install command"
                    }
                ],
                "implementation_steps": ["Step 1", "Step 2", "Step 3"],
                "code_example": {
                    "language": "python",
                    "code": "# Implementation code",
                    "explanation": "What this code does"
                },
                "effort": "Low | Medium | High",
                "time_estimate": "< 1 day | 1-5 days | 1-2 weeks"
            }
        ],
        "highly_recommended": [
            {
                "tier": "HIGHLY_RECOMMENDED",
                "tier_label": "⚠️ HIGHLY RECOMMENDED",
                ...same structure as above...
            }
        ],
        "recommended": [
            {
                "tier": "RECOMMENDED", 
                "tier_label": "✅ RECOMMENDED",
                ...same structure as above...
            }
        ],
        "optional": [
            {
                "tier": "OPTIONAL",
                "tier_label": "💡 OPTIONAL",
                ...same structure as above...
            }
        ]
    },
    "tier_summary": {
        "non_negotiable_count": 0,
        "highly_recommended_count": 0,
        "recommended_count": 0,
        "optional_count": 0,
        "critical_blockers": ["List of items that MUST be done before deployment"],
        "immediate_actions": ["Top 3 actions to take today"],
        "deployment_readiness": "NOT READY | CONDITIONAL | READY WITH MONITORING | PRODUCTION READY"
    },
    ...rest of response structure...
}
```

### Tier Assignment Guidelines

When assigning tiers, consider:

1. **NON-NEGOTIABLE (Required)**:
   - Safety-critical for this specific use case
   - Required by regulations (EU AI Act, HIPAA, etc.)
   - Prevents system failures or security breaches
   - Cannot deploy without this

2. **HIGHLY RECOMMENDED**:
   - Expected by enterprise customers
   - Required for audit compliance
   - Significantly reduces operational risk
   - Industry standard practice

3. **RECOMMENDED**:
   - Demonstrates AI maturity
   - Improves system quality
   - Reduces technical debt
   - Competitive advantage

4. **OPTIONAL**:
   - Advanced enterprise features
   - Nice-to-have optimizations
   - Future-proofing capabilities
   - Specialized use cases
"""


def get_tiered_recommendation_prompt() -> str:
    """Get the complete tiered recommendation prompt enhancement."""
    return TIERED_JSON_SCHEMA


def validate_tiered_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and enrich a tiered recommendation response."""
    errors = []
    warnings = []
    
    # Check for tiered_recommendations structure
    if "tiered_recommendations" not in response:
        # Try to convert legacy format
        if "recommendations" in response:
            response = convert_legacy_to_tiered(response)
            warnings.append("Converted legacy recommendation format to tiered structure")
    
    tiered = response.get("tiered_recommendations", {})
    
    # Validate each tier has the required structure
    for tier_name in ["non_negotiable", "highly_recommended", "recommended", "optional"]:
        tier_items = tiered.get(tier_name, [])
        for i, item in enumerate(tier_items):
            if "tier_reason" not in item:
                warnings.append(f"{tier_name}[{i}]: Missing tier_reason")
            if "skip_risk" not in item:
                warnings.append(f"{tier_name}[{i}]: Missing skip_risk")
    
    # Add validation results
    response["_validation"] = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
    
    return response


def convert_legacy_to_tiered(legacy_response: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a legacy flat recommendations list to tiered structure."""
    recommendations = legacy_response.get("recommendations", [])
    
    tiered = {
        "non_negotiable": [],
        "highly_recommended": [],
        "recommended": [],
        "optional": []
    }
    
    priority_to_tier = {
        "critical": "non_negotiable",
        "high": "highly_recommended",
        "medium": "recommended",
        "low": "optional"
    }
    
    for rec in recommendations:
        priority = rec.get("priority", "medium").lower()
        tier_key = priority_to_tier.get(priority, "recommended")
        
        # Enhance with tier information
        tier_enum = {
            "non_negotiable": RecommendationTier.NON_NEGOTIABLE,
            "highly_recommended": RecommendationTier.HIGHLY_RECOMMENDED,
            "recommended": RecommendationTier.RECOMMENDED,
            "optional": RecommendationTier.OPTIONAL
        }[tier_key]
        
        tier_def = TIER_DEFINITIONS[tier_enum]
        
        rec["tier"] = tier_enum.name
        rec["tier_label"] = tier_def["label"]
        rec["tier_reason"] = rec.get("tier_reason", "Assigned based on priority level")
        rec["skip_risk"] = rec.get("skip_risk", tier_def["risk_if_skipped"])
        rec["implementation_deadline"] = tier_def["timeline_guidance"]
        
        tiered[tier_key].append(rec)
    
    # Update response
    legacy_response["tiered_recommendations"] = tiered
    
    # Add tier summary
    legacy_response["tier_summary"] = {
        "non_negotiable_count": len(tiered["non_negotiable"]),
        "highly_recommended_count": len(tiered["highly_recommended"]),
        "recommended_count": len(tiered["recommended"]),
        "optional_count": len(tiered["optional"]),
        "critical_blockers": [r.get("title", "Untitled") for r in tiered["non_negotiable"]],
        "immediate_actions": [r.get("title", "Untitled") for r in (tiered["non_negotiable"] + tiered["highly_recommended"])[:3]],
        "deployment_readiness": "NOT READY" if tiered["non_negotiable"] else "CONDITIONAL"
    }
    
    return legacy_response


# Export main functions
__all__ = [
    'RecommendationTier',
    'TIER_DEFINITIONS',
    'build_tiered_system_prompt',
    'get_tiered_recommendation_prompt',
    'get_project_characteristics',
    'get_tool_tier_assignments',
    'validate_tiered_response',
    'convert_legacy_to_tiered'
]
