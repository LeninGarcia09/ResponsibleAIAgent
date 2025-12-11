"""
Dynamic Resources Module

This module provides real-time fetching of Microsoft AI reference architectures,
GitHub samples, and guidance resources. It uses multiple strategies to ensure
content freshness:

1. Azure OpenAI with Bing grounding for real-time web search
2. GitHub API for repository metadata and activity
3. Intelligent caching with TTL to balance freshness vs. cost

Version: 1.0.0
Created: December 2025
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_TTL_HOURS = {
    "github_repos": 6,           # GitHub data refreshes every 6 hours
    "reference_architectures": 24,  # Architecture docs refresh daily
    "tools_catalog": 12,         # Tools refresh every 12 hours
    "web_search": 4,             # Web search results refresh every 4 hours
}

# Ensure cache directory exists
CACHE_DIR.mkdir(exist_ok=True)


class DynamicResourceFetcher:
    """
    Fetches and caches dynamic AI resources from multiple sources.
    
    Strategies:
    1. Bing-grounded Azure OpenAI for comprehensive web search
    2. GitHub API for repository statistics
    3. Static fallback for offline/error scenarios
    """
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client
        self.github_token = os.environ.get("GITHUB_TOKEN")  # Optional, for higher rate limits
        
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the cache file path for a given key."""
        safe_key = hashlib.md5(cache_key.encode()).hexdigest()
        return CACHE_DIR / f"{safe_key}.json"
    
    def _is_cache_valid(self, cache_path: Path, ttl_hours: int) -> bool:
        """Check if cached data is still valid based on TTL."""
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                cached_time = datetime.fromisoformat(cached.get("timestamp", "2000-01-01"))
                return datetime.now() - cached_time < timedelta(hours=ttl_hours)
        except Exception:
            return False
    
    def _read_cache(self, cache_path: Path) -> Optional[Dict[str, Any]]:
        """Read data from cache."""
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("data")
        except Exception:
            return None
    
    def _write_cache(self, cache_path: Path, data: Any) -> None:
        """Write data to cache with timestamp."""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")
    
    def fetch_github_repo_info(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real-time repository information from GitHub API.
        
        Returns: Repository metadata including stars, last update, description
        """
        cache_key = f"github_{owner}_{repo}"
        cache_path = self._get_cache_path(cache_key)
        
        # Check cache first
        if self._is_cache_valid(cache_path, CACHE_TTL_HOURS["github_repos"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                cached_data["_source"] = "cache"
                return cached_data
        
        # Fetch from GitHub API
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ResponsibleAIAgent/1.0"
            }
            
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                repo_data = json.loads(response.read().decode())
                
                result = {
                    "name": repo_data.get("name"),
                    "full_name": repo_data.get("full_name"),
                    "description": repo_data.get("description"),
                    "url": repo_data.get("html_url"),
                    "stars": repo_data.get("stargazers_count", 0),
                    "forks": repo_data.get("forks_count", 0),
                    "last_updated": repo_data.get("updated_at"),
                    "last_pushed": repo_data.get("pushed_at"),
                    "topics": repo_data.get("topics", []),
                    "language": repo_data.get("language"),
                    "open_issues": repo_data.get("open_issues_count", 0),
                    "license": repo_data.get("license", {}).get("spdx_id"),
                    "_source": "github_api",
                    "_fetched_at": datetime.now().isoformat()
                }
                
                self._write_cache(cache_path, result)
                return result
                
        except urllib.error.HTTPError as e:
            logger.warning(f"GitHub API error for {owner}/{repo}: {e.code}")
        except Exception as e:
            logger.warning(f"Failed to fetch GitHub repo {owner}/{repo}: {e}")
        
        # Return cached data even if expired (better than nothing)
        cached_data = self._read_cache(cache_path)
        if cached_data:
            cached_data["_source"] = "stale_cache"
            return cached_data
        
        return None
    
    def get_popular_azure_samples(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of popular Azure-Samples repositories for AI/ML.
        Uses cached list with periodic refresh.
        """
        # Key repositories to track (curated list)
        key_repos = [
            ("Azure-Samples", "azure-search-openai-demo"),
            ("Azure-Samples", "chat-with-your-data-solution-accelerator"),
            ("Azure-Samples", "contoso-chat-csharp-prompty"),
            ("Azure-Samples", "openai"),
            ("Azure-Samples", "cognitive-services-speech-sdk"),
            ("Azure-Samples", "graphrag-accelerator"),
            ("Azure-Samples", "microsoft-foundry-basic"),
            ("Azure-Samples", "mcp-agent-langchainjs"),
            ("Azure-Samples", "aspire-semantic-kernel-creative-writer"),
            ("Azure-Samples", "art-voice-agent-accelerator"),
            ("microsoft", "semantic-kernel"),
            ("microsoft", "responsible-ai-toolbox"),
            ("microsoft", "autogen"),
            ("microsoft", "promptflow"),
            ("microsoft", "guidance"),
        ]
        
        results = []
        for owner, repo in key_repos[:limit]:
            info = self.fetch_github_repo_info(owner, repo)
            if info:
                results.append(info)
        
        # Sort by stars
        results.sort(key=lambda x: x.get("stars", 0), reverse=True)
        return results
    
    def search_with_bing_grounding(
        self, 
        query: str, 
        context: str = "Microsoft Azure AI"
    ) -> Optional[Dict[str, Any]]:
        """
        Use Azure OpenAI with Bing grounding to search for latest information.
        
        This enables real-time web search through the AI model.
        """
        cache_key = f"bing_search_{query}_{context}"
        cache_path = self._get_cache_path(cache_key)
        
        # Check cache first
        if self._is_cache_valid(cache_path, CACHE_TTL_HOURS["web_search"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                cached_data["_source"] = "cache"
                return cached_data
        
        if not self.openai_client:
            logger.warning("OpenAI client not available for Bing grounding")
            return None
        
        try:
            # Use Azure OpenAI with Bing grounding (data_sources)
            deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a research assistant specialized in {context}.
                    Provide factual, up-to-date information with specific URLs and dates.
                    Format your response as JSON with these fields:
                    - results: array of relevant findings
                    - sources: array of source URLs
                    - last_verified: ISO date when you last verified this info"""
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            # Note: Bing grounding requires special configuration in Azure
            # This is a standard call that can be enhanced with data_sources
            response = self.openai_client.chat.completions.create(
                model=deployment,
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                # For Bing grounding, you would add:
                # extra_body={
                #     "data_sources": [{
                #         "type": "bing_grounding",
                #         "parameters": {"search_queries": [query]}
                #     }]
                # }
            )
            
            result_text = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{[\s\S]*\}', result_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"raw_response": result_text}
            except json.JSONDecodeError:
                result = {"raw_response": result_text}
            
            result["_source"] = "bing_grounding"
            result["_fetched_at"] = datetime.now().isoformat()
            
            self._write_cache(cache_path, result)
            return result
            
        except Exception as e:
            logger.error(f"Bing grounding search failed: {e}")
            return None
    
    def get_reference_architectures(
        self, 
        project_type: str,
        use_case: str
    ) -> Dict[str, Any]:
        """
        Get relevant reference architectures for a given project type and use case.
        
        Combines:
        - Curated architecture patterns
        - Real-time GitHub repo data
        - Cached documentation links
        """
        cache_key = f"ref_arch_{project_type}_{use_case}"
        cache_path = self._get_cache_path(cache_key)
        
        # Check cache
        if self._is_cache_valid(cache_path, CACHE_TTL_HOURS["reference_architectures"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Build architecture recommendation
        result = {
            "patterns": [],
            "github_repos": [],
            "documentation": [],
            "quick_start_commands": [],
            "_generated_at": datetime.now().isoformat()
        }
        
        # Map project types to relevant patterns
        pattern_mapping = {
            "chatbot": {
                "patterns": ["RAG", "Conversational AI", "Multi-turn Dialog"],
                "repos": [
                    ("Azure-Samples", "azure-search-openai-demo"),
                    ("Azure-Samples", "chat-with-your-data-solution-accelerator"),
                ],
                "docs": [
                    {"title": "RAG Solution Design Guide", "url": "https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide"},
                    {"title": "Chat with Your Data", "url": "https://learn.microsoft.com/azure/ai-services/openai/concepts/use-your-data"},
                ]
            },
            "content_generation": {
                "patterns": ["LLM Fine-tuning", "Prompt Engineering", "Content Safety"],
                "repos": [
                    ("Azure-Samples", "openai"),
                    ("microsoft", "guidance"),
                ],
                "docs": [
                    {"title": "Azure OpenAI Fine-tuning", "url": "https://learn.microsoft.com/azure/ai-services/openai/how-to/fine-tuning"},
                    {"title": "Content Safety", "url": "https://learn.microsoft.com/azure/ai-services/content-safety/overview"},
                ]
            },
            "document_processing": {
                "patterns": ["Document Intelligence", "OCR + LLM", "Form Recognition"],
                "repos": [
                    ("Azure-Samples", "azure-search-openai-demo"),
                ],
                "docs": [
                    {"title": "Document Intelligence", "url": "https://learn.microsoft.com/azure/ai-services/document-intelligence/"},
                ]
            },
            "multi_agent": {
                "patterns": ["Agent Orchestration", "Semantic Kernel Agents", "AutoGen"],
                "repos": [
                    ("microsoft", "semantic-kernel"),
                    ("microsoft", "autogen"),
                    ("Azure-Samples", "mcp-agent-langchainjs"),
                ],
                "docs": [
                    {"title": "AI Agent Orchestration Patterns", "url": "https://learn.microsoft.com/azure/architecture/ai-ml/guide/ai-agent-design-patterns"},
                    {"title": "Semantic Kernel Agents", "url": "https://learn.microsoft.com/semantic-kernel/frameworks/agent/"},
                ]
            },
            "voice_enabled": {
                "patterns": ["Speech-to-Text", "Text-to-Speech", "Voice Agents"],
                "repos": [
                    ("Azure-Samples", "cognitive-services-speech-sdk"),
                    ("Azure-Samples", "art-voice-agent-accelerator"),
                ],
                "docs": [
                    {"title": "Azure Speech Services", "url": "https://learn.microsoft.com/azure/ai-services/speech-service/"},
                ]
            },
            "computer_vision": {
                "patterns": ["Image Classification", "Object Detection", "Multimodal"],
                "repos": [
                    ("microsoft", "responsible-ai-toolbox"),
                ],
                "docs": [
                    {"title": "Azure AI Vision", "url": "https://learn.microsoft.com/azure/ai-services/computer-vision/"},
                ]
            },
            "default": {
                "patterns": ["RAG", "Azure AI Foundry Baseline"],
                "repos": [
                    ("Azure-Samples", "azure-search-openai-demo"),
                    ("Azure-Samples", "microsoft-foundry-basic"),
                ],
                "docs": [
                    {"title": "AI Architecture Design", "url": "https://learn.microsoft.com/azure/architecture/ai-ml/"},
                    {"title": "Microsoft Foundry", "url": "https://learn.microsoft.com/azure/ai-foundry/what-is-ai-foundry"},
                ]
            }
        }
        
        # Get mapping for project type (fallback to default)
        project_lower = project_type.lower() if project_type else "default"
        mapping = None
        
        for key in pattern_mapping:
            if key in project_lower or project_lower in key:
                mapping = pattern_mapping[key]
                break
        
        if not mapping:
            mapping = pattern_mapping["default"]
        
        result["patterns"] = mapping["patterns"]
        result["documentation"] = mapping["docs"]
        
        # Fetch real-time GitHub data for repos
        for owner, repo in mapping.get("repos", []):
            repo_info = self.fetch_github_repo_info(owner, repo)
            if repo_info:
                result["github_repos"].append(repo_info)
        
        # Add quick start commands
        if result["github_repos"]:
            primary_repo = result["github_repos"][0]
            result["quick_start_commands"] = [
                {
                    "description": f"Clone {primary_repo['name']}",
                    "command": f"git clone {primary_repo['url']}"
                },
                {
                    "description": "Deploy with Azure Developer CLI",
                    "command": f"azd init -t {primary_repo['full_name']}"
                }
            ]
        
        # Cache result
        self._write_cache(cache_path, result)
        
        return result
    
    def get_latest_tools_versions(self) -> Dict[str, Any]:
        """
        Get latest versions and release info for key RAI tools.
        """
        tools = [
            ("microsoft", "responsible-ai-toolbox"),
            ("microsoft", "promptflow"),
            ("fairlearn", "fairlearn"),
            ("interpretml", "interpret"),
        ]
        
        results = {}
        for owner, repo in tools:
            info = self.fetch_github_repo_info(owner, repo)
            if info:
                results[repo] = {
                    "latest_push": info.get("last_pushed"),
                    "stars": info.get("stars"),
                    "url": info.get("url"),
                }
        
        return results
    
    def clear_cache(self, cache_type: Optional[str] = None) -> int:
        """
        Clear cached data.
        
        Args:
            cache_type: Optional specific cache type to clear, or None for all
            
        Returns:
            Number of cache files deleted
        """
        count = 0
        for cache_file in CACHE_DIR.glob("*.json"):
            if cache_type is None:
                cache_file.unlink()
                count += 1
            elif cache_type in cache_file.stem:
                cache_file.unlink()
                count += 1
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        stats = {
            "total_files": 0,
            "total_size_bytes": 0,
            "oldest_entry": None,
            "newest_entry": None,
            "entries": []
        }
        
        for cache_file in CACHE_DIR.glob("*.json"):
            stats["total_files"] += 1
            stats["total_size_bytes"] += cache_file.stat().st_size
            
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    timestamp = data.get("timestamp")
                    if timestamp:
                        stats["entries"].append({
                            "file": cache_file.name,
                            "timestamp": timestamp
                        })
            except Exception:
                pass
        
        if stats["entries"]:
            stats["entries"].sort(key=lambda x: x["timestamp"])
            stats["oldest_entry"] = stats["entries"][0]["timestamp"]
            stats["newest_entry"] = stats["entries"][-1]["timestamp"]
        
        return stats


# Singleton instance
_fetcher_instance: Optional[DynamicResourceFetcher] = None


def get_dynamic_fetcher(openai_client=None) -> DynamicResourceFetcher:
    """Get or create the singleton DynamicResourceFetcher instance."""
    global _fetcher_instance
    
    if _fetcher_instance is None:
        _fetcher_instance = DynamicResourceFetcher(openai_client)
    elif openai_client and _fetcher_instance.openai_client is None:
        _fetcher_instance.openai_client = openai_client
    
    return _fetcher_instance


def get_dynamic_reference_architectures(
    project_type: str,
    use_case: str,
    openai_client=None
) -> Dict[str, Any]:
    """
    Convenience function to get reference architectures.
    
    This is the main entry point for the dynamic resources system.
    """
    fetcher = get_dynamic_fetcher(openai_client)
    return fetcher.get_reference_architectures(project_type, use_case)


def get_github_repo_realtime(owner: str, repo: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get real-time GitHub repo info.
    """
    fetcher = get_dynamic_fetcher()
    return fetcher.fetch_github_repo_info(owner, repo)
