# Cloud Run Environment Variables Guide

How to set, update, and manage environment variables for the **options-mcp-backend** service on Google Cloud Run.

## Quick Reference

| Variable | Purpose | Required By |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Gemini AI analysis | `/api/options-ai`, `/api/spread-trade` (AI), `/api/options-enhanced` (with AI) |
| `FINHUB_API_KEY` | Finnhub market data | `/api/pipeline/run`, `/api/pipeline/run-single` |
| `GCP_PROJECT_ID` | Firestore project | `/api/options-enhanced`, `/api/pipeline/*` |

---

## Option 1: Terminal (gcloud CLI)

### Prerequisites

```bash
# Install gcloud CLI (if not installed)
# macOS:
brew install google-cloud-sdk

# Verify installation
gcloud --version

# Login
gcloud auth login

# Set default project
gcloud config set project ttb-lang1
```

### Set Environment Variables

**Set all env vars at once:**

```bash
gcloud run services update options-mcp-backend \
  --project=ttb-lang1 \
  --region=us-central1 \
  --set-env-vars="GEMINI_API_KEY=your-key-here,FINHUB_API_KEY=your-key-here,GCP_PROJECT_ID=ttb-lang1"
```

> **Warning:** `--set-env-vars` replaces ALL env vars. Any existing vars not included will be removed.

**Add or update a single env var (keeps existing ones):**

```bash
gcloud run services update options-mcp-backend \
  --project=ttb-lang1 \
  --region=us-central1 \
  --update-env-vars="GEMINI_API_KEY=new-key-here"
```

**Add multiple without wiping existing:**

```bash
gcloud run services update options-mcp-backend \
  --project=ttb-lang1 \
  --region=us-central1 \
  --update-env-vars="GEMINI_API_KEY=your-key,FINHUB_API_KEY=your-key"
```

**Remove a specific env var:**

```bash
gcloud run services update options-mcp-backend \
  --project=ttb-lang1 \
  --region=us-central1 \
  --remove-env-vars="FINHUB_API_KEY"
```

### View Current Environment Variables

```bash
gcloud run services describe options-mcp-backend \
  --project=ttb-lang1 \
  --region=us-central1 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

**Compact view (key=value pairs):**

```bash
gcloud run services describe options-mcp-backend \
  --project=ttb-lang1 \
  --region=us-central1 \
  --format="table(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"
```

### Deploy with Env Vars (One Command)

When deploying from source, include env vars so they persist:

```bash
gcloud run deploy options-mcp-backend \
  --project=ttb-lang1 \
  --region=us-central1 \
  --source=./nubackend1 \
  --set-env-vars="GEMINI_API_KEY=your-key,FINHUB_API_KEY=your-key,GCP_PROJECT_ID=ttb-lang1" \
  --allow-unauthenticated
```

Or use the included deploy script which reads from `.env.cloud-run`:

```bash
bash nubackend1/deploy.sh
```

### Verify After Setting

```bash
# Check the service root (shows ai_available and pipeline_available flags)
curl -s https://options-mcp-backend-cif7ppahzq-uc.a.run.app/

