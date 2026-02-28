# infra-telemetry-harvester

A read-only telemetry collector for infrastructure incident signals from technical communities. Built because keeping tabs on emerging issues across cloud providers shouldn't require manually refreshing 10 different subreddits.

## Why this exists

If you've ever been paged at 3am because AWS us-east-1 is having issues *again*, and you had zero warning because you weren't watching r/aws at the right moment — this is for you.

Reddit's technical communities are often faster than official status pages. A post hits r/GoogleCloud about BigQuery latency 15-20 minutes before the dashboard updates. This harvester exists to capture those signals programmatically, without being a jerk about it.

## The 2025 API Reality Check

Reddit changed the game in late 2024/early 2025. The "Responsible Builder Policy" killed self-service API access. You now need explicit approval for any OAuth tokens. This isn't optional — try to spin up a quick script with PRAW using defaults and you'll hit a wall.

Here's what actually works now:

1. **Get your app approved first** — No way around this anymore. Submit a request, wait (usually 2-5 business days in my experience), get your client_id/client_secret.

2. **Your User-Agent matters** — Reddit is actively filtering. `praw/7.7.1` gets you 403'd instantly. You need something that signals legitimate use.

3. **Script apps are the sweet spot** — For read-only data collection, the "Script" app type with Client Credentials (no user password) is the most approvable path. You're not impersonating anyone, just collecting public posts.

4. **Have a real callback URL** — `localhost` apps get scrutinized harder. A deployed Vercel endpoint signals you're building infrastructure, not a throwaway scraper.

## Setup

### 1. Reddit App Approval

Go to https://www.reddit.com/prefs/apps and create an app **after** you've read the Responsible Builder Policy. Use these values:

| Field | What to put |
|-------|-------------|
| **name** | `Infra_Telemetry_Harvester` |
| **description** | Something professional that explains *why* you need this. I used: "Automated monitoring of infrastructure-related community incident reports for SRE audit trails." |
| **type** | `Script` |
| **redirect URI** | Your Vercel URL + `/api/telemetry/callback` |

Save the client ID (the string under the app name) and client secret.

### 2. Deploy the callback endpoint

```bash
npm i -g vercel  # if you haven't already
vercel --prod
```

Grab the production URL. Mine ended up being `https://infra-telemetry-harvester.vercel.app`. Update your Reddit app with the full callback path: `https://your-app.vercel.app/api/telemetry/callback`

### 3. GitHub Actions (optional but recommended)

Running this from GitHub's IPs instead of your home connection adds legitimacy. Reddit sees requests coming from known infrastructure ranges rather than residential ISP blocks.

```bash
gh repo create infra-telemetry-harvester --public
gh secret set REDDIT_CLIENT_ID
gh secret set REDDIT_CLIENT_SECRET
```

The workflow runs every 30 minutes. You can adjust this in `.github/workflows/harvest.yml` but I'd recommend staying conservative. Reddit's rate limits are technically 100 requests/minute for OAuth apps, but there's a difference between "technically allowed" and "actually tolerated."

## Usage

### Local testing

```bash
pip install -r requirements.txt
export REDDIT_CLIENT_ID="your_id"
export REDDIT_CLIENT_SECRET="your_secret"
python scripts/harvester.py
```

Data lands in `scripts/data/harvest_*.json`. Each run gets timestamped.

### What's actually being collected

The harvester pulls top posts from the last 24 hours across:
- r/GoogleCloud, r/aws, r/Azure — the big three cloud providers
- r/devops, r/kubernetes, r/sysadmin, r/SRE — operational context
- r/ClaudeAI, r/OpenAI, r/MachineLearning — emerging AI infra signals

Why these? Because when Lambda cold starts spike or GPT-4's API latency jumps, someone posts about it here before anywhere else. The data is public, read-only, and we're not touching comments or user data — just post metadata and titles.

## Rate limiting & being a good citizen

PRAW handles the OAuth token refresh and respects the `X-Ratelimit-*` headers automatically. I've added a 2-second sleep between subreddits just to be extra polite.

The User-Agent string is intentionally verbose:
```
InfraTelemetryHarvester/1.0 (Enterprise SRE Monitoring; Contact: sre-team@company.internal; Purpose: Infrastructure Incident Research)
```

This isn't about being sneaky — it's about being transparent. If Reddit's abuse team looks at this, they immediately see: legitimate enterprise use, contact point, specific non-abusive purpose.

## Data retention

The harvester only grabs post titles, scores, timestamps, and truncated selftext (first 1000 chars). No comments, no user PMs, no voting. JSON files are saved locally and optionally committed to the repo.

Per Reddit's policy for researchers (which this arguably falls under): "retain copies of data beyond what is strictly necessary for the immediate research project." I delete files older than 30 days. Adjust to your compliance needs.

## Troubleshooting

**403 Forbidden on every request**
Your app probably isn't approved yet. Check your email for the Reddit approval notification. Until then, all API calls fail.

**Rate limit warnings in logs**
The harvester slows down automatically. If you're seeing this consistently, increase the sleep delay in `harvester.py` or reduce the number of subreddits.

**"Unauthorized" errors**
Double-check your client ID and secret. The client ID is the 14-character string *under* the app name in Reddit prefs, not the app's display name.

## Why not just use the official API pricing?

Reddit's API pricing is designed for apps with users. If you're building a client app that displays content to humans, you need to pay. This harvester is different — it's machine-to-machine, no user interface, no content display. Think of it like an RSS reader that happens to use OAuth.

That said, if your use case grows beyond personal/team SRE monitoring, you'll need to talk to Reddit about commercial terms. Don't be the person who ruins API access for everyone else.

## Contributing

This is a personal tool that I open-sourced because the 2025 API approval process is painful and opaque. If you find a better way to structure the approval request, or discover new rate limit behaviors, PRs welcome.

## License

MIT — use at your own risk, follow Reddit's policies, don't be abusive.

---

*Built with PRAW, caffeine, and the frustration of finding out about outages from Twitter instead of official channels.*
