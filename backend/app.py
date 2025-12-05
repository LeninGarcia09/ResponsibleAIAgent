from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import json
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

app = Flask(__name__)
CORS(app)

# Import system prompt
from rai_system_prompt import SYSTEM_PROMPT, build_full_prompt, RESPONSE_FORMAT_INSTRUCTIONS, OPENAI_CONFIG

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")  # e.g., https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")  # Your deployment name
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# Initialize Azure OpenAI client with Managed Identity
client = None
auth_method = None

try:
    if AZURE_OPENAI_ENDPOINT:
        # Use Managed Identity (DefaultAzureCredential)
        # This works with: Managed Identity, Azure CLI, VS Code, etc.
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=AZURE_OPENAI_API_VERSION
        )
        auth_method = "managed_identity"
        print(f"✓ Azure OpenAI initialized with Managed Identity")
        print(f"  Endpoint: {AZURE_OPENAI_ENDPOINT}")
        print(f"  Deployment: {AZURE_OPENAI_DEPLOYMENT}")
    else:
        print("⚠ AZURE_OPENAI_ENDPOINT not set - AI features disabled")
except Exception as e:
    print(f"✗ Failed to initialize Azure OpenAI: {e}")
    client = None

# Comprehensive Microsoft Responsible AI Tools & Resources
MICROSOFT_RAI_TOOLS = {
    "fairness": [
        {
            "name": "Fairlearn",
            "url": "https://fairlearn.org/",
            "description": "Open-source toolkit for assessing and improving fairness of AI systems. Includes metrics for group fairness and algorithms for mitigating unfairness.",
            "category": "Assessment & Mitigation"
        },
        {
            "name": "Azure Machine Learning Responsible AI Dashboard",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai-dashboard",
            "description": "Unified interface for model debugging, fairness assessment, error analysis, and interpretability in Azure ML.",
            "category": "Dashboard & Visualization"
        },
        {
            "name": "InterpretML",
            "url": "https://interpret.ml/",
            "description": "Microsoft's toolkit for training interpretable models and explaining blackbox systems.",
            "category": "Explainability"
        }
    ],
    "safety": [
        {
            "name": "Azure AI Content Safety",
            "url": "https://azure.microsoft.com/products/ai-services/ai-content-safety",
            "description": "Detect harmful content including hate speech, violence, self-harm, and sexual content in text and images.",
            "category": "Content Moderation"
        },
        {
            "name": "Azure OpenAI Content Filtering",
            "url": "https://learn.microsoft.com/azure/ai-services/openai/concepts/content-filter",
            "description": "Built-in content filtering for Azure OpenAI deployments to block harmful inputs and outputs.",
            "category": "Content Filtering"
        },
        {
            "name": "Prompt Shields",
            "url": "https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection",
            "description": "Detect and block prompt injection and jailbreak attempts in LLM applications.",
            "category": "Security"
        },
        {
            "name": "Groundedness Detection",
            "url": "https://learn.microsoft.com/azure/ai-services/content-safety/concepts/groundedness",
            "description": "Detect hallucinations and ungrounded content in LLM outputs.",
            "category": "Accuracy & Reliability"
        },
        {
            "name": "Azure AI Studio Safety Evaluations",
            "url": "https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-approach-gen-ai",
            "description": "Evaluate generative AI applications for safety, quality, and performance.",
            "category": "Evaluation"
        }
    ],
    "privacy": [
        {
            "name": "Presidio",
            "url": "https://microsoft.github.io/presidio/",
            "description": "Data protection and PII anonymization SDK. Detect and redact sensitive information in text and images.",
            "category": "PII Detection & Anonymization"
        },
        {
            "name": "SmartNoise",
            "url": "https://github.com/opendp/smartnoise-sdk",
            "description": "Differential privacy library for protecting individual privacy in data analysis.",
            "category": "Differential Privacy"
        },
        {
            "name": "Azure Confidential Computing",
            "url": "https://azure.microsoft.com/solutions/confidential-compute/",
            "description": "Protect data in use with hardware-based trusted execution environments.",
            "category": "Data Protection"
        },
        {
            "name": "Customer Lockbox",
            "url": "https://learn.microsoft.com/azure/security/fundamentals/customer-lockbox-overview",
            "description": "Control and audit Microsoft support access to your data.",
            "category": "Access Control"
        }
    ],
    "transparency": [
        {
            "name": "InterpretML / Explainable Boosting Machine",
            "url": "https://interpret.ml/",
            "description": "Glass-box models that are inherently interpretable while maintaining high accuracy.",
            "category": "Interpretable Models"
        },
        {
            "name": "SHAP (via InterpretML)",
            "url": "https://github.com/interpretml/interpret",
            "description": "SHapley Additive exPlanations for understanding feature contributions.",
            "category": "Model Explanation"
        },
        {
            "name": "Error Analysis",
            "url": "https://erroranalysis.ai/",
            "description": "Identify and diagnose model errors with tree-based error exploration.",
            "category": "Error Analysis"
        },
        {
            "name": "Azure OpenAI System Message Best Practices",
            "url": "https://learn.microsoft.com/azure/ai-services/openai/concepts/system-message",
            "description": "Guidelines for transparent system prompts in LLM applications.",
            "category": "LLM Transparency"
        },
        {
            "name": "Model Cards",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-model-card",
            "description": "Document model purpose, performance, limitations, and intended use.",
            "category": "Documentation"
        }
    ],
    "accountability": [
        {
            "name": "Azure Machine Learning MLOps",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment",
            "description": "End-to-end ML lifecycle management with versioning, lineage, and governance.",
            "category": "ML Lifecycle"
        },
        {
            "name": "Azure Purview / Microsoft Purview",
            "url": "https://azure.microsoft.com/products/purview/",
            "description": "Unified data governance for discovering, cataloging, and managing data assets.",
            "category": "Data Governance"
        },
        {
            "name": "Azure Policy",
            "url": "https://learn.microsoft.com/azure/governance/policy/overview",
            "description": "Enforce organizational standards and assess compliance at scale.",
            "category": "Compliance"
        },
        {
            "name": "Microsoft Responsible AI Impact Assessment Template",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai",
            "description": "Framework for assessing potential impacts of AI systems.",
            "category": "Assessment Framework"
        }
    ],
    "security": [
        {
            "name": "Azure AI Studio Red Teaming",
            "url": "https://learn.microsoft.com/azure/ai-studio/concepts/red-teaming",
            "description": "Adversarial testing tools for identifying vulnerabilities in AI systems.",
            "category": "Security Testing"
        },
        {
            "name": "Counterfit",
            "url": "https://github.com/Azure/counterfit",
            "description": "Microsoft's tool for security testing of AI systems against adversarial attacks.",
            "category": "Adversarial ML"
        },
        {
            "name": "Azure Key Vault",
            "url": "https://azure.microsoft.com/products/key-vault/",
            "description": "Secure storage for API keys, secrets, and certificates.",
            "category": "Secrets Management"
        },
        {
            "name": "Microsoft Defender for Cloud",
            "url": "https://azure.microsoft.com/products/defender-for-cloud/",
            "description": "Cloud security posture management and threat protection.",
            "category": "Cloud Security"
        }
    ],
    "llm_specific": [
        {
            "name": "Azure OpenAI Service",
            "url": "https://azure.microsoft.com/products/ai-services/openai-service/",
            "description": "Enterprise-grade OpenAI models with built-in responsible AI features.",
            "category": "LLM Platform"
        },
        {
            "name": "Semantic Kernel",
            "url": "https://learn.microsoft.com/semantic-kernel/",
            "description": "SDK for integrating LLMs with conventional programming, includes prompt management and planning.",
            "category": "LLM Development"
        },
        {
            "name": "Prompt Flow",
            "url": "https://learn.microsoft.com/azure/ai-studio/how-to/prompt-flow",
            "description": "Development tool for building, evaluating, and deploying LLM applications.",
            "category": "LLM Development"
        },
        {
            "name": "Azure AI Evaluation SDK",
            "url": "https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk",
            "description": "Programmatic evaluation of LLM applications for quality and safety.",
            "category": "LLM Evaluation"
        }
    ]
}

