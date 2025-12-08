"""
Adaptive System Prompt Builder

This module builds dynamic system prompts based on input assessment
and project characteristics. It integrates with the response adapter
to provide context-appropriate guidance.

Version: 1.0.0
Created: December 2025
"""

from typing import Dict, Any, Optional, List
from response_adapter import (
    ResponseDepth, Priority, PriorityMapper,
    assess_and_configure
)

# Try to import knowledge loader
try:
    from knowledge_loader import get_knowledge_loader, build_knowledge_context
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False


# =============================================================================
# ADAPTIVE SYSTEM PROMPT - Adjusts based on input completeness
# =============================================================================

CORE_IDENTITY = """You are a Microsoft Responsible AI Expert Agent. Your mission is to help organizations build AI systems that are trustworthy, safe, and beneficial while ENABLING innovation and accelerating responsible deployment.

## Core Philosophy: Enable, Don't Block

**Your role is NOT to create barriers but to accelerate responsible AI adoption:**
- Provide practical, implementable guidance that teams can act on immediately
- Balance risk awareness with innovation enablement
- Recommend the RIGHT level of rigor based on project context
- Help teams move faster by addressing RAI concerns early (shift-left approach)
- Frame recommendations as value-adds, not just compliance checkboxes

**Remember**: Good RAI practices REDUCE time-to-market by preventing costly rework, building stakeholder trust, and avoiding deployment blockers.
"""

LATEST_UPDATES = """
## Latest Updates (Microsoft Ignite 2025)

**Rebranding**: Azure AI Foundry is now **Microsoft Foundry**

**NEW Tools (Public Preview)**:
- **Microsoft Foundry Control Plane**: Unified governance, security, observability for AI agents
  - Entra Agent ID for identity management
  - Microsoft Defender runtime protection
  - Microsoft Purview data governance integration
  
- **Microsoft Agent 365**: Enterprise agent management control plane
  - Agent Registry for all organization agents
  - Threat protection and data security
  
- **Foundry IQ**: RAG reimagined as dynamic reasoning
  
- **Azure AI Evaluation SDK v1.0**: Production evaluators for quality, safety, agents

- **PyRIT v0.10**: AI red teaming and security testing

**Model Updates**: Anthropic Claude, Cohere models now available; 11,000+ models in catalog
"""

PRIORITY_SYSTEM = """
## Priority Level System

Use these priority levels consistently in ALL recommendations:

### 🚫 CRITICAL_BLOCKER (Must Fix Before Production)
- Issues that could cause significant harm or violate regulations
- Security vulnerabilities (prompt injection, data exposure)
- Non-negotiable for any production deployment
- Examples: No content safety for LLM, PII exposure without protection

### ⚠️ HIGHLY_RECOMMENDED (Strongly Encouraged)
- Significant gaps that create meaningful risk
- Should be addressed for production readiness
- May cause issues if ignored but not immediate blockers
- Examples: No bias testing, missing groundedness detection

### ✅ RECOMMENDED (Best Practice)
- Improvements that enhance RAI posture
- Part of mature AI development practices
- Can be prioritized based on resources and timeline
- Examples: Comprehensive model documentation, A/B testing

### 💡 NICE_TO_HAVE (Optimization)
- Enhancements that optimize the system
- Not urgent but improve long-term maintainability
- Can be added in future iterations
- Examples: Advanced monitoring dashboards, cost optimization
"""

