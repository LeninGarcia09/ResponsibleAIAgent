# Contributing to Responsible AI Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker (optional, for local container testing)
- Azure CLI (for deployment)
- Git

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/responsible-ai-agent.git
   cd responsible-ai-agent
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Variables**:
   ```bash
   # Backend (.env)
   cp .env.example .env
   # Edit with your Azure OpenAI credentials
   
   # Frontend (.env.local)
   cd frontend
   cp .env.local.example .env.local
   ```

5. **Run Locally**:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Project Structure

```
responsible-ai-agent/
├── backend/                 # Flask API
│   ├── app.py              # Main application
│   ├── rai_system_prompt.py # AI system prompt
│   └── requirements.txt
├── frontend/               # Next.js UI
│   ├── src/app/           # App routes
│   └── src/lib/           # API client
├── docs/                   # Documentation
├── infrastructure/         # Terraform configs
└── .github/workflows/      # CI/CD
```

## Types of Contributions

### 1. System Prompt Improvements

The AI's behavior is defined in `backend/rai_system_prompt.py`. When improving the prompt:

- **Test thoroughly** before submitting
- Provide **before/after examples** in your PR
- Update `docs/SYSTEM_PROMPT.md`
- Consider edge cases (LLM vs ML projects, different industries)

### 2. Frontend Enhancements

- Follow React/Next.js best practices
- Use TypeScript for type safety
- Keep components modular
- Update CSS modules for styling

### 3. Backend Features

- Follow Flask conventions
- Add proper error handling
- Document new endpoints
- Update `requirements.txt` if adding dependencies

### 4. Documentation

- Fix typos, improve clarity
- Add examples and diagrams
- Keep docs in sync with code

## Branching Strategy

```
main
  └── feature/your-feature-name
  └── fix/bug-description
  └── docs/documentation-update
```

- `main` - Production-ready code
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation only

## Commit Messages

Use conventional commits:

```
feat: add new fairness metric recommendation
fix: correct URL for Presidio documentation
docs: update system prompt documentation
refactor: simplify recommendation parsing
test: add evaluation test cases
```

## Pull Request Process

1. **Create a branch** from `main`
2. **Make your changes** with clear commits
3. **Test locally** - ensure nothing breaks
4. **Update documentation** if needed
5. **Submit PR** with:
   - Clear description of changes
   - Screenshots (for UI changes)
   - Before/after examples (for prompt changes)
   - Link to related issue (if applicable)

## Code Review

PRs require:
- At least 1 approval
- Passing CI checks
- No merge conflicts

## Testing

### Backend Tests
```bash
cd backend
python -m pytest test_backend.py -v
```

### Frontend Tests
```bash
cd frontend
npm run lint
npm run build
```

### Prompt Evaluation

For system prompt changes, include test cases:

```python
# Test Case 1: LLM Project
{
    "project_name": "Customer Chatbot",
    "project_description": "GPT-4 powered chatbot",
    "expected": ["Prompt Shields", "Content Safety", "Groundedness"]
}

# Test Case 2: ML Classification
{
    "project_name": "Loan Approval Model",
    "project_description": "ML model for credit decisions",
    "expected": ["Fairlearn", "InterpretML", "Explainability"]
}
```

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow Microsoft's Code of Conduct

## Questions?

- Open an issue for bugs or feature requests
- Contact: Lenin Garcia (lesalgad@microsoft.com)

## License

By contributing, you agree that your contributions will be licensed under the project's license.