# Microsoft RAI Principles and Best Practices
MICROSOFT_RAI_PRINCIPLES = {
    "fairness": {
        "title": "Fairness",
        "description": "AI systems should treat all people fairly and avoid affecting similarly situated groups in different ways.",
        "key_questions": [
            "Who might be affected by this system?",
            "What demographic groups should be considered?",
            "How will performance be measured across groups?",
            "What is the acceptable disparity threshold?"
        ],
        "best_practices": [
            "Identify and document potential sources of bias in training data",
            "Test model performance across demographic groups before deployment",
            "Implement ongoing monitoring for fairness metrics in production",
            "Establish clear remediation processes for detected bias",
            "Include diverse perspectives in design and testing phases"
        ]
    },
    "reliability_safety": {
        "title": "Reliability & Safety",
        "description": "AI systems should perform reliably and safely under expected conditions and handle unexpected conditions gracefully.",
        "key_questions": [
            "What are the failure modes and their consequences?",
            "How will the system behave with out-of-distribution inputs?",
            "What human oversight is required?",
            "How quickly can the system be disabled if needed?"
        ],
        "best_practices": [
            "Define operational boundaries and document limitations",
            "Implement robust error handling and fallback mechanisms",
            "Conduct adversarial testing and red team exercises",
            "Establish human-in-the-loop processes for high-stakes decisions",
            "Create incident response and rollback procedures"
        ]
    },
    "privacy_security": {
        "title": "Privacy & Security",
        "description": "AI systems should be secure and respect privacy throughout their lifecycle.",
        "key_questions": [
            "What data is collected and how is it used?",
            "How is sensitive data protected?",
            "Who has access to the data and model?",
            "How long is data retained?"
        ],
        "best_practices": [
            "Apply data minimization principles - collect only what's needed",
            "Implement encryption for data at rest and in transit",
            "Use differential privacy techniques when appropriate",
            "Conduct regular security assessments and penetration testing",
            "Establish clear data retention and deletion policies"
        ]
    },
    "inclusiveness": {
        "title": "Inclusiveness",
        "description": "AI systems should empower everyone and engage people, including those with disabilities.",
        "key_questions": [
            "Does the system work for users with different abilities?",
            "Are there language or cultural barriers?",
            "How accessible is the system's interface?",
            "Who might be excluded by design choices?"
        ],
        "best_practices": [
            "Follow accessibility standards (WCAG) in interface design",
            "Test with diverse user groups including people with disabilities",
            "Support multiple languages and cultural contexts where appropriate",
            "Avoid requiring capabilities that exclude potential users",
            "Gather feedback from underrepresented groups"
        ]
    },
    "transparency": {
        "title": "Transparency",
        "description": "AI systems should be understandable, with clear documentation of capabilities and limitations.",
        "key_questions": [
            "Do users know they're interacting with AI?",
            "Can decisions be explained?",
            "Are limitations clearly documented?",
            "How is the system's behavior logged?"
        ],
        "best_practices": [
            "Clearly disclose AI involvement to users",
            "Provide explanations for AI-driven decisions when appropriate",
            "Maintain comprehensive documentation (model cards, datasheets)",
            "Log system behavior for auditability",
            "Communicate known limitations to stakeholders"
        ]
    },
    "accountability": {
        "title": "Accountability",
        "description": "People should be accountable for AI systems, with clear governance and oversight.",
        "key_questions": [
            "Who is responsible for the system's behavior?",
            "What governance processes are in place?",
            "How are concerns escalated and addressed?",
            "What mechanisms exist for feedback and redress?"
        ],
        "best_practices": [
            "Establish clear ownership and accountability chains",
            "Implement governance review processes before deployment",
            "Create mechanisms for users to report issues and seek redress",
            "Maintain audit trails of decisions and changes",
            "Conduct regular reviews and impact assessments"
        ]
    }
}

