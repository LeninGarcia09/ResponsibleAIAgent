"""
Knowledge Loader Module

This module handles loading, validating, and accessing the RAI Agent's
externalized knowledge base. It allows for easy updates without code changes.

Version: 2.0.0
Last Updated: December 2025
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Get the knowledge directory path
KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


class KnowledgeLoader:
    """
    Handles loading and accessing RAI knowledge from external JSON files.
    
    This class provides:
    - Lazy loading of knowledge files
    - Caching for performance
    - Validation of knowledge structure
    - Easy access to specific knowledge categories
    """
    
    def __init__(self, knowledge_dir: Optional[Path] = None):
        self.knowledge_dir = knowledge_dir or KNOWLEDGE_DIR
        self._cache: Dict[str, Any] = {}
        self._load_timestamps: Dict[str, datetime] = {}
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file from the knowledge directory."""
        filepath = self.knowledge_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Knowledge file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._load_timestamps[filename] = datetime.now()
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}
    
    def _get_cached_or_load(self, filename: str, force_reload: bool = False) -> Dict[str, Any]:
        """Get cached data or load from file."""
        if force_reload or filename not in self._cache:
            self._cache[filename] = self._load_json(filename)
        return self._cache[filename]
    
    @property
    def tools_catalog(self) -> Dict[str, Any]:
        """Get the RAI tools catalog."""
        return self._get_cached_or_load("rai_tools_catalog.json")
    
    @property
    def microsoft_references(self) -> Dict[str, Any]:
        """Get Microsoft documentation references."""
        return self._get_cached_or_load("microsoft_references.json")
    
    @property
    def regulatory_frameworks(self) -> Dict[str, Any]:
        """Get regulatory framework information."""
        return self._get_cached_or_load("regulatory_frameworks.json")
    
    @property
    def code_examples(self) -> Dict[str, Any]:
        """Get code examples for RAI tools."""
        return self._get_cached_or_load("code_examples.json")
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        catalog = self.tools_catalog
        
        # Search through all categories
        for category_name, category_data in catalog.get("categories", {}).items():
            for tool in category_data.get("tools", []):
                if tool.get("name", "").lower() == tool_name.lower():
                    return tool
        
        return None
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all tools in a specific category."""
        catalog = self.tools_catalog
        category_data = catalog.get("categories", {}).get(category, {})
        return category_data.get("tools", [])
    
    def get_tools_for_risk(self, risk_type: str) -> List[str]:
        """Get recommended tools for a specific risk type."""
        catalog = self.tools_catalog
        quick_ref = catalog.get("quick_reference", {}).get("tool_by_risk", {})
        return quick_ref.get(risk_type, [])
    
    def get_reference_url(self, category: str, key: str) -> Optional[str]:
        """Get a specific reference URL."""
        refs = self.microsoft_references
        category_data = refs.get(category, {})
        ref = category_data.get(key, {})
        return ref.get("url")
    
    def get_regulation_info(self, regulation: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific regulation."""
        frameworks = self.regulatory_frameworks
        return frameworks.get(regulation)
    
    def get_eu_ai_act_classification(self, category: str) -> Optional[Dict[str, Any]]:
        """Get EU AI Act risk category information."""
        eu_ai_act = self.regulatory_frameworks.get("eu_ai_act", {})
        risk_categories = eu_ai_act.get("risk_categories", {})
        return risk_categories.get(category)
    
    def get_code_example(self, tool: str, example_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific code example."""
        examples = self.code_examples
        tool_examples = examples.get(tool, {}).get("examples", [])
        
        for example in tool_examples:
            if example.get("name") == example_name:
                return example
        
        return None
    
    def get_all_code_examples(self, tool: str) -> List[Dict[str, Any]]:
        """Get all code examples for a tool."""
        examples = self.code_examples
        return examples.get(tool, {}).get("examples", [])
    
    def get_industry_recommendation(self, industry: str) -> Dict[str, Any]:
        """Get tool recommendations for a specific industry."""
        catalog = self.tools_catalog
        framework = catalog.get("client_recommendation_framework", {})
        
        for dimension in framework.get("assessment_dimensions", []):
            if dimension.get("dimension") == "Industry Vertical":
                for ind in dimension.get("industries", []):
                    if ind.get("industry", "").lower() == industry.lower():
                        return ind
        
        return {}
    
    def get_use_case_recommendation(self, use_case: str) -> Dict[str, Any]:
        """Get tool recommendations for a specific use case type."""
        catalog = self.tools_catalog
        framework = catalog.get("client_recommendation_framework", {})
        
        for dimension in framework.get("assessment_dimensions", []):
            if dimension.get("dimension") == "Use Case Type":
                for uc in dimension.get("types", []):
                    if use_case.lower() in uc.get("type", "").lower():
                        return uc
        
        return {}
    
    def get_implementation_phases(self) -> List[Dict[str, Any]]:
        """Get the implementation phases roadmap."""
        catalog = self.tools_catalog
        framework = catalog.get("client_recommendation_framework", {})
        return framework.get("implementation_phases", [])
    
    def reload_all(self) -> None:
        """Force reload all knowledge files."""
        self._cache.clear()
        self._load_timestamps.clear()
        logger.info("All knowledge caches cleared - will reload on next access")
    
    def get_knowledge_status(self) -> Dict[str, Any]:
        """Get status of loaded knowledge files."""
        status = {
            "knowledge_directory": str(self.knowledge_dir),
            "files": {}
        }
        
        for filename in ["rai_tools_catalog.json", "microsoft_references.json", 
                         "regulatory_frameworks.json", "code_examples.json"]:
            filepath = self.knowledge_dir / filename
            file_status = {
                "exists": filepath.exists(),
                "cached": filename in self._cache,
                "last_loaded": str(self._load_timestamps.get(filename, "Never"))
            }
            
            if filepath.exists():
                data = self._get_cached_or_load(filename)
                metadata = data.get("metadata", data.get("catalog_metadata", {}))
                file_status["version"] = metadata.get("version", "unknown")
                file_status["last_updated"] = metadata.get("last_updated", "unknown")
            
            status["files"][filename] = file_status
        
        return status


# Global singleton instance
_knowledge_loader: Optional[KnowledgeLoader] = None


def get_knowledge_loader() -> KnowledgeLoader:
    """Get the global knowledge loader instance."""
    global _knowledge_loader
    if _knowledge_loader is None:
        _knowledge_loader = KnowledgeLoader()
    return _knowledge_loader


def load_all_knowledge() -> Dict[str, Any]:
    """Load and return all knowledge for validation."""
    loader = get_knowledge_loader()
    return {
        "tools_catalog": loader.tools_catalog,
        "microsoft_references": loader.microsoft_references,
        "regulatory_frameworks": loader.regulatory_frameworks,
        "code_examples": loader.code_examples
    }


# =============================================================================
# KNOWLEDGE INJECTION FOR SYSTEM PROMPT
# =============================================================================

def get_tools_by_rai_pillar() -> Dict[str, List[Dict[str, Any]]]:
    """
    Organize all tools from the catalog by RAI pillar.
    Returns a dictionary with pillar names as keys and lists of tools as values.
    """
    loader = get_knowledge_loader()
    catalog = loader.tools_catalog
    
    pillars = {
        "Fairness": [],
        "Reliability & Safety": [],
        "Privacy & Security": [],
        "Inclusiveness": [],
        "Transparency": [],
        "Accountability": []
    }
    
    # Iterate through all categories and tools
    for category_name, category_data in catalog.get("categories", {}).items():
        for tool in category_data.get("tools", []):
            tool_pillars = tool.get("rai_pillars", [])
            tool_info = {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "primary_purpose": tool.get("primary_purpose", ""),
                "when_to_use": tool.get("when_to_use", []),
                "status": tool.get("status", "GA"),
                "documentation_url": tool.get("documentation_url", ""),
                "category": category_name
            }
            
            # Add tool to each pillar it addresses
            for pillar in tool_pillars:
                # Normalize pillar names
                if "Safety" in pillar and "Reliability" not in pillar:
                    pillar = "Reliability & Safety"
                elif "Security" in pillar and "Privacy" not in pillar:
                    pillar = "Privacy & Security"
                
                if pillar in pillars:
                    pillars[pillar].append(tool_info)
    
    return pillars


def get_tools_catalog_for_prompt() -> str:
    """
    Build a comprehensive tools catalog summary organized by RAI pillar
    for injection into the system prompt.
    """
    pillars = get_tools_by_rai_pillar()
    loader = get_knowledge_loader()
    
    parts = [
        "",
        "# MICROSOFT RAI TOOLS CATALOG (Use ONLY these tools in recommendations)",
        "",
        "**CRITICAL**: When making recommendations, you MUST use tools from this catalog.",
        "Each tool includes: purpose, when to use, and documentation URL.",
        ""
    ]
    
    for pillar_name, tools in pillars.items():
        if not tools:
            continue
            
        parts.append(f"## {pillar_name} Tools")
        parts.append("")
        
        # Deduplicate tools (same tool may appear multiple times)
        seen_tools = set()
        for tool in tools:
            if tool["name"] in seen_tools:
                continue
            seen_tools.add(tool["name"])
            
            parts.append(f"### {tool['name']}")
            parts.append(f"- **Purpose**: {tool['primary_purpose'] or tool['description'][:200]}")
            if tool['when_to_use']:
                use_cases = tool['when_to_use'][:3] if isinstance(tool['when_to_use'], list) else [tool['when_to_use']]
                parts.append(f"- **When to Use**: {'; '.join(use_cases)}")
            if tool['documentation_url']:
                parts.append(f"- **Docs**: {tool['documentation_url']}")
            parts.append("")
    
    # Add use case scenarios
    catalog = loader.tools_catalog
    scenarios = catalog.get("actionable_use_cases", {}).get("scenarios", [])
    
    if scenarios:
        parts.append("")
        parts.append("# USE CASE TOOL MAPPINGS")
        parts.append("")
        parts.append("Use these as reference when recommending tools for specific project types:")
        parts.append("")
        
        for scenario in scenarios[:5]:  # Top 5 scenarios
            parts.append(f"## {scenario.get('title', '')}")
            parts.append(f"**Risk Profile**: {scenario.get('risk_profile', '')}")
            
            required = scenario.get("required_tools", [])
            if required:
                tool_names = [t.get("tool", "") if isinstance(t, dict) else t for t in required[:4]]
                parts.append(f"**Required Tools**: {', '.join(tool_names)}")
            
            parts.append("")
    
    return "\n".join(parts)


def get_latest_tools_summary() -> str:
    """Get a summary of the latest tools for the system prompt."""
    loader = get_knowledge_loader()
    
    summary_parts = [
        "",
        "## Latest Microsoft RAI Tools (Updated December 2025 - Ignite 2025)",
        "",
        "### NEW at Ignite 2025:",
        "- **Microsoft Foundry Control Plane** (Public Preview): Unified governance, security, and observability for AI agents",
        "- **Microsoft Agent 365** (Public Preview): Enterprise agent management control plane", 
        "- **Foundry IQ** (Public Preview): RAG reimagined as dynamic reasoning",
        "- **GitHub + Defender Integration** (Public Preview): Unified code-to-cloud security",
        "- **Entra Agent ID**: Identity management for AI agents",
        "",
        "### Core RAI Tools:",
        "- **Azure AI Content Safety**: Content moderation, Prompt Shields, Groundedness Detection",
        "- **Azure AI Evaluation SDK**: Quality, safety, and agent evaluators",
        "- **Fairlearn**: Fairness metrics and bias mitigation (v0.13.0)",
        "- **InterpretML**: Explainable Boosting Machines, SHAP, LIME (v0.7.3)",
        "- **Presidio**: PII detection and anonymization (v2.2.0)",
        "- **PyRIT**: AI red teaming and security testing (v0.10.0)",
        ""
    ]
    
    return "\n".join(summary_parts)


def build_knowledge_context(
    industry: Optional[str] = None,
    use_case: Optional[str] = None,
    include_tools: bool = True,
    include_regulations: bool = True
) -> str:
    """
    Build a context string from knowledge base for injection into prompts.
    """
    loader = get_knowledge_loader()
    context_parts = []
    
    if include_tools and use_case:
        uc_rec = loader.get_use_case_recommendation(use_case)
        if uc_rec:
            context_parts.append(f"\n## Recommended Tools for {uc_rec.get('type', use_case)}")
            context_parts.append(f"**Key Risks**: {', '.join(uc_rec.get('risks', []))}")
            context_parts.append(f"**Required Tools**: {', '.join(uc_rec.get('required_tools', []))}")
            context_parts.append(f"**Evaluators**: {', '.join(uc_rec.get('recommended_evaluators', []))}")
    
    if include_tools and industry:
        ind_rec = loader.get_industry_recommendation(industry)
        if ind_rec:
            context_parts.append(f"\n## Industry Requirements: {ind_rec.get('industry', industry)}")
            context_parts.append(f"**Regulatory**: {', '.join(ind_rec.get('regulatory_requirements', []))}")
            context_parts.append(f"**Priority Tools**: {', '.join(ind_rec.get('priority_tools', []))}")
    
    if include_regulations:
        eu_ai_act = loader.regulatory_frameworks.get("eu_ai_act", {})
        if eu_ai_act:
            context_parts.append("\n## EU AI Act Quick Reference")
            for cat_name, cat_data in eu_ai_act.get("risk_categories", {}).items():
                context_parts.append(f"- **{cat_name.replace('_', ' ').title()}**: {cat_data.get('description', '')}")
    
    return "\n".join(context_parts)


def get_code_examples_for_tool(tool_name: str) -> str:
    """Get formatted code examples for a specific tool."""
    loader = get_knowledge_loader()
    examples = loader.get_all_code_examples(tool_name)
    
    if not examples:
        return ""
    
    parts = [f"\n### Code Examples for {tool_name}:"]
    for ex in examples[:2]:  # Limit to 2 examples
        parts.append(f"\n**{ex.get('description', '')}**")
        parts.append(f"```{ex.get('language', 'python')}")
        parts.append(ex.get('code', ''))
        parts.append("```")
    
    return "\n".join(parts)


# =============================================================================
# CLI for testing and validation
# =============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("RAI Knowledge Loader - Validation")
    print("=" * 60)
    
    loader = get_knowledge_loader()
    status = loader.get_knowledge_status()
    
    print(f"\nKnowledge Directory: {status['knowledge_directory']}")
    print("\nFile Status:")
    
    all_valid = True
    for filename, file_status in status['files'].items():
        exists = "✓" if file_status['exists'] else "✗"
        version = file_status.get('version', 'N/A')
        updated = file_status.get('last_updated', 'N/A')
        print(f"  [{exists}] {filename}")
        if file_status['exists']:
            print(f"      Version: {version}, Updated: {updated}")
        else:
            all_valid = False
    
    if all_valid:
        print("\n✓ All knowledge files loaded successfully!")
        
        # Test some lookups
        print("\nSample Lookups:")
        
        tool = loader.get_tool_info("Fairlearn")
        if tool:
            print(f"  Fairlearn version: {tool.get('version', 'N/A')}")
        
        uc = loader.get_use_case_recommendation("AI Agents")
        if uc:
            print(f"  Agent tools: {', '.join(uc.get('required_tools', [])[:3])}")
        
        ind = loader.get_industry_recommendation("Healthcare")
        if ind:
            print(f"  Healthcare priority: {', '.join(ind.get('priority_tools', [])[:3])}")
        
        sys.exit(0)
    else:
        print("\n✗ Some knowledge files are missing!")
        sys.exit(1)
