"""
Catalog Integration Module

This module provides integration between the RAI tools catalog and the
adaptive recommendation system. It handles priority-based tool selection
and dynamic tool injection based on project context.

Version: 1.0.0
Created: December 2025
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import knowledge loader
try:
    from knowledge_loader import get_knowledge_loader
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False


class CatalogIntegration:
    """
    Provides integration with the RAI tools catalog for priority-based
    tool recommendations.
    """
    
    # Map of risk types to priority levels (from quick_reference)
    RISK_PRIORITIES = {
        # Critical Blockers
        "prompt_injection_jailbreak": "CRITICAL_BLOCKER",
        "harmful_content_generation": "CRITICAL_BLOCKER",
        "pii_data_exposure": "CRITICAL_BLOCKER",
        "unauthorized_actions": "CRITICAL_BLOCKER",
        
        # Highly Recommended
        "hallucination_grounding": "HIGHLY_RECOMMENDED",
        "bias_discrimination": "HIGHLY_RECOMMENDED",
        "model_reliability": "HIGHLY_RECOMMENDED",
        "excessive_agency": "HIGHLY_RECOMMENDED",
        
        # Recommended
        "lack_of_explainability": "RECOMMENDED",
        "insufficient_monitoring": "RECOMMENDED",
        "accessibility_gaps": "RECOMMENDED",
        
        # Nice to Have
        "performance_optimization": "NICE_TO_HAVE",
        "cost_optimization": "NICE_TO_HAVE"
    }
    
    # Tool to risk mapping (which risks each tool addresses)
    TOOL_RISK_MAP = {
        "Azure AI Content Safety": ["harmful_content_generation", "prompt_injection_jailbreak"],
        "Prompt Shields": ["prompt_injection_jailbreak"],
        "Groundedness Detection": ["hallucination_grounding"],
        "Presidio": ["pii_data_exposure"],
        "Fairlearn": ["bias_discrimination"],
        "InterpretML": ["lack_of_explainability", "bias_discrimination"],
        "Microsoft Foundry Control Plane": ["unauthorized_actions", "excessive_agency"],
        "Entra Agent ID": ["unauthorized_actions"],
        "Azure AI Evaluation SDK": ["model_reliability", "hallucination_grounding"],
        "PyRIT": ["prompt_injection_jailbreak", "unauthorized_actions"],
        "Azure Monitor": ["insufficient_monitoring"],
        "HAX Toolkit": ["accessibility_gaps", "lack_of_explainability"]
    }
    
    @classmethod
    def get_loader(cls):
        """Get the knowledge loader instance."""
        if KNOWLEDGE_AVAILABLE:
            return get_knowledge_loader()
        return None
    
    @classmethod
    def get_tools_for_project_type(
        cls,
        project_type: str,
        is_llm: bool = False,
        is_agent: bool = False,
        handles_pii: bool = False,
        is_high_risk: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get recommended tools based on project characteristics.
        
        Returns a list of tools with their priorities.
        """
        loader = cls.get_loader()
        if not loader:
            return cls._get_fallback_tools(is_llm, is_agent, handles_pii, is_high_risk)
        
        tools = []
        
        # Get tools based on use case from catalog
        uc_rec = loader.get_use_case_recommendation(project_type)
        if uc_rec:
            for tool_name in uc_rec.get("required_tools", []):
                tool_info = loader.get_tool_info(tool_name)
                if tool_info:
                    priority = cls._get_tool_priority(tool_name, is_high_risk, "Production")
                    tools.append({
                        **tool_info,
                        "priority": priority,
                        "required": True
                    })
            
            for tool_name in uc_rec.get("recommended_evaluators", []):
                tool_info = loader.get_tool_info(tool_name)
                if tool_info:
                    tools.append({
                        **tool_info,
                        "priority": "RECOMMENDED",
                        "required": False
                    })
        
        # Add context-specific tools
        if is_llm:
            cls._add_llm_tools(tools, loader)
        
        if is_agent:
            cls._add_agent_tools(tools, loader)
        
        if handles_pii:
            cls._add_pii_tools(tools, loader)
        
        # Sort by priority
        priority_order = ["CRITICAL_BLOCKER", "HIGHLY_RECOMMENDED", "RECOMMENDED", "NICE_TO_HAVE"]
        tools.sort(key=lambda x: priority_order.index(x.get("priority", "RECOMMENDED")))
        
        # Remove duplicates (keep highest priority)
        seen = set()
        unique_tools = []
        for tool in tools:
            name = tool.get("name")
            if name not in seen:
                seen.add(name)
                unique_tools.append(tool)
        
        return unique_tools
    
    @classmethod
    def _add_llm_tools(cls, tools: List[Dict], loader) -> None:
        """Add LLM-specific tools with correct priorities."""
        llm_required = [
            ("Azure AI Content Safety", "CRITICAL_BLOCKER"),
            ("Prompt Shields", "CRITICAL_BLOCKER"),
            ("Groundedness Detection", "HIGHLY_RECOMMENDED"),
            ("Azure AI Evaluation SDK", "HIGHLY_RECOMMENDED")
        ]
        
        for tool_name, priority in llm_required:
            tool_info = loader.get_tool_info(tool_name)
            if tool_info:
                tools.append({
                    **tool_info,
                    "priority": priority,
                    "required": priority == "CRITICAL_BLOCKER"
                })
    
    @classmethod
    def _add_agent_tools(cls, tools: List[Dict], loader) -> None:
        """Add agent-specific tools with correct priorities."""
        agent_required = [
            ("Microsoft Foundry Control Plane", "CRITICAL_BLOCKER"),
            ("Entra Agent ID", "CRITICAL_BLOCKER"),
            ("PyRIT", "HIGHLY_RECOMMENDED"),
            ("Azure AI Evaluation SDK", "HIGHLY_RECOMMENDED")
        ]
        
        for tool_name, priority in agent_required:
            tool_info = loader.get_tool_info(tool_name)
            if tool_info:
                tools.append({
                    **tool_info,
                    "priority": priority,
                    "required": priority == "CRITICAL_BLOCKER"
                })
    
    @classmethod
    def _add_pii_tools(cls, tools: List[Dict], loader) -> None:
        """Add PII-handling tools with correct priorities."""
        pii_required = [
            ("Presidio", "CRITICAL_BLOCKER"),
            ("Azure Key Vault", "HIGHLY_RECOMMENDED"),
            ("Azure Confidential Computing", "RECOMMENDED")
        ]
        
        for tool_name, priority in pii_required:
            tool_info = loader.get_tool_info(tool_name)
            if tool_info:
                tools.append({
                    **tool_info,
                    "priority": priority,
                    "required": priority == "CRITICAL_BLOCKER"
                })
    
    @classmethod
    def _get_tool_priority(
        cls, 
        tool_name: str, 
        is_high_risk: bool = False,
        deployment_stage: str = "Development"
    ) -> str:
        """Determine the priority for a tool based on context."""
        # Check what risks this tool addresses
        risks = cls.TOOL_RISK_MAP.get(tool_name, [])
        
        if not risks:
            return "RECOMMENDED"
        
        # Get the highest priority among the risks this tool addresses
        highest_priority = "NICE_TO_HAVE"
        priority_order = ["CRITICAL_BLOCKER", "HIGHLY_RECOMMENDED", "RECOMMENDED", "NICE_TO_HAVE"]
        
        for risk in risks:
            risk_priority = cls.RISK_PRIORITIES.get(risk, "RECOMMENDED")
            if priority_order.index(risk_priority) < priority_order.index(highest_priority):
                highest_priority = risk_priority
        
        # Escalate priority for production or high-risk contexts
        if deployment_stage.lower() == "production":
            if highest_priority == "HIGHLY_RECOMMENDED":
                highest_priority = "CRITICAL_BLOCKER"
            elif highest_priority == "RECOMMENDED":
                highest_priority = "HIGHLY_RECOMMENDED"
        
        if is_high_risk:
            if highest_priority == "RECOMMENDED":
                highest_priority = "HIGHLY_RECOMMENDED"
        
        return highest_priority
    
    @classmethod
    def _get_fallback_tools(
        cls,
        is_llm: bool,
        is_agent: bool,
        handles_pii: bool,
        is_high_risk: bool
    ) -> List[Dict[str, Any]]:
        """Fallback tool list when knowledge loader is not available."""
        tools = []
        
        # Core tools everyone should consider
        tools.append({
            "name": "Azure Machine Learning Responsible AI Dashboard",
            "url": "https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai-dashboard",
            "description": "Unified interface for model debugging, fairness assessment, and interpretability",
            "priority": "HIGHLY_RECOMMENDED",
            "required": False
        })
        
        if is_llm:
            tools.extend([
                {
                    "name": "Azure AI Content Safety",
                    "url": "https://azure.microsoft.com/products/ai-services/ai-content-safety",
                    "description": "Detect and filter harmful content in AI applications",
                    "priority": "CRITICAL_BLOCKER",
                    "required": True
                },
                {
                    "name": "Prompt Shields",
                    "url": "https://learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection",
                    "description": "Protect against jailbreak and prompt injection attacks",
                    "priority": "CRITICAL_BLOCKER",
                    "required": True
                },
                {
                    "name": "Groundedness Detection",
                    "url": "https://learn.microsoft.com/azure/ai-services/content-safety/concepts/groundedness",
                    "description": "Detect hallucinations and ensure responses are grounded",
                    "priority": "HIGHLY_RECOMMENDED",
                    "required": False
                }
            ])
        
        if is_agent:
            tools.extend([
                {
                    "name": "Microsoft Foundry Control Plane",
                    "url": "https://learn.microsoft.com/azure/ai-services/agents/",
                    "description": "Unified governance and observability for AI agents",
                    "priority": "CRITICAL_BLOCKER",
                    "required": True
                },
                {
                    "name": "Entra Agent ID",
                    "url": "https://learn.microsoft.com/azure/ai-services/agents/",
                    "description": "Managed identity for AI agents with audit logging",
                    "priority": "CRITICAL_BLOCKER",
                    "required": True
                }
            ])
        
        if handles_pii:
            tools.append({
                "name": "Presidio",
                "url": "https://microsoft.github.io/presidio/",
                "description": "PII detection and anonymization SDK",
                "priority": "CRITICAL_BLOCKER",
                "required": True
            })
        
        if is_high_risk:
            tools.extend([
                {
                    "name": "Fairlearn",
                    "url": "https://fairlearn.org/",
                    "description": "Fairness assessment and bias mitigation toolkit",
                    "priority": "CRITICAL_BLOCKER" if is_high_risk else "HIGHLY_RECOMMENDED",
                    "required": is_high_risk
                },
                {
                    "name": "InterpretML",
                    "url": "https://interpret.ml/",
                    "description": "Interpretable machine learning and model explanations",
                    "priority": "HIGHLY_RECOMMENDED",
                    "required": False
                }
            ])
        
        return tools
    
    @classmethod
    def get_quick_reference(cls) -> Dict[str, Any]:
        """Get the quick reference data from the catalog."""
        loader = cls.get_loader()
        if not loader:
            return cls._get_fallback_quick_reference()
        
        catalog = loader.tools_catalog
        return catalog.get("quick_reference", {})
    
    @classmethod
    def _get_fallback_quick_reference(cls) -> Dict[str, Any]:
        """Fallback quick reference when catalog not available."""
        return {
            "risk_categories": {
                "prompt_injection_jailbreak": {
                    "priority": "CRITICAL_BLOCKER",
                    "tools": ["Prompt Shields", "Azure AI Content Safety", "PyRIT"]
                },
                "harmful_content_generation": {
                    "priority": "CRITICAL_BLOCKER",
                    "tools": ["Azure AI Content Safety", "Azure OpenAI Content Filtering"]
                },
                "pii_data_exposure": {
                    "priority": "CRITICAL_BLOCKER",
                    "tools": ["Presidio", "Azure Key Vault"]
                },
                "hallucination_grounding": {
                    "priority": "HIGHLY_RECOMMENDED",
                    "tools": ["Groundedness Detection", "Azure AI Evaluation SDK"]
                },
                "bias_discrimination": {
                    "priority": "HIGHLY_RECOMMENDED",
                    "tools": ["Fairlearn", "Azure ML Responsible AI Dashboard"]
                }
            }
        }
    
    @classmethod
    def get_implementation_phases(cls) -> List[Dict[str, Any]]:
        """Get implementation phases from the catalog."""
        loader = cls.get_loader()
        if not loader:
            return cls._get_fallback_phases()
        
        return loader.get_implementation_phases()
    
    @classmethod
    def _get_fallback_phases(cls) -> List[Dict[str, Any]]:
        """Fallback implementation phases."""
        return [
            {
                "phase": 1,
                "name": "Foundation",
                "duration": "Week 1",
                "focus": "Security and Safety",
                "actions": [
                    "Deploy Azure AI Content Safety",
                    "Enable Prompt Shields",
                    "Set up basic monitoring"
                ]
            },
            {
                "phase": 2,
                "name": "Data Protection",
                "duration": "Week 2",
                "focus": "Privacy and Compliance",
                "actions": [
                    "Integrate Presidio for PII detection",
                    "Configure data governance",
                    "Implement access controls"
                ]
            },
            {
                "phase": 3,
                "name": "Quality & Fairness",
                "duration": "Week 3",
                "focus": "Model Quality",
                "actions": [
                    "Set up Fairlearn metrics",
                    "Configure evaluation pipeline",
                    "Implement groundedness checks"
                ]
            },
            {
                "phase": 4,
                "name": "Governance",
                "duration": "Week 4",
                "focus": "Documentation and Monitoring",
                "actions": [
                    "Create model documentation",
                    "Set up production monitoring",
                    "Establish review cadence"
                ]
            }
        ]


