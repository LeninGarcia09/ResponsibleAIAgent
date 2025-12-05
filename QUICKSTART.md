# 🚀 Quick Start Guide - Responsible AI Agent

## ⚡ TL;DR - Get Running in 5 Minutes

### What Works Right Now (No Azure Required)
```powershell
# 1. Test Backend Modules
cd C:\ResponsibleAIAgent\backend
python test_backend.py

# 2. Run Frontend UI
cd C:\ResponsibleAIAgent\frontend
npm run dev
# Open http://localhost:3000
```

### What You've Built
- ✅ **Backend**: 3 Azure Functions (Submit, Process, Generate Reports)
- ✅ **AI Review Engine**: Automated compliance checking
- ✅ **Frontend**: Next.js web application
- ✅ **Data Models**: 7 Responsible AI Principles + Security Checks
- ✅ **Reports**: HTML report generation with email delivery

---

## 📋 Testing Checklist - What We Verified

| Component | Status | Command |
|-----------|--------|---------|
| Python Dependencies | ✅ | `pip install -r requirements.txt` |
| Backend Config | ✅ | `python test_backend.py` |
| Data Models | ✅ | Pydantic validation working |
| Frontend Dependencies | ✅ | `npm install` |
| Frontend Build | ✅ | `npm run build` |

---

## 🎯 Three Ways to Use This Project

### 1️⃣ Frontend Development (No Backend)
Perfect for UI/UX work:
```powershell
cd frontend
npm run dev
```
→ http://localhost:3000

### 2️⃣ Backend Testing (No Azure)
Test Python logic and models:
```powershell
cd backend
python test_backend.py
```

### 3️⃣ Full Stack (Requires Azure)
Complete end-to-end testing:
```powershell
# Step 1: Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Step 2: Configure credentials in backend/local.settings.json

# Step 3: Start Backend (Terminal 1)
cd backend
func start

# Step 4: Start Frontend (Terminal 2)
cd frontend
npm run dev
```

---

## 🔑 Azure Services You'll Need (Later)

Only required when you want to deploy or test with real Azure:

| Service | Purpose | Required? |
|---------|---------|-----------|
| Azure OpenAI | AI-powered review | Yes |
| Cosmos DB | Data storage | Yes |
| Blob Storage | Report storage | Yes |
| Microsoft Graph API | Email notifications | Optional |
| Azure Key Vault | Secrets management | Recommended |

---

## 📁 Key Files Reference

### Backend
- `backend/shared/models.py` - Data models for reviews
- `backend/shared/config.py` - Configuration management
- `backend/shared/azure_clients.py` - Azure service clients
- `backend/SubmitReview/__init__.py` - Submit review endpoint
- `backend/ProcessReview/__init__.py` - AI review engine
- `backend/GenerateReport/__init__.py` - Report generation
- `backend/test_backend.py` - **Run this to test backend**

### Frontend
- `frontend/src/app/page.tsx` - Home page
- `frontend/src/app/layout.tsx` - App layout
- `frontend/package.json` - Dependencies

### Config
- `backend/local.settings.json` - Backend configuration
- `frontend/.env.local.example` - Frontend environment template
- `.env.example` - Root environment template

---

## 🧪 Quick Test Commands

```powershell
# Test backend modules
cd backend; python test_backend.py

# Build frontend
cd frontend; npm run build

# Check structure
Get-ChildItem -Recurse -Directory | Select-Object FullName

# View Python dependencies
cd backend; pip list | Select-String "azure|openai|msal"

# View npm dependencies
cd frontend; npm list --depth=0
```

---

## 💡 Common Tasks

### Add a New Azure Function
1. Create folder: `backend/NewFunction/`
2. Add `__init__.py` with async main()
3. Add `function.json` with binding config

### Modify Review Criteria
Edit: `backend/ProcessReview/__init__.py`
- Add methods: `_assess_new_principle()`
- Update scoring: `_calculate_score()`

### Add Frontend Page
1. Create: `frontend/src/app/newpage/page.tsx`
2. Auto-routes to `/newpage`

---

## 🆘 Troubleshooting

### "Import errors" in backend
```powershell
cd backend
pip install -r requirements.txt --upgrade
```

### "Module not found" in frontend
```powershell
cd frontend
rm -rf node_modules
npm install
```

### "func not recognized"
Install Azure Functions Core Tools:
```powershell
npm install -g azure-functions-core-tools@4
```

---

## 📊 Project Stats

- **Python Files**: 8
- **TypeScript Files**: 2  
- **Python Dependencies**: 25 packages
- **npm Dependencies**: 378 packages
- **Azure Functions**: 3
- **Responsible AI Principles**: 7
- **Security Check Types**: 6

---

## 🎓 Learning Resources

- **Responsible AI**: https://www.microsoft.com/ai/responsible-ai
- **Azure Functions**: https://learn.microsoft.com/azure/azure-functions/
- **Next.js**: https://nextjs.org/docs
- **Azure OpenAI**: https://learn.microsoft.com/azure/ai-services/openai/

---

## 📞 Documentation Map

1. **README.md** - Full project documentation
2. **TESTING.md** - Detailed testing procedures
3. **TEST_SUMMARY.md** - Complete test results
4. **QUICKSTART.md** - This file (fastest way to get started)

---

## ✨ What's Next?

You can now:
1. ✅ Develop the frontend UI
2. ✅ Test backend logic without Azure
3. ✅ Create additional review criteria
4. ⏳ Provision Azure resources (when ready)
5. ⏳ Deploy to production

**Everything is set up and tested. Happy coding! 🚀**

---

*Last Updated: December 2, 2025*  
*Project: Responsible AI Agent*  
*Status: ✅ All Systems Ready*
