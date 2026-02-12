#!/bin/bash
# Deploy Next.js Frontend to Google Cloud Run
set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-ttb-lang1}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="mcp-finance-frontend"
BACKEND_URL="${MCP_CLOUD_RUN_URL}"

# Validate backend URL is set
if [ -z "$BACKEND_URL" ]; then
    echo "❌ Error: MCP_CLOUD_RUN_URL is not set"
    echo ""
    echo "Please set the backend URL before deploying:"
    echo "  export MCP_CLOUD_RUN_URL=https://your-backend-url.run.app"
    echo ""
    echo "Or deploy backend first:"
    echo "  ./scripts/deploy-backend.sh"
    exit 1
fi

echo "🚀 Deploying Next.js Frontend to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE"
echo "   Backend URL: $BACKEND_URL"
echo ""

# Navigate to frontend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../nextjs-mcp-finance"

# Build environment variables string
ENV_VARS="MCP_CLOUD_RUN_URL=$BACKEND_URL,NODE_ENV=production"

# Add Clerk keys if available
if [ -n "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" ]; then
    ENV_VARS="$ENV_VARS,NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"
fi
if [ -n "$CLERK_SECRET_KEY" ]; then
    ENV_VARS="$ENV_VARS,CLERK_SECRET_KEY=$CLERK_SECRET_KEY"
fi

# Deploy to Cloud Run
gcloud run deploy $SERVICE \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --set-env-vars="$ENV_VARS" \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --quiet

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE \
    --region $REGION \
    --project $PROJECT_ID \
    --format='value(status.url)')

echo ""
echo "✅ Frontend deployed successfully!"
echo ""
echo "Frontend URL: $SERVICE_URL"
echo "Backend URL: $BACKEND_URL"
echo ""
echo "Open in browser:"
echo "  open $SERVICE_URL"