def generate_recommendations_with_ai(project_data, is_advanced=False):
    """Generate recommendations using Azure OpenAI with Managed Identity."""
    if not client:
        # Fallback to static recommendations if no Azure OpenAI configured
        return generate_recommendations_static(project_data)
    
    try:
        # Build the user prompt with project details
        if is_advanced:
            user_prompt = build_advanced_prompt(project_data)
        else:
            user_prompt = build_full_prompt(
                project_name=project_data.get("project_name", "Unknown Project"),
                project_description=project_data.get("project_description", ""),
                deployment_stage=project_data.get("deployment_stage", "Development"),
                technology_type=project_data.get("technology_type", "Not specified"),
                industry=project_data.get("industry", "Not specified"),
                target_users=project_data.get("target_users", "Not specified"),
                data_types=project_data.get("data_types", "Not specified"),
                additional_context=project_data.get("additional_context", "")
            )
        
        # Call Azure OpenAI using the deployment name
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,  # This is the deployment name in Azure
            temperature=OPENAI_CONFIG["temperature"],
            max_tokens=OPENAI_CONFIG["max_tokens"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        ai_response = json.loads(response.choices[0].message.content)
        return ai_response
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to static recommendations
        return {"error": str(e), "fallback": True, "recommendations": generate_recommendations_static(project_data)}


def build_advanced_prompt(project_data):
    """Build a comprehensive prompt from the advanced review questionnaire."""
    sections = []
    
    # Project Overview
    sections.append(f"""## Project Overview
- **Project Name**: {project_data.get('project_name', 'Not provided')}
- **Deployment Stage**: {project_data.get('deployment_stage', 'Not specified')}""")
    
    # Purpose & Use Case
    if any(project_data.get(f) for f in ['intended_purpose', 'business_problem', 'end_users']):
        sections.append(f"""## Purpose & Use Case
- **Intended Purpose**: {project_data.get('intended_purpose', 'Not provided')}
- **Business Problem**: {project_data.get('business_problem', 'Not provided')}
- **End Users**: {project_data.get('end_users', 'Not provided')}""")
    
    # Data & Inputs
    if any(project_data.get(f) for f in ['data_sources', 'data_collection_storage', 'sensitive_data']):
        sections.append(f"""## Data & Inputs
- **Data Sources**: {project_data.get('data_sources', 'Not provided')}
- **Data Collection, Storage & Processing**: {project_data.get('data_collection_storage', 'Not provided')}
- **Sensitive/Personal Data**: {project_data.get('sensitive_data', 'Not provided')}""")
    
    # Model & Technology
    if any(project_data.get(f) for f in ['ai_models', 'model_type', 'environments_connectors']):
        sections.append(f"""## Model & Technology
- **AI Models/Techniques**: {project_data.get('ai_models', 'Not provided')}
- **Model Type**: {project_data.get('model_type', 'Not specified')}
- **Environments & Connectors**: {project_data.get('environments_connectors', 'Not provided')}""")
    
    # Fairness & Bias
    if any(project_data.get(f) for f in ['bias_checking', 'bias_mitigation']):
        sections.append(f"""## Fairness & Bias
- **Bias Detection Methods**: {project_data.get('bias_checking', 'Not provided')}
- **Mitigation Strategies**: {project_data.get('bias_mitigation', 'Not provided')}""")
    
    # Transparency & Explainability
    if any(project_data.get(f) for f in ['decision_explainability', 'output_documentation']):
        sections.append(f"""## Transparency & Explainability
- **Decision Explainability**: {project_data.get('decision_explainability', 'Not provided')}
- **Output Documentation**: {project_data.get('output_documentation', 'Not provided')}""")
    
    # Accountability & Governance
    if any(project_data.get(f) for f in ['system_ownership', 'escalation_paths']):
        sections.append(f"""## Accountability & Governance
- **System Ownership**: {project_data.get('system_ownership', 'Not provided')}
- **Escalation Paths**: {project_data.get('escalation_paths', 'Not provided')}""")
    
    # Security & Privacy
    if any(project_data.get(f) for f in ['data_security', 'privacy_compliance']):
        sections.append(f"""## Security & Privacy
- **Data Security**: {project_data.get('data_security', 'Not provided')}
- **Privacy Compliance**: {project_data.get('privacy_compliance', 'Not provided')}""")
    
    # Impact & Risk
    if any(project_data.get(f) for f in ['potential_risks', 'risk_monitoring']):
        sections.append(f"""## Impact & Risk
- **Potential Risks**: {project_data.get('potential_risks', 'Not provided')}
- **Risk Monitoring & Mitigation**: {project_data.get('risk_monitoring', 'Not provided')}""")
    
    # User Interaction
    if any(project_data.get(f) for f in ['user_interaction_method', 'human_in_loop']):
        sections.append(f"""## User Interaction
- **Interaction Method**: {project_data.get('user_interaction_method', 'Not specified')}
- **Human-in-the-Loop**: {project_data.get('human_in_loop', 'Not specified')}""")
    
    full_prompt = f"""# Comprehensive Responsible AI Review Request

This is a DETAILED review submission with comprehensive information provided across all RAI dimensions. Please provide thorough, specific recommendations based on the detailed information provided.

{''.join(sections)}

---

Based on this comprehensive information, please provide:
1. An overall assessment considering ALL the information provided
2. Specific recommendations that address gaps identified in each section
3. Prioritized action items based on the deployment stage and risks identified
4. Recommended Microsoft tools with official documentation links

Focus on actionable, specific recommendations rather than generic advice since detailed context has been provided."""

    return full_prompt

def generate_recommendations_static(project_data):
    """Static recommendations as fallback when OpenAI is not available."""
    project_name = project_data.get("project_name", "Unknown Project")
    deployment_stage = project_data.get("deployment_stage", "Development")
    project_description = project_data.get("project_description", "")
    
    # Detect if this is an LLM/GenAI project
    is_llm_project = any(keyword in project_description.lower() for keyword in 
        ["llm", "gpt", "chatbot", "generative", "language model", "openai", "copilot", "assistant"])
    
    recommendations = []
    
    # Fairness recommendations
    fairness_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["fairness"]["title"],
        "priority": "High",
        "description": MICROSOFT_RAI_PRINCIPLES["fairness"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["fairness"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["fairness"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["fairness"]
    }
    recommendations.append(fairness_rec)
    
    # Reliability & Safety recommendations
    safety_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["title"],
        "priority": "Critical",
        "description": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["reliability_safety"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["safety"]
    }
    recommendations.append(safety_rec)
    
    # Privacy & Security recommendations
    privacy_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["title"],
        "priority": "High",
        "description": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["privacy_security"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["privacy"] + MICROSOFT_RAI_TOOLS["security"]
    }
    recommendations.append(privacy_rec)
    
    # Inclusiveness recommendations
    inclusiveness_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["title"],
        "priority": "Medium",
        "description": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["inclusiveness"]["best_practices"],
        "tools": []  # Inclusiveness is more about process than tools
    }
    recommendations.append(inclusiveness_rec)
    
    # Transparency recommendations
    transparency_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["transparency"]["title"],
        "priority": "High",
        "description": MICROSOFT_RAI_PRINCIPLES["transparency"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["transparency"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["transparency"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["transparency"]
    }
    recommendations.append(transparency_rec)
    
    # Accountability recommendations
    accountability_rec = {
        "principle": MICROSOFT_RAI_PRINCIPLES["accountability"]["title"],
        "priority": "Medium",
        "description": MICROSOFT_RAI_PRINCIPLES["accountability"]["description"],
        "key_questions": MICROSOFT_RAI_PRINCIPLES["accountability"]["key_questions"],
        "recommendations": MICROSOFT_RAI_PRINCIPLES["accountability"]["best_practices"],
        "tools": MICROSOFT_RAI_TOOLS["accountability"]
    }
    recommendations.append(accountability_rec)
    
    # Add LLM-specific recommendations if applicable
    if is_llm_project:
        llm_rec = {
            "principle": "LLM/Generative AI Specific",
            "priority": "Critical",
            "description": "Additional considerations for Large Language Models and Generative AI systems.",
            "key_questions": [
                "How will you prevent prompt injection attacks?",
                "What content filters are in place for inputs and outputs?",
                "How will you detect and handle hallucinations?",
                "What guardrails prevent harmful content generation?"
            ],
            "recommendations": [
                "Implement Azure AI Content Safety for content moderation",
                "Use Prompt Shields to detect jailbreak attempts",
                "Enable Groundedness Detection to catch hallucinations",
                "Configure appropriate content filtering levels in Azure OpenAI",
                "Implement rate limiting and abuse detection",
                "Use system messages to establish clear AI behavior boundaries",
                "Log and monitor all LLM interactions for quality assurance"
            ],
            "tools": MICROSOFT_RAI_TOOLS["llm_specific"]
        }
        recommendations.insert(1, llm_rec)  # Add after fairness but before others
    
    # Add stage-specific recommendations
    if deployment_stage == "Production":
        production_rec = {
            "principle": "Production Readiness",
            "priority": "Critical",
            "description": "Critical checks before deploying AI systems to production.",
            "key_questions": [
                "Has the system passed all safety evaluations?",
                "Is monitoring and alerting configured?",
                "Are rollback procedures documented and tested?",
                "Have stakeholders signed off on deployment?"
            ],
            "recommendations": [
                "Complete pre-deployment checklist and sign-off",
                "Configure production monitoring with Azure Monitor and Application Insights",
                "Document and test rollback procedures",
                "Establish on-call rotation for incident response",
                "Set up automated alerts for safety and performance metrics",
                "Conduct final security review and penetration testing"
            ],
            "tools": [
                {
                    "name": "Azure Monitor",
                    "url": "https://azure.microsoft.com/products/monitor/",
                    "description": "Full-stack monitoring for applications and infrastructure.",
                    "category": "Monitoring"
                },
                {
                    "name": "Application Insights",
                    "url": "https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview",
                    "description": "Application performance management and monitoring.",
                    "category": "APM"
                }
            ]
        }
        recommendations.append(production_rec)
    elif deployment_stage == "Planning":
        planning_rec = {
            "principle": "Planning Phase",
            "priority": "High",
            "description": "Key considerations during the AI system planning phase.",
            "key_questions": [
                "Is AI the right solution for this problem?",
                "What are the potential harms and benefits?",
                "Who are the stakeholders and affected parties?",
                "What success metrics will be used?"
            ],
            "recommendations": [
                "Conduct a Responsible AI Impact Assessment",
                "Identify and engage key stakeholders early",
                "Define clear success metrics including fairness criteria",
                "Consider alternative non-AI solutions",
                "Document intended use cases and out-of-scope uses",
                "Establish governance and review processes"
            ],
            "tools": [
                {
                    "name": "Microsoft HAX Toolkit",
                    "url": "https://www.microsoft.com/haxtoolkit/",
                    "description": "Human-AI Experience guidelines and design patterns.",
                    "category": "Design"
                },
                {
                    "name": "AI Fairness Checklist",
                    "url": "https://www.microsoft.com/research/project/ai-fairness-checklist/",
                    "description": "Checklist for addressing fairness in AI systems.",
                    "category": "Assessment"
                }
            ]
        }
        recommendations.insert(0, planning_rec)
    
    return recommendations

@app.route("/api/health", methods=["GET"])
def health():
    azure_openai_configured = client is not None
    return jsonify({
        "status": "healthy", 
        "message": "Responsible AI Agent API", 
        "version": "3.0",
        "azure_openai": {
            "enabled": azure_openai_configured,
            "auth_method": auth_method if azure_openai_configured else None,
            "endpoint": AZURE_OPENAI_ENDPOINT if azure_openai_configured else None,
            "deployment": AZURE_OPENAI_DEPLOYMENT if azure_openai_configured else None
        }
    })

@app.route("/api/submit-review", methods=["POST", "OPTIONS"])
def submit_review():
    if request.method == "OPTIONS":
        return jsonify({})
    
    try:
        project_data = request.get_json() or {}
        
        # Use AI-powered recommendations if available
        if client:
            ai_response = generate_recommendations_with_ai(project_data, is_advanced=False)
            
            # If we got a proper AI response, use it
            if "recommendations" in ai_response and not ai_response.get("fallback"):
                return jsonify({
                    "submission_id": str(uuid.uuid4()),
                    "project_name": project_data.get("project_name", "Unknown"),
                    "ai_powered": True,
                    **ai_response
                })
        
        # Fallback to static recommendations
        recommendations = generate_recommendations_static(project_data)
        
        response_data = {
            "submission_id": str(uuid.uuid4()),
            "project_name": project_data.get("project_name", "Unknown"),
            "recommendations": recommendations,
            "status": "completed",
            "summary": {
                "total_recommendations": len(recommendations),
                "critical_items": sum(1 for r in recommendations if r["priority"] == "Critical"),
                "high_priority_items": sum(1 for r in recommendations if r["priority"] == "High")
            },
            "microsoft_rai_resources": {
                "overview": "https://www.microsoft.com/ai/responsible-ai",
                "standards": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai",
                "tools": "https://www.microsoft.com/ai/tools-practices"
            }
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/submit-advanced-review", methods=["POST", "OPTIONS"])
def submit_advanced_review():
    """Handle comprehensive/advanced review submissions with detailed questionnaire data."""
    if request.method == "OPTIONS":
        return jsonify({})
    
    try:
        project_data = request.get_json() or {}
        
        # Use AI-powered recommendations if available
        if client:
            ai_response = generate_recommendations_with_ai(project_data, is_advanced=True)
            
            # If we got a proper AI response, use it
            if "recommendations" in ai_response and not ai_response.get("fallback"):
                return jsonify({
                    "submission_id": str(uuid.uuid4()),
                    "project_name": project_data.get("project_name", "Unknown"),
                    "ai_powered": True,
                    "review_type": "comprehensive",
                    **ai_response
                })
        
        # Fallback to static recommendations
        recommendations = generate_recommendations_static(project_data)
        
        response_data = {
            "submission_id": str(uuid.uuid4()),
            "project_name": project_data.get("project_name", "Unknown"),
            "review_type": "comprehensive",
            "recommendations": recommendations,
            "status": "completed",
            "summary": {
                "total_recommendations": len(recommendations),
                "critical_items": sum(1 for r in recommendations if r["priority"] == "Critical"),
                "high_priority_items": sum(1 for r in recommendations if r["priority"] == "High")
            },
            "microsoft_rai_resources": {
                "overview": "https://www.microsoft.com/ai/responsible-ai",
                "standards": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai",
                "tools": "https://www.microsoft.com/ai/tools-practices"
            }
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools", methods=["GET"])
def get_tools():
    """Return all available Microsoft RAI tools organized by category."""
    return jsonify({
        "tools": MICROSOFT_RAI_TOOLS,
        "principles": {k: {"title": v["title"], "description": v["description"]} 
                      for k, v in MICROSOFT_RAI_PRINCIPLES.items()}
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