def get_catalog_integration() -> CatalogIntegration:
    """Get the catalog integration instance."""
    return CatalogIntegration()


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Catalog Integration Test")
    print("=" * 60)
    
    # Test LLM project tools
    print("\n1. LLM Project Tools:")
    tools = CatalogIntegration.get_tools_for_project_type(
        "LLM/Generative AI",
        is_llm=True,
        is_agent=False,
        handles_pii=True,
        is_high_risk=False
    )
    for tool in tools[:5]:
        print(f"  [{tool.get('priority', 'N/A')}] {tool.get('name')}")
    
    # Test Agent project tools
    print("\n2. Agent Project Tools:")
    tools = CatalogIntegration.get_tools_for_project_type(
        "AI Agent",
        is_llm=True,
        is_agent=True,
        handles_pii=True,
        is_high_risk=True
    )
    for tool in tools[:5]:
        print(f"  [{tool.get('priority', 'N/A')}] {tool.get('name')}")
    
    # Test quick reference
    print("\n3. Quick Reference Categories:")
    quick_ref = CatalogIntegration.get_quick_reference()
    for risk_type in list(quick_ref.get("risk_categories", {}).keys())[:3]:
        print(f"  - {risk_type}")
    
    # Test implementation phases
    print("\n4. Implementation Phases:")
    phases = CatalogIntegration.get_implementation_phases()
    for phase in phases[:2]:
        print(f"  Phase {phase.get('phase', 'N/A')}: {phase.get('name', 'N/A')}")
