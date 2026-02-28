# Infra Telemetry Harvester

> Automated monitoring of infrastructure-related community incident reports for SRE audit.

## Overview

This project implements a **Responsible Builder Policy** compliant Reddit data collection system. It is designed as a professional enterprise monitoring tool that respects Reddit's API terms and rate limits.

### Architecture Principles

| Principle | Implementation |
|-----------|----------------|
| **Low-Velocity, High-Precision** | 30-minute polling intervals, targeted subreddits |
| **Machine-to-Machine Auth** | Client Credentials flow (read-only, no impersonation) |
| **Rate Limit Compliance** | PRAW native header handling + manual delays |
| **Enterprise Identity** | Professional User-Agent signaling legitimate use |

## Project Structure

```
reddit-telemetry-harvester/
├── api/
│   └── callback.py          # Vercel serverless OAuth callback endpoint
├── scripts/
│   └── harvester.py         # Main telemetry harvester
├── .github/workflows/
│   └── harvest.yml          # GitHub Actions scheduled execution
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment config
└── README.md               # This file
```

## Setup Instructions

### 1. Create Reddit App

1. Navigate to: https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Configure exactly as follows:

| Field | Value |
|-------|-------|
| **Name** | `Infra_Telemetry_Harvester` |
| **Description** | `Automated monitoring of infrastructure-related community incident reports for SRE audit.` |
| **App Type** | `Script` |
| **Redirect URI** | `https://your-project.vercel.app/api/telemetry/callback` |

4. Save the **Client ID** (under app name) and **Client Secret**

### 2. Deploy to Vercel

```bash
# Install Vercel CLI if needed
npm i -g vercel

# Deploy
cd reddit-telemetry-harvester
vercel
```

Note your deployed URL and update the Reddit app Redirect URI if needed.

### 3. Configure GitHub Repository

```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit: Infra Telemetry Harvester"

# Create GitHub repo (via gh CLI or web interface)
gh repo create infra-telemetry-harvester --public --source=. --remote=origin --push
```

### 4. Configure GitHub Secrets

Add these secrets to your GitHub repository:

| Secret Name | Value |
|-------------|-------|
| `REDDIT_CLIENT_ID` | Your Reddit app Client ID |
| `REDDIT_CLIENT_SECRET` | Your Reddit app Client Secret |

Via CLI:
```bash
gh secret set REDDIT_CLIENT_ID --body "your_client_id"
gh secret set REDDIT_CLIENT_SECRET --body "your_client_secret"
```

### 5. Run Harvester

**Locally:**
```bash
# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Install dependencies
pip install -r requirements.txt

# Run
python scripts/harvester.py
```

**GitHub Actions:**
- The workflow runs automatically every 30 minutes
- Manual trigger: Actions → Infra Telemetry Harvest → Run workflow

## Target Subreddits

Currently monitoring:
- `GoogleCloud` - GCP incidents and discussions
- `aws` - Amazon Web Services updates
- `Azure` - Microsoft Azure community
- `devops` - DevOps practices and tools
- `kubernetes` - K8s cluster management
- `sysadmin` - System administration
- `SRE` - Site Reliability Engineering
- `ClaudeAI`, `OpenAI` - AI infrastructure
- `MachineLearning` - ML ops and scaling

## Compliance Notes

### User-Agent
```
InfraTelemetryHarvester/1.0 (Enterprise SRE Monitoring; Contact: sre-team@company.internal; Purpose: Infrastructure Incident Research)
```

This User-Agent signals:
- Legitimate enterprise use case
- Contact point for inquiries
- Specific, non-abusive purpose

### Rate Limiting
- PRAW automatically respects `X-Ratelimit` headers
- Additional 2-second delay between subreddit queries
- 30-minute GitHub Actions schedule (conservative)

### Data Usage
- Read-only access to public posts
- No user impersonation
- No comment posting or voting
- Focused on infrastructure incident research

## License

Internal use only - SRE Telemetry Team
