# Privacy Statement - RAI Tools Navigator

**Effective Date:** January 2025  
**Version:** 1.0.0  
**Owner:** Lenin Garcia (lesalgad@microsoft.com)

---

## 1. Overview

This Privacy Statement describes how the RAI Tools Navigator ("the Tool") collects, uses, and protects your information. This statement applies specifically to the pilot version of the Tool.

---

## 2. Information We Collect

### 2.1 Conversation Data

| Data Type | Description | Retention |
|-----------|-------------|-----------|
| **User Queries** | Questions and prompts you enter into the chat interface | Session + logs |
| **AI Responses** | The Tool's generated responses | Session + logs |
| **Session Context** | Conversation history within a session | Session duration |

### 2.2 Technical Data

| Data Type | Description | Purpose |
|-----------|-------------|---------|
| **Access Logs** | Timestamps, endpoints accessed | Operations, debugging |
| **Error Logs** | Error messages, stack traces | Bug fixing, reliability |
| **Performance Metrics** | Response times, resource usage | Optimization |

### 2.3 Data We Do NOT Collect

- Personal identification information (unless voluntarily provided in queries)
- Authentication credentials (managed by Azure infrastructure)
- Payment information
- Location data
- Device identifiers

---

## 3. How We Use Your Information

### 3.1 Primary Uses

| Purpose | Description |
|---------|-------------|
| **Provide Service** | Process your queries and generate relevant responses |
| **Improve Quality** | Analyze usage patterns to enhance Tool accuracy and usefulness |
| **Debug Issues** | Identify and fix technical problems |
| **Ensure Safety** | Monitor for misuse and enforce acceptable use policies |

### 3.2 AI Processing

Your queries are processed by:
- **Azure OpenAI Service (GPT-4o)** - For generating conversational responses
- **Backend RAG System** - For retrieving relevant RAI tool information

Queries are sent to Azure OpenAI with system prompts and context. Microsoft's data handling policies for Azure OpenAI apply.

---

## 4. Data Storage and Security

### 4.1 Where Data Is Stored

| Component | Location | Security |
|-----------|----------|----------|
| **Frontend** | Azure Container Apps (West US 3) | HTTPS, Azure security |
| **Backend** | Azure Container Apps (West US 3) | HTTPS, Managed Identity |
| **AI Service** | Azure OpenAI (Azure region) | Azure enterprise security |

### 4.2 Security Measures

- All data transmission encrypted via HTTPS/TLS
- Azure Managed Identity for service authentication
- No storage of credentials in code or configurations
- Azure infrastructure security and compliance

### 4.3 Data Retention

| Data Type | Retention Period | Deletion |
|-----------|------------------|----------|
| **Session Data** | Duration of session | Automatic on session end |
| **Application Logs** | 30 days (default) | Automatic rotation |
| **Error Logs** | 90 days | Automatic purge |

---

## 5. Data Sharing

### 5.1 We Share Data With

| Entity | Purpose | Data Shared |
|--------|---------|-------------|
| **Azure OpenAI** | AI processing | Queries and context |
| **Azure Platform** | Infrastructure | Operational data |

### 5.2 We Do NOT Share Data With

- Third-party advertisers
- Data brokers
- External analytics services
- Other Microsoft products (unless explicitly integrated)

### 5.3 Legal Disclosure

We may disclose information when required by law or to protect Microsoft's rights, safety, or property.

---

## 6. Your Rights and Choices

### 6.1 Access and Control

During the pilot phase:
- You may request information about data collected from your sessions
- You may request deletion of your session data
- You may opt out of the pilot program at any time

### 6.2 Contact for Requests

For privacy-related requests, contact:
- **Email:** lesalgad@microsoft.com
- **Subject Line:** "RAI Tools Navigator - Privacy Request"

### 6.3 Response Time

We will respond to privacy requests within 30 days.

---

## 7. Content Safety Considerations

### 7.1 Input Monitoring

The Tool may filter or reject inputs that:
- Contain harmful or inappropriate content
- Attempt to manipulate the AI system
- Violate acceptable use policies

### 7.2 Output Safety

AI-generated outputs are designed to:
- Avoid harmful content generation
- Stay within the scope of RAI tool guidance
- Decline inappropriate requests

---

## 8. Cookies and Tracking

### 8.1 Current State

The pilot version:
- Does NOT use tracking cookies
- Does NOT use third-party analytics
- Does NOT use advertising trackers

### 8.2 Session Management

Basic session functionality may use:
- Session identifiers (not persistent)
- Local storage for UI state (client-side only)

---

## 9. Children's Privacy

The Tool is not intended for use by individuals under 18 years of age. We do not knowingly collect information from children.

---

## 10. International Users

### 10.1 Data Location

Data is processed in the United States (Azure West US 3 region).

### 10.2 Cross-Border Transfers

By using the Tool, you consent to the transfer of your data to the United States for processing.

---

## 11. Changes to This Statement

### 11.1 Updates

We may update this Privacy Statement as the Tool evolves. Changes will be reflected in the "Effective Date" above.

### 11.2 Notification

Significant changes will be communicated through:
- Updated documentation
- In-app notifications (if applicable)

---

## 12. Microsoft Privacy Practices

This Tool operates within Microsoft's broader privacy framework. For more information:
- [Microsoft Privacy Statement](https://privacy.microsoft.com/privacystatement)
- [Azure Privacy](https://azure.microsoft.com/privacy)
- [Azure OpenAI Data Privacy](https://learn.microsoft.com/azure/ai-services/openai/concepts/data-privacy)

---

## 13. Contact Information

**Privacy Contact:** Lenin Garcia  
**Email:** lesalgad@microsoft.com  
**Role:** Tool Owner

For general Microsoft privacy inquiries:
- Visit: https://privacy.microsoft.com

---

## 14. Related Documents

- [Transparency Note](./TRANSPARENCY_NOTE.md)
- [Terms of Use](./TERMS_OF_USE.md)
- [System Card](./SYSTEM_CARD.md)

---

*Last Updated: January 2025*