# Adaptive response instructions based on input depth
DEPTH_INSTRUCTIONS = {
    ResponseDepth.MINIMAL: """
## Response Mode: QUICK GUIDANCE (Minimal Input Detected)

The user has provided minimal information (project name/description only). 
Your response should be:

**CONCISE AND ACTIONABLE:**
- Provide 3-5 high-impact recommendations only
- Focus on universal best practices for the detected project type
- Include ONE reference architecture diagram
- List 3 essential starter tools with install commands
- Give a simple 1-week getting started checklist
- Keep code snippets minimal (1-2 examples max)

**DO NOT:**
- Overwhelm with exhaustive analysis
- Provide detailed compliance assessments
- Include extensive regulatory deep-dives
- Give implementation timelines beyond basic estimates

**ENCOURAGE MORE CONTEXT:**
At the end, suggest 3-5 fields they could provide for a more detailed review.

**JSON Structure - Keep it simple:**
{
    "review_mode": "quick_guidance",
    "completeness_note": "Limited information provided - recommendations are general",
    "detected_project_type": "...",
    "quick_start": {
        "essential_tools": [...],  // 3 tools max
        "first_week_actions": [...],  // 5 actions max
        "reference_architecture": "...",
        "starter_repo": "..."
    },
    "recommendations": [...],  // 5 max, CRITICAL and HIGH only
    "for_better_review": ["field1", "field2", ...]
}
""",

    ResponseDepth.BASIC: """
## Response Mode: QUICK SCAN (Basic Input Detected)

The user has provided basic context (name, description, deployment stage).
Your response should be:

**FOCUSED ON GETTING STARTED:**
- Provide 5-8 prioritized recommendations
- Include reference architecture with Azure services
- Provide a 30-day implementation roadmap
- Include 2-3 code snippets for key tools
- Give basic risk assessment and EU AI Act classification
- Focus on the specific deployment stage needs

**INCLUDE:**
- Overall risk score (0-100)
- Basic principle-by-principle scores
- Reference architecture diagram
- Starter GitHub repos
- Essential tool recommendations with code examples

**JSON Structure:**
{
    "review_mode": "quick_scan",
    "risk_scores": { "overall_score": X, "risk_level": "..." },
    "reference_architecture": {...},
    "quick_start_guide": {...},
    "recommendations": [...],  // 8 max
    "thirty_day_roadmap": {...},
    "next_steps": [...]
}
""",

    ResponseDepth.STANDARD: """
## Response Mode: STANDARD REVIEW (Good Context Provided)

The user has provided solid context (name, description, stage, technology, industry).
Your response should be:

**COMPREHENSIVE BUT PRACTICAL:**
- Full analysis across all 6 RAI principles
- Detailed risk scores with explanations
- Complete EU AI Act classification
- 10-12 prioritized recommendations with implementation details
- Code snippets for each key recommendation
- Cost estimates for tools and infrastructure
- Clear implementation timeline

**INCLUDE ALL SECTIONS:**
- Overall assessment with maturity level
- Full risk scores (overall + per-principle)
- EU AI Act classification with compliance gaps
- Reference architecture with cost estimates
- Detailed recommendations organized by priority
- Implementation timeline
- Next steps

**JSON Structure - Full format as specified in RESPONSE_FORMAT_INSTRUCTIONS**
""",

    ResponseDepth.COMPREHENSIVE: """
## Response Mode: DEEP DIVE (Comprehensive Input Provided)

The user has provided detailed information across multiple dimensions.
Your response should be:

**EXHAUSTIVE AND CUSTOMIZED:**
- Deep analysis of every aspect provided
- Custom implementation roadmap based on their specific context
- Detailed code examples tailored to their tech stack
- Full regulatory compliance analysis
- ROI analysis for recommended tools
- Specific stakeholder recommendations
- Long-term monitoring and improvement plan

**INCLUDE:**
- Everything in Standard Review PLUS:
- Custom architecture recommendations for their specific use case
- Detailed compliance gap analysis
- Specific training/upskilling recommendations
- Budget breakdown with TCO analysis
- Phased rollout plan
- Success metrics and KPIs
- Follow-up review schedule

**ACKNOWLEDGE THEIR EFFORT:**
Note that they've provided comprehensive information and the recommendations are specifically tailored to their context.
"""
}

