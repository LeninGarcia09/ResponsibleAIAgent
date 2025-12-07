# RAI Agent Knowledge Base

This directory contains the externalized knowledge files for the Responsible AI Agent. This structure makes it easy to update the agent's knowledge without modifying code.

## Directory Structure

```
knowledge/
├── README.md                    # This file
├── rai_tools_catalog.json       # Comprehensive RAI tools catalog
├── microsoft_references.json    # Official Microsoft documentation links
├── regulatory_frameworks.json   # Regulatory requirements and mappings
├── code_examples.json           # Reusable code snippets
└── update_log.md               # Log of knowledge updates
```

## How to Update Knowledge

### 1. Tools Catalog (`rai_tools_catalog.json`)
- Contains all Microsoft RAI tools with capabilities, versions, and recommendations
- Update when new tools are released or at Microsoft events (Ignite, Build)
- Last updated: December 2025 (Ignite 2025 updates)

### 2. Microsoft References (`microsoft_references.json`)
- Official documentation URLs organized by category
- Update quarterly or when new docs are published
- Verify links are still valid before updating

### 3. Regulatory Frameworks (`regulatory_frameworks.json`)
- EU AI Act, NIST AI RMF, ISO 42001 requirements
- Update when regulations change or new guidance is published

### 4. Code Examples (`code_examples.json`)
- Working code snippets for each tool
- Update when APIs change or new patterns emerge

## Update Process

1. **Check for Updates**: Monitor these sources:
   - Microsoft Ignite announcements (annually, November)
   - Microsoft Build announcements (annually, May)
   - Azure AI Blog: https://azure.microsoft.com/en-us/blog/tag/ai/
   - GitHub releases for open-source tools

2. **Update Files**: Modify the relevant JSON file(s)

3. **Validate**: Run `python knowledge_loader.py`

4. **Log Changes**: Add entry to `update_log.md`

5. **Deploy**: Push changes and redeploy the agent

## Automated Update Sources

Consider setting up automated monitoring for:
- [ ] PyPI package versions (Fairlearn, InterpretML, etc.)
- [ ] GitHub release notifications
- [ ] Azure service updates RSS feed
- [ ] Microsoft Learn documentation changes

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-06 | 2.0.0 | Initial externalized knowledge structure, Ignite 2025 updates |
