# Transparency Note: Responsible AI Agent Platform

## What is the Responsible AI Agent?

The Responsible AI Agent is an AI-powered tool designed to help Microsoft employees and partners review AI implementations against Microsoft's Responsible AI principles and security best practices. It provides guidance and recommendations for building AI solutions that are fair, reliable, safe, private, inclusive, transparent, and accountable.

## Intended Use

### Primary Use Cases
- **AI Project Reviews**: Submit AI project descriptions to receive automated analysis and recommendations
- **Tool Discovery**: Browse the catalog of Microsoft Responsible AI tools and services
- **Guidance**: Get recommendations on which RAI tools to use for specific scenarios
- **Documentation**: Access organized resources on responsible AI implementation

### Intended Users
- Microsoft employees building AI solutions
- Microsoft partners developing AI applications
- Authorized external users participating in the pilot program

## How It Works

### AI-Powered Review
When you submit an AI project for review, the system:
1. Sends your project description to Azure OpenAI (GPT-4)
2. Analyzes it against Microsoft's Responsible AI principles
3. Identifies potential risks and gaps
4. Recommends appropriate tools and mitigations
5. Generates a structured review report

### Knowledge Base
The tool draws from:
- Microsoft's official Responsible AI documentation
- Tool and service specifications from Microsoft Ignite 2025
- Best practices and implementation guidance
- Risk-tool mapping matrices

## Limitations and Known Issues

### AI Limitations
- **Not a substitute for human review**: This tool provides automated guidance but does not replace formal Responsible AI reviews, legal review, or security assessments
- **Potential for incomplete analysis**: The AI may not identify all risks or considerations relevant to your specific context
- **Knowledge cutoff**: The tool's knowledge is based on available documentation and may not reflect the latest updates to tools or guidance
- **No code analysis**: The tool reviews project descriptions, not actual code or implementations

### Accuracy Considerations
- Recommendations are **advisory only** and should be validated by subject matter experts
- The AI may occasionally provide generic recommendations that need contextual adaptation
- Complex or novel AI applications may require additional human expertise

### What This Tool Cannot Do
- ❌ Guarantee compliance with regulations or policies
- ❌ Provide legal advice
- ❌ Replace security penetration testing
- ❌ Audit production AI systems
- ❌ Access or analyze your actual code, data, or deployed systems

## Responsible Use

### Best Practices
1. **Validate recommendations**: Always verify AI-generated recommendations with relevant experts
2. **Provide accurate information**: The quality of recommendations depends on the accuracy of your project description
3. **Use as a starting point**: Treat recommendations as a starting point for deeper investigation
4. **Report issues**: Use the feedback mechanism to report inaccurate or concerning outputs

### Prohibited Uses
- Do not submit sensitive or classified information
- Do not use for final compliance determinations
- Do not bypass human review processes based solely on this tool's output
- Do not share outputs externally without appropriate review

## Data Handling

### What Data We Collect
- Project descriptions you submit for review
- Generated review reports
- Basic usage analytics (anonymized)
- Feedback you provide

### How We Protect Your Data
- All data transmitted over HTTPS/TLS
- Data stored in Azure with encryption at rest
- Access controlled via Microsoft Entra ID
- No data shared with third parties
- Retention per Microsoft data governance policies

### AI Model Data Usage
- Your submissions are sent to Azure OpenAI for processing
- Azure OpenAI does not use your data to train models (per Microsoft enterprise terms)
- No prompts or completions are stored by Azure OpenAI beyond what's needed for abuse monitoring

## Feedback and Reporting

We actively encourage feedback to improve this tool:

- **Feature requests**: Submit via the feedback form in the application
- **Report issues**: Use the "Report a Problem" feature for inaccurate or concerning outputs
- **Security concerns**: Report to Microsoft Security Response Center (MSRC)

## Version Information

- **Current Version**: Pilot / Preview
- **Last Updated**: December 2025
- **Status**: Active development - features and recommendations may change

## Contact

**Tool Owner**: Lenin Garcia (lesalgad@microsoft.com)

For questions about this tool:
- **Product Team**: Contact Lenin Garcia at lesalgad@microsoft.com
- **Responsible AI Questions**: https://www.microsoft.com/ai/responsible-ai

---

*This Transparency Note follows Microsoft's Responsible AI Standard and HAX Toolkit guidelines for AI system documentation.*
