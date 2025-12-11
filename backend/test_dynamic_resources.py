"""Test script for dynamic resources module."""
import sys

try:
    from dynamic_resources import get_dynamic_fetcher, get_dynamic_reference_architectures
    
    print("=" * 60)
    print("Dynamic Resources Module Test")
    print("=" * 60)
    
    # Initialize fetcher
    fetcher = get_dynamic_fetcher()
    print("✅ Dynamic Resource Fetcher initialized")
    
    # Test GitHub repos (without API - uses curated list)
    print("\n📦 Testing get_popular_azure_samples(3)...")
    repos = fetcher.get_popular_azure_samples(3)
    print(f"Found {len(repos)} repos:")
    for r in repos:
        # The structure uses 'full_name' or 'name' not 'repo'
        repo_name = r.get('full_name') or r.get('name', 'unknown')
        stars = r.get('stars', 'N/A')
        desc = r.get('description') or 'No description'
        print(f"  - {repo_name}: {stars} stars")
        print(f"    {desc[:60]}...")
    
    # Test reference architectures
    print("\n🏗️ Testing get_reference_architectures('chatbot', '')...")
    arch = fetcher.get_reference_architectures("chatbot", "")
    print(f"Architecture keys: {list(arch.keys())}")
    
    if "recommended_repos" in arch:
        print(f"  Recommended repos: {len(arch['recommended_repos'])}")
    if "azure_services" in arch:
        print(f"  Azure services: {len(arch['azure_services'])}")
    if "rai_considerations" in arch:
        print(f"  RAI considerations: {len(arch['rai_considerations'])}")
    
    # Test multi-agent architecture
    print("\n🤖 Testing get_reference_architectures('multi_agent', '')...")
    agent_arch = fetcher.get_reference_architectures("multi_agent", "")
    if "recommended_repos" in agent_arch:
        print(f"  Agent-focused repos: {len(agent_arch['recommended_repos'])}")
        for r in agent_arch['recommended_repos'][:2]:
            print(f"    - {r.get('repo', 'unknown')}")
    
    # Test cache stats
    print("\n📊 Cache Statistics:")
    stats = fetcher.get_cache_stats()
    for key, val in stats.items():
        print(f"  {key}: {val}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