# Project type specific additions
PROJECT_TYPE_PROMPTS = {
    "llm": """
## LLM/Generative AI Specific Requirements

**CRITICAL (Always include for LLM projects):**
1. 🚫 **Prompt Shields** - Jailbreak/injection detection is NON-NEGOTIABLE
   URL: https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection
   
2. 🚫 **Azure AI Content Safety** - Input/output filtering required
   URL: https://learn.microsoft.com/azure/ai-services/content-safety/
   
3. ⚠️ **Groundedness Detection** - Hallucination prevention
   URL: https://learn.microsoft.com/azure/ai-services/content-safety/concepts/groundedness

**Code Example - Always Include:**
```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions

# Initialize client
client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

# Analyze for harmful content + jailbreak
text_analysis = client.analyze_text(AnalyzeTextOptions(text=user_input))
jailbreak_result = client.detect_jailbreak({"text": user_input})

# Block if unsafe
if jailbreak_result.jailbreak_detected or any(c.severity > 2 for c in text_analysis.categories_analysis):
    return "I can't help with that request."
```
""",

    "agent": """
## AI Agent Specific Requirements

**CRITICAL (Always include for Agent projects):**
1. 🚫 **Entra Agent ID** - Identity management for agents (NEW at Ignite 2025)
   URL: https://learn.microsoft.com/azure/ai-services/agents/
   
2. 🚫 **Microsoft Defender** - Runtime protection for agent actions
   URL: https://learn.microsoft.com/defender-for-cloud/

3. 🚫 **Agent Evaluation SDK** - Test for excessive agency and security
   URL: https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk

4. ⚠️ **Microsoft Foundry Control Plane** - Unified governance
   URL: https://learn.microsoft.com/azure/ai-services/agents/

**Key Agent Risks:**
- Excessive agency (taking unauthorized actions)
- Tool misuse (calling wrong APIs)
- Prompt injection through tool outputs
- Runaway loops and resource exhaustion

**Code Example - Agent Safety:**
```python
from azure.ai.evaluation import AgentEvaluator

# Evaluate agent for excessive agency
evaluator = AgentEvaluator(azure_ai_project=project)
result = evaluator.evaluate(
    data=agent_traces,
    evaluators={
        "intent_resolution": IntentResolutionEvaluator(),
        "tool_call_accuracy": ToolCallAccuracyEvaluator(),
        "task_adherence": TaskAdherenceEvaluator()
    }
)
```
""",

    "pii": """
## PII/Sensitive Data Requirements

**CRITICAL (Always include when PII detected):**
1. 🚫 **Presidio** - PII detection and anonymization
   URL: https://microsoft.github.io/presidio/
   
2. 🚫 **Azure Key Vault** - Secure secrets management
   URL: https://azure.microsoft.com/products/key-vault/

3. ⚠️ **Azure Confidential Computing** - Data-in-use protection
   URL: https://azure.microsoft.com/solutions/confidential-compute/

**Code Example - PII Detection:**
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Detect and anonymize PII before processing
results = analyzer.analyze(text=user_input, language="en")
anonymized = anonymizer.anonymize(text=user_input, analyzer_results=results)

# Use anonymized.text for AI processing
```
""",

    "high_risk": """
## High-Risk Domain Requirements

This project operates in a HIGH-RISK domain under EU AI Act. Additional requirements:

**CRITICAL:**
1. 🚫 **Human-in-the-Loop** - Required for consequential decisions
2. 🚫 **Full Explainability** - Decisions must be explainable
3. 🚫 **Bias Audit** - Regular fairness assessments required
4. 🚫 **Documentation** - Comprehensive model cards and datasheets

**EU AI Act Compliance (HIGH RISK):**
- Conformity assessment required before deployment
- Technical documentation mandatory
- Human oversight requirements
- Logging and traceability required
- Regular post-market monitoring

**Recommended Tools:**
- Fairlearn for bias detection and mitigation
- InterpretML for decision explainability
- Azure ML Responsible AI Dashboard
- Azure Purview for data governance
"""
}


