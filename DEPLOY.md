# Deploy AI Research Agent to Render (Free Tier)

## Prerequisites

1. **GitHub Account** - https://github.com
2. **Render Account** - https://render.com (sign up with GitHub)
3. **API Keys**:
   - Groq API Key: https://console.groq.com
   - Tavily API Key: https://tavily.com
   - Google API Key (optional): https://makersuite.google.com

---

## Step 1: Prepare Your Project

### 1.1 Copy Deployment Files

Copy these files into your project root:
- `render.yaml`
- `build.sh`
- `Procfile`
- `runtime.txt`
- `requirements.txt` (overwrite with production version)
- `config/settings.py` (overwrite with production version)
- `.env.example`
- `.gitignore`

### 1.2 Make build.sh Executable

```bash
chmod +x build.sh