# Expected response when all env vars are set:
# {
#   "service": "Options MCP Backend",
#   "version": "2.0.0",
#   "status": "healthy",
#   "mcp_available": true,
#   "ai_available": true,        <-- GEMINI_API_KEY is set
#   "pipeline_available": true   <-- FINHUB_API_KEY is set
# }
```

---

## Option 2: Google Cloud Console (Browser)

### Step 1: Open Cloud Run

Go to: **https://console.cloud.google.com/run?project=ttb-lang1**

Or navigate manually:
1. Open https://console.cloud.google.com
2. Select project **ttb-lang1** from the dropdown at the top
3. In the left sidebar, click **Cloud Run** (under Serverless)

### Step 2: Select the Service

1. You will see a list of Cloud Run services
2. Click on **options-mcp-backend**

### Step 3: Edit & Deploy New Revision

1. Click the **"Edit & Deploy New Revision"** button at the top

### Step 4: Add Environment Variables

1. Scroll down to the **"Container(s)"** section
2. Click on the container tab (or expand it)
3. Scroll down to find **"Environment variables"**
4. Click **"+ Add Variable"** for each:

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | `AIzaSy...` (your Gemini key) |
| `FINHUB_API_KEY` | `d66cl2...` (your Finnhub key) |
| `GCP_PROJECT_ID` | `ttb-lang1` |

5. Click **"Deploy"** at the bottom

### Step 5: Verify

1. After deployment completes (green checkmark), click the **service URL** at the top
2. You should see the JSON with `"ai_available": true` and `"pipeline_available": true`

### Editing Existing Variables

1. Go to the service page: **Cloud Run > options-mcp-backend**
2. Click **"Edit & Deploy New Revision"**
3. Scroll to **Environment variables**
4. Edit the value of any existing variable
5. Click **Deploy**

### Viewing Current Variables

1. Go to **Cloud Run > options-mcp-backend**
2. Click the **"Revisions"** tab
3. Click on the active revision (the one serving traffic)
4. Scroll to the **"Container"** section
5. Environment variables are listed there

---

## Key Differences: `--set-env-vars` vs `--update-env-vars`

| Flag | Behavior | When to Use |
|------|----------|-------------|
| `--set-env-vars` | **Replaces all** env vars | Fresh deploy, setting everything from scratch |
| `--update-env-vars` | **Adds/updates** specified vars, keeps the rest | Adding a new key or changing one value |
| `--remove-env-vars` | **Removes** specified vars, keeps the rest | Removing a key you no longer need |

**Example scenario:**

```bash
# Current state: GEMINI_API_KEY=old, FINHUB_API_KEY=abc, GCP_PROJECT_ID=ttb-lang1

# This REMOVES FINHUB_API_KEY and GCP_PROJECT_ID (they're not included):
gcloud run services update options-mcp-backend \
  --set-env-vars="GEMINI_API_KEY=new"
# Result: only GEMINI_API_KEY=new

# This KEEPS FINHUB_API_KEY and GCP_PROJECT_ID:
gcloud run services update options-mcp-backend \
  --update-env-vars="GEMINI_API_KEY=new"
# Result: GEMINI_API_KEY=new, FINHUB_API_KEY=abc, GCP_PROJECT_ID=ttb-lang1
```

**Rule of thumb:** Use `--update-env-vars` unless you want to reset everything.

---

## Automated Deploy Script

The repo includes `nubackend1/deploy.sh` which reads secrets from `.env.cloud-run`:

**Setup (one time):**

```bash
# Create the env file (already gitignored via .env.* pattern)
cat > nubackend1/.env.cloud-run << 'EOF'
GEMINI_API_KEY=your-gemini-key
FINHUB_API_KEY=your-finnhub-key
GCP_PROJECT_ID=ttb-lang1
EOF
```

**Deploy:**

```bash
bash nubackend1/deploy.sh
```

This runs `gcloud run deploy` with `--set-env-vars` sourced from the file, so env vars are always included with every deploy.

---

## Troubleshooting

### "ai_available: false" after deploy

The deploy wiped your env vars. Fix:

```bash
gcloud run services update options-mcp-backend \
  --project=ttb-lang1 --region=us-central1 \
  --update-env-vars="GEMINI_API_KEY=your-key-here"
```

Or redeploy with `bash deploy.sh`.

### "pipeline_available: false"

Either `FINHUB_API_KEY` is not set, or the `finnhub-python` package is missing from `environment.yml`.

Check env vars:
```bash
gcloud run services describe options-mcp-backend \
  --project=ttb-lang1 --region=us-central1 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

Check logs:
```bash
gcloud run services logs read options-mcp-backend \
  --project=ttb-lang1 --region=us-central1 --limit=20
```

### "404 models/gemini-2.0-flash-exp is not found"

The Gemini model name is outdated. Update `src/options_mcp/config.py`:

```python
GEMINI_MODEL: Final[str] = "gemini-2.0-flash"  # not "gemini-2.0-flash-exp"
```

Then redeploy.

### Env vars visible in console but service not using them

Cloud Run creates a new **revision** when you change env vars. Make sure the new revision is serving traffic:

1. Go to **Cloud Run > options-mcp-backend > Revisions**
2. The latest revision should show **100%** traffic
3. If not, click **Manage Traffic** and route 100% to the latest revision