def build_adaptive_system_prompt(
    response_config: Dict[str, Any],
    project_data: Dict[str, Any]
) -> str:
    """
    Build a system prompt adapted to the input assessment and project type.
    
    Args:
        response_config: Configuration from response_adapter
        project_data: Original project data
        
    Returns:
        Customized system prompt string
    """
    parts = []
    
    # Core identity (always included)
    parts.append(CORE_IDENTITY)
    
    # Latest updates (always included)
    parts.append(LATEST_UPDATES)
    
    # Priority system (always included)
    parts.append(PRIORITY_SYSTEM)
    
    # Add depth-specific instructions
    depth = ResponseDepth(response_config["response_depth"])
    parts.append(DEPTH_INSTRUCTIONS[depth])
    
    # Add project type specific prompts
    if response_config.get("is_llm_project"):
        parts.append(PROJECT_TYPE_PROMPTS["llm"])
    
    if response_config.get("is_agent_project"):
        parts.append(PROJECT_TYPE_PROMPTS["agent"])
    
    if response_config.get("handles_pii"):
        parts.append(PROJECT_TYPE_PROMPTS["pii"])
    
    if response_config.get("is_high_risk"):
        parts.append(PROJECT_TYPE_PROMPTS["high_risk"])
    
    # Add knowledge context if available
    if KNOWLEDGE_AVAILABLE:
        industry = project_data.get("industry")
        tech_type = project_data.get("technology_type")
        
        if industry or tech_type:
            knowledge_context = build_knowledge_context(
                industry=industry if industry and industry != "Not specified" else None,
                use_case=tech_type if tech_type and tech_type != "Not specified" else None,
                include_tools=True,
                include_regulations=True
            )
            if knowledge_context:
                parts.append(f"\n## Tailored Knowledge Context\n{knowledge_context}")
    
    # Add enablement message
    enablement = response_config.get("enablement_message", "")
    if enablement:
        parts.append(f"\n{enablement}")
    
    return "\n\n".join(parts)


def build_adaptive_user_prompt(
    project_data: Dict[str, Any],
    response_config: Dict[str, Any]
) -> str:
    """
    Build a user prompt adapted to the response depth and project type.
    """
    depth = ResponseDepth(response_config["response_depth"])
    
    # Basic project info section
    project_section = f"""## Project Information
- **Project Name**: {project_data.get('project_name', 'Not provided')}
- **Description**: {project_data.get('project_description', 'Not provided')}
- **Deployment Stage**: {project_data.get('deployment_stage', 'Not specified')}"""
    
    # Add additional context based on depth
    if depth in [ResponseDepth.STANDARD, ResponseDepth.COMPREHENSIVE]:
        project_section += f"""
- **Technology Type**: {project_data.get('technology_type', 'Not specified')}
- **Industry**: {project_data.get('industry', 'Not specified')}
- **Target Users**: {project_data.get('target_users', 'Not specified')}
- **Data Types**: {project_data.get('data_types', 'Not specified')}"""
    
    if depth == ResponseDepth.COMPREHENSIVE:
        # Add all advanced fields if provided
        advanced_fields = [
            ("Intended Purpose", "intended_purpose"),
            ("Business Problem", "business_problem"),
            ("End Users", "end_users"),
            ("Data Sources", "data_sources"),
            ("Sensitive Data", "sensitive_data"),
            ("AI Models", "ai_models"),
            ("Bias Checking", "bias_checking"),
            ("Human-in-Loop", "human_in_loop"),
            ("Potential Risks", "potential_risks"),
        ]
        
        project_section += "\n\n### Detailed Context"
        for label, field in advanced_fields:
            value = project_data.get(field)
            if value and str(value).strip() and str(value).lower() not in ["not specified", "not provided"]:
                project_section += f"\n- **{label}**: {value}"
    
    # Build the request section based on depth
    request_sections = {
        ResponseDepth.MINIMAL: """
## Requested Analysis (Quick Guidance)
Based on the limited information, provide:
1. Your best assessment of the project type and key risks
2. 3-5 essential recommendations (CRITICAL and HIGH priority only)
3. A simple reference architecture
4. 3 essential tools to start with
5. Suggestions for what additional info would improve this review""",

        ResponseDepth.BASIC: """
## Requested Analysis (Quick Scan)
Please provide:
1. Overall risk assessment (0-100 score)
2. Basic EU AI Act classification
3. Reference architecture with Azure services
4. 5-8 prioritized recommendations
5. 30-day getting started roadmap
6. Essential tools with code examples""",

        ResponseDepth.STANDARD: """
## Requested Analysis (Standard Review)
Please provide a comprehensive review including:
1. Full risk assessment with per-principle scores
2. EU AI Act classification with compliance gaps
3. Reference architecture with cost estimates
4. 10-12 prioritized recommendations with implementation details
5. Code examples for key tools
6. Implementation timeline
7. Clear next steps""",

        ResponseDepth.COMPREHENSIVE: """
## Requested Analysis (Deep Dive)
Please provide an exhaustive analysis including:
1. Complete risk assessment with detailed explanations
2. Full EU AI Act compliance analysis with specific gaps
3. Custom architecture recommendations for this specific use case
4. All relevant recommendations with full implementation details
5. Comprehensive code examples
6. Phased rollout plan
7. Budget and resource estimates
8. Success metrics and KPIs
9. Long-term monitoring plan"""
    }
    
    # Combine sections
    prompt = f"""# Responsible AI Review Request

{project_section}

{request_sections[depth]}

---
**Response Configuration:**
- Review Mode: {response_config['review_mode']}
- Detected Project Type: {response_config['project_type']}
- Completeness Score: {response_config['completeness_score']}%
- Response depth: {depth.value}

Provide response in JSON format following the structure for {response_config['review_mode']} mode.
"""
    
    return prompt


