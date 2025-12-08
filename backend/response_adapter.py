"""
Response Adapter Module

This module provides adaptive response generation based on input completeness.
It determines the appropriate response depth and structures recommendations
to balance risk mitigation with innovation enablement.

Version: 1.0.0
Created: December 2025
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ResponseDepth(Enum):
    """Response depth levels based on input completeness."""
    MINIMAL = "minimal"      # Only project name/description - Quick guidance
    BASIC = "basic"          # + deployment stage - Reference architectures
    STANDARD = "standard"    # + technology/industry - Full analysis
    COMPREHENSIVE = "comprehensive"  # All fields - Deep dive with custom roadmap


class Priority(Enum):
    """Priority levels aligned with catalog quick_reference."""
    CRITICAL_BLOCKER = "CRITICAL_BLOCKER"
    HIGHLY_RECOMMENDED = "HIGHLY_RECOMMENDED"
    RECOMMENDED = "RECOMMENDED"
    NICE_TO_HAVE = "NICE_TO_HAVE"

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()
    
    @property
    def icon(self) -> str:
        icons = {
            "CRITICAL_BLOCKER": "🚫",
            "HIGHLY_RECOMMENDED": "⚠️",
            "RECOMMENDED": "✅",
            "NICE_TO_HAVE": "💡"
        }
        return icons.get(self.value, "•")


class InputAssessor:
    """
    Assesses input completeness and determines appropriate response depth.
    """
    
    # Field weights for completeness scoring
    FIELD_WEIGHTS = {
        # Core fields (required for any review)
        "project_name": 10,
        "project_description": 15,
        
        # Basic context fields
        "deployment_stage": 10,
        "technology_type": 10,
        "industry": 10,
        
        # Detailed fields
        "target_users": 8,
        "data_types": 8,
        "additional_context": 5,
        
        # Advanced review fields
        "intended_purpose": 8,
        "business_problem": 5,
        "end_users": 5,
        "data_sources": 5,
        "data_collection_storage": 5,
        "sensitive_data": 8,
        "ai_models": 5,
        "model_type": 5,
        "environments_connectors": 3,
        "bias_checking": 5,
        "bias_mitigation": 5,
        "decision_explainability": 5,
        "output_documentation": 3,
        "system_ownership": 5,
        "escalation_paths": 3,
        "data_security": 5,
        "privacy_compliance": 5,
        "potential_risks": 8,
        "risk_monitoring": 5,
        "user_interaction_method": 3,
        "human_in_loop": 5
    }
    
    # Thresholds for response depth
    DEPTH_THRESHOLDS = {
        ResponseDepth.MINIMAL: 0,
        ResponseDepth.BASIC: 25,
        ResponseDepth.STANDARD: 50,
        ResponseDepth.COMPREHENSIVE: 75
    }
    
    @classmethod
    def assess_input(cls, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the completeness of input data and determine response depth.
        
        Returns:
            Dict containing:
            - completeness_score: 0-100
            - response_depth: ResponseDepth enum
            - provided_fields: List of fields that have values
            - missing_critical: List of critical missing fields
            - suggestions: Fields that would improve the analysis
        """
        provided_fields = []
        missing_fields = []
        total_weight = sum(cls.FIELD_WEIGHTS.values())
        achieved_weight = 0
        
        for field, weight in cls.FIELD_WEIGHTS.items():
            value = project_data.get(field, "")
            if value and str(value).strip() and str(value).lower() not in ["not specified", "not provided", "n/a", "none"]:
                provided_fields.append(field)
                achieved_weight += weight
            else:
                missing_fields.append(field)
        
        completeness_score = round((achieved_weight / total_weight) * 100)
        
        # Determine response depth
        response_depth = ResponseDepth.MINIMAL
        for depth, threshold in sorted(cls.DEPTH_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if completeness_score >= threshold:
                response_depth = depth
                break
        
        # Identify critical missing fields
        critical_fields = ["project_name", "project_description"]
        missing_critical = [f for f in critical_fields if f in missing_fields]
        
        # Suggest fields that would most improve the analysis
        high_value_missing = [
            f for f in missing_fields 
            if cls.FIELD_WEIGHTS.get(f, 0) >= 8
        ][:5]  # Top 5 suggestions
        
        return {
            "completeness_score": completeness_score,
            "response_depth": response_depth,
            "provided_fields": provided_fields,
            "missing_critical": missing_critical,
            "suggestions": high_value_missing,
            "field_count": len(provided_fields),
            "total_fields": len(cls.FIELD_WEIGHTS)
        }
    
    @classmethod
    def detect_project_type(cls, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect the project type from description and technology fields.
        
        Returns:
            Dict with detected project characteristics
        """
        description = str(project_data.get("project_description", "")).lower()
        tech_type = str(project_data.get("technology_type", "")).lower()
        ai_models = str(project_data.get("ai_models", "")).lower()
        combined = f"{description} {tech_type} {ai_models}"
        
        # Detection patterns
        patterns = {
            "is_llm_project": [
                "llm", "gpt", "chatbot", "generative", "language model", 
                "openai", "copilot", "assistant", "claude", "gemini",
                "rag", "retrieval", "prompt", "chat"
            ],
            "is_agent_project": [
                "agent", "autonomous", "multi-agent", "agentic", "orchestrat",
                "tool use", "function calling", "reasoning"
            ],
            "is_ml_project": [
                "machine learning", "ml", "classification", "regression",
                "prediction", "forecast", "clustering", "neural network",
                "deep learning", "training", "model"
            ],
            "is_vision_project": [
                "vision", "image", "video", "computer vision", "ocr",
                "object detection", "face", "recognition"
            ],
            "is_document_project": [
                "document", "pdf", "form", "extract", "invoice",
                "receipt", "contract"
            ],
            "handles_pii": [
                "personal", "pii", "customer data", "user data",
                "health", "financial", "ssn", "email", "phone",
                "address", "name", "hipaa", "gdpr"
            ],
            "is_high_risk": [
                "healthcare", "medical", "diagnosis", "treatment",
                "financial", "credit", "loan", "hr", "hiring",
                "recruitment", "law enforcement", "legal", "education",
                "grading", "assessment"
            ],
            "is_customer_facing": [
                "customer", "user-facing", "public", "consumer",
                "external", "client", "end user"
            ]
        }
        
        detected = {}
        for category, keywords in patterns.items():
            detected[category] = any(kw in combined for kw in keywords)
        
        # Determine primary project type
        if detected["is_agent_project"]:
            detected["primary_type"] = "AI Agent"
        elif detected["is_llm_project"]:
            detected["primary_type"] = "LLM/Generative AI"
        elif detected["is_vision_project"]:
            detected["primary_type"] = "Computer Vision"
        elif detected["is_document_project"]:
            detected["primary_type"] = "Document Intelligence"
        elif detected["is_ml_project"]:
            detected["primary_type"] = "Traditional ML"
        else:
            detected["primary_type"] = "General AI"
        
        return detected


class ResponseBuilder:
    """
    Builds adaptive responses based on input assessment and project characteristics.
    """
    
    # Response templates for different depths
    DEPTH_TEMPLATES = {
        ResponseDepth.MINIMAL: {
            "mode": "quick_guidance",
            "title": "Quick Guidance",
            "description": "Based on the limited information provided, here's quick guidance to get started.",
            "sections": ["quick_start", "reference_architecture", "essential_tools", "next_steps"],
            "recommendation_limit": 5,
            "include_code_snippets": False,
            "include_cost_estimates": False
        },
        ResponseDepth.BASIC: {
            "mode": "quick_scan",
            "title": "Quick Scan Review",
            "description": "Reference architectures and starter guidance based on your project context.",
            "sections": ["risk_overview", "reference_architecture", "starter_tools", "30_day_roadmap", "next_steps"],
            "recommendation_limit": 8,
            "include_code_snippets": True,
            "include_cost_estimates": False
        },
        ResponseDepth.STANDARD: {
            "mode": "standard_review",
            "title": "Standard Review",
            "description": "Comprehensive analysis across all RAI principles with specific tool recommendations.",
            "sections": ["risk_scores", "eu_ai_act", "principle_analysis", "tools", "implementation_timeline", "next_steps"],
            "recommendation_limit": 12,
            "include_code_snippets": True,
            "include_cost_estimates": True
        },
        ResponseDepth.COMPREHENSIVE: {
            "mode": "deep_dive",
            "title": "Deep Dive Review",
            "description": "Exhaustive analysis with custom implementation roadmap and detailed guidance.",
            "sections": ["all"],
            "recommendation_limit": None,  # No limit
            "include_code_snippets": True,
            "include_cost_estimates": True
        }
    }
    
    # Innovation-enabling language patterns
    ENABLEMENT_MESSAGES = {
        "header": "🚀 Enabling Responsible Innovation",
        "principles": [
            "Responsible AI accelerates adoption by building trust and reducing risk",
            "Early RAI integration prevents costly rework and deployment delays",
            "Good AI governance enables faster time-to-market with confidence",
            "RAI tools automate compliance, freeing teams to focus on innovation"
        ],
        "value_propositions": {
            "fairness": "Fair AI systems reach broader markets and build lasting customer trust",
            "safety": "Safe AI reduces incident response costs and protects brand reputation",
            "privacy": "Privacy-first design simplifies global compliance (GDPR, CCPA, etc.)",
            "transparency": "Explainable AI accelerates stakeholder buy-in and user adoption",
            "accountability": "Clear governance prevents project delays and leadership concerns",
            "inclusiveness": "Inclusive AI expands your addressable market and user satisfaction"
        }
    }
    
    @classmethod
    def build_response_config(
        cls, 
        input_assessment: Dict[str, Any],
        project_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build the response configuration based on assessment results.
        """
        depth = input_assessment["response_depth"]
        template = cls.DEPTH_TEMPLATES[depth]
        
        config = {
            "response_depth": depth.value,
            "review_mode": template["mode"],
            "title": template["title"],
            "description": template["description"],
            "completeness_score": input_assessment["completeness_score"],
            "sections_to_include": template["sections"],
            "recommendation_limit": template["recommendation_limit"],
            "include_code_snippets": template["include_code_snippets"],
            "include_cost_estimates": template["include_cost_estimates"],
            "project_type": project_characteristics.get("primary_type", "General AI"),
            "is_llm_project": project_characteristics.get("is_llm_project", False),
            "is_agent_project": project_characteristics.get("is_agent_project", False),
            "is_high_risk": project_characteristics.get("is_high_risk", False),
            "handles_pii": project_characteristics.get("handles_pii", False),
            "suggestions_for_better_review": input_assessment.get("suggestions", [])
        }
        
        # Add enablement messaging
        config["enablement_message"] = cls._get_enablement_message(project_characteristics)
        
        return config
    
    @classmethod
    def _get_enablement_message(cls, characteristics: Dict[str, Any]) -> str:
        """Generate an innovation-enabling message based on project type."""
        messages = [cls.ENABLEMENT_MESSAGES["header"]]
        messages.append("")
        
        # Add relevant principle value propositions
        if characteristics.get("is_customer_facing"):
            messages.append(f"• {cls.ENABLEMENT_MESSAGES['value_propositions']['fairness']}")
        if characteristics.get("is_llm_project") or characteristics.get("is_agent_project"):
            messages.append(f"• {cls.ENABLEMENT_MESSAGES['value_propositions']['safety']}")
        if characteristics.get("handles_pii"):
            messages.append(f"• {cls.ENABLEMENT_MESSAGES['value_propositions']['privacy']}")
        if characteristics.get("is_high_risk"):
            messages.append(f"• {cls.ENABLEMENT_MESSAGES['value_propositions']['transparency']}")
        
        # Always add a general enablement message
        messages.append("")
        messages.append(cls.ENABLEMENT_MESSAGES["principles"][0])
        
        return "\n".join(messages)


class PriorityMapper:
    """
    Maps recommendations to priority levels based on project context and risk.
    """
    
    # Risk-to-priority mapping from catalog quick_reference
    RISK_PRIORITY_MAP = {
        # Critical blockers - must address before production
        "prompt_injection_jailbreak": Priority.CRITICAL_BLOCKER,
        "harmful_content_generation": Priority.CRITICAL_BLOCKER,
        "pii_data_exposure": Priority.CRITICAL_BLOCKER,
        "unauthorized_actions": Priority.CRITICAL_BLOCKER,
        
        # Highly recommended - strongly encouraged
        "hallucination_grounding": Priority.HIGHLY_RECOMMENDED,
        "bias_discrimination": Priority.HIGHLY_RECOMMENDED,
        "model_reliability": Priority.HIGHLY_RECOMMENDED,
        "excessive_agency": Priority.HIGHLY_RECOMMENDED,
        
        # Recommended - best practice
        "lack_of_explainability": Priority.RECOMMENDED,
        "insufficient_monitoring": Priority.RECOMMENDED,
        "accessibility_gaps": Priority.RECOMMENDED,
        
        # Nice to have - optimization
        "cost_optimization": Priority.NICE_TO_HAVE,
        "performance_tuning": Priority.NICE_TO_HAVE
    }
    
    # Context-based priority escalation
    ESCALATION_RULES = {
        "is_high_risk": {
            Priority.RECOMMENDED: Priority.HIGHLY_RECOMMENDED,
            Priority.NICE_TO_HAVE: Priority.RECOMMENDED
        },
        "production_stage": {
            Priority.HIGHLY_RECOMMENDED: Priority.CRITICAL_BLOCKER,
            Priority.RECOMMENDED: Priority.HIGHLY_RECOMMENDED
        },
        "handles_pii": {
            "pii_data_exposure": Priority.CRITICAL_BLOCKER,
            "lack_of_explainability": Priority.HIGHLY_RECOMMENDED
        }
    }
    
    @classmethod
    def get_priority(
        cls, 
        risk_type: str, 
        project_characteristics: Dict[str, Any],
        deployment_stage: str = "Development"
    ) -> Priority:
        """
        Determine the priority level for a given risk type based on project context.
        """
        base_priority = cls.RISK_PRIORITY_MAP.get(risk_type, Priority.RECOMMENDED)
        
        # Apply escalation rules
        if project_characteristics.get("is_high_risk"):
            escalation = cls.ESCALATION_RULES["is_high_risk"]
            base_priority = escalation.get(base_priority, base_priority)
        
        if deployment_stage.lower() == "production":
            escalation = cls.ESCALATION_RULES["production_stage"]
            base_priority = escalation.get(base_priority, base_priority)
        
        # Check for specific risk escalations
        if project_characteristics.get("handles_pii"):
            pii_rules = cls.ESCALATION_RULES["handles_pii"]
            if risk_type in pii_rules:
                base_priority = pii_rules[risk_type]
        
        return base_priority
    
    @classmethod
    def format_priority_badge(cls, priority: Priority) -> str:
        """Format a priority as a display badge."""
        return f"{priority.icon} {priority.display_name}"
    
    @classmethod
    def get_priority_description(cls, priority: Priority) -> str:
        """Get a description of what this priority level means."""
        descriptions = {
            Priority.CRITICAL_BLOCKER: "Must be addressed before production deployment. Non-negotiable for responsible AI.",
            Priority.HIGHLY_RECOMMENDED: "Strongly recommended for production readiness. Significant risk if not addressed.",
            Priority.RECOMMENDED: "Best practice that improves RAI posture. Should be part of the roadmap.",
            Priority.NICE_TO_HAVE: "Enhancement that optimizes the system. Can be prioritized based on resources."
        }
        return descriptions.get(priority, "")


def assess_and_configure(project_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Main entry point: Assess input and return response configuration.
    
    Args:
        project_data: The project data from the review request
        
    Returns:
        Tuple of (input_assessment, response_config)
    """
    # Assess input completeness
    input_assessment = InputAssessor.assess_input(project_data)
    
    # Detect project characteristics
    project_characteristics = InputAssessor.detect_project_type(project_data)
    
    # Build response configuration
    response_config = ResponseBuilder.build_response_config(
        input_assessment, 
        project_characteristics
    )
    
    # Add deployment stage context
    deployment_stage = project_data.get("deployment_stage", "Development")
    response_config["deployment_stage"] = deployment_stage
    
    logger.info(
        f"Input assessed: depth={response_config['response_depth']}, "
        f"completeness={input_assessment['completeness_score']}%, "
        f"type={response_config['project_type']}"
    )
    
    return input_assessment, response_config


# =============================================================================
# CLI Testing
# =============================================================================

if __name__ == "__main__":
    # Test with different input levels
    test_cases = [
        {
            "name": "Minimal Input",
            "data": {
                "project_name": "Customer Chatbot"
            }
        },
        {
            "name": "Basic Input",
            "data": {
                "project_name": "Customer Chatbot",
                "project_description": "An AI chatbot for customer support",
                "deployment_stage": "Development"
            }
        },
        {
            "name": "Standard Input",
            "data": {
                "project_name": "Customer Chatbot",
                "project_description": "An LLM-powered chatbot using GPT-4 for customer support",
                "deployment_stage": "Testing",
                "technology_type": "LLM/Generative AI",
                "industry": "Retail"
            }
        },
        {
            "name": "Comprehensive Input",
            "data": {
                "project_name": "Healthcare Assistant",
                "project_description": "An AI agent that helps healthcare providers with patient documentation",
                "deployment_stage": "Production",
                "technology_type": "AI Agent",
                "industry": "Healthcare",
                "target_users": "Healthcare providers, doctors, nurses",
                "data_types": "Patient records, medical notes, PHI",
                "sensitive_data": "Yes - PHI, patient names, diagnoses",
                "potential_risks": "Incorrect medical advice, privacy breaches",
                "human_in_loop": "Required for all medical recommendations"
            }
        }
    ]
    
    print("=" * 70)
    print("Response Adapter Test Results")
    print("=" * 70)
    
    for test in test_cases:
        print(f"\n{'='*50}")
        print(f"Test: {test['name']}")
        print(f"{'='*50}")
        
        assessment, config = assess_and_configure(test["data"])
        
        print(f"Completeness Score: {assessment['completeness_score']}%")
        print(f"Response Depth: {config['response_depth']}")
        print(f"Review Mode: {config['review_mode']}")
        print(f"Project Type: {config['project_type']}")
        print(f"Is LLM: {config['is_llm_project']}")
        print(f"Is Agent: {config['is_agent_project']}")
        print(f"Is High Risk: {config['is_high_risk']}")
        print(f"Handles PII: {config['handles_pii']}")
        print(f"Recommendation Limit: {config['recommendation_limit']}")
        
        if assessment['suggestions']:
            print(f"Suggestions for better review: {', '.join(assessment['suggestions'][:3])}")
        
        print(f"\nEnablement Message:\n{config['enablement_message']}")