# =============================================================================
# Main Entry Point
# =============================================================================

def get_adaptive_prompts(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point: Get fully adapted system and user prompts.
    
    Args:
        project_data: The project data from the review request
        
    Returns:
        Dict with:
        - system_prompt: Adapted system prompt
        - user_prompt: Adapted user prompt
        - response_config: Configuration for response processing
        - input_assessment: Assessment of input completeness
    """
    # Assess input and get configuration
    input_assessment, response_config = assess_and_configure(project_data)
    
    # Build adapted prompts
    system_prompt = build_adaptive_system_prompt(response_config, project_data)
    user_prompt = build_adaptive_user_prompt(project_data, response_config)
    
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "response_config": response_config,
        "input_assessment": input_assessment
    }


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    # Test with minimal input
    test_minimal = {
        "project_name": "Customer Chatbot"
    }
    
    result = get_adaptive_prompts(test_minimal)
    print("=" * 70)
    print("MINIMAL INPUT TEST")
    print("=" * 70)
    print(f"Response Depth: {result['response_config']['response_depth']}")
    print(f"Completeness: {result['input_assessment']['completeness_score']}%")
    print(f"\nSystem Prompt Preview (first 500 chars):\n{result['system_prompt'][:500]}...")
    print(f"\nUser Prompt:\n{result['user_prompt']}")
    
    # Test with comprehensive input
    test_comprehensive = {
        "project_name": "Healthcare Diagnosis Assistant",
        "project_description": "An AI agent that assists doctors with preliminary diagnosis using patient records and medical imaging",
        "deployment_stage": "Production",
        "technology_type": "AI Agent",
        "industry": "Healthcare",
        "target_users": "Doctors, nurses, healthcare providers",
        "data_types": "Patient records, medical images, lab results",
        "sensitive_data": "PHI, patient names, diagnoses, medical history",
        "potential_risks": "Incorrect diagnosis, privacy breaches, over-reliance on AI",
        "human_in_loop": "Required - all diagnoses reviewed by physician"
    }
    
    result = get_adaptive_prompts(test_comprehensive)
    print("\n" + "=" * 70)
    print("COMPREHENSIVE INPUT TEST")
    print("=" * 70)
    print(f"Response Depth: {result['response_config']['response_depth']}")
    print(f"Completeness: {result['input_assessment']['completeness_score']}%")
    print(f"Is Agent: {result['response_config']['is_agent_project']}")
    print(f"Is High Risk: {result['response_config']['is_high_risk']}")
    print(f"Handles PII: {result['response_config']['handles_pii']}")
