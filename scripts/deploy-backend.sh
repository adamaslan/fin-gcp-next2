#!/bin/bash
# Deploy MCP Backend to Google Cloud Run
set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-ttb-lang1}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="technical-analysis-api"

echo "🚀 Deploying MCP Backend to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE"
echo ""

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../mcp-finance1/cloud-run"

# Deploy to Cloud Run
gcloud run deploy $SERVICE \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID" \
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
echo "✅ Backend deployed successfully!"
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test with:"
echo "  curl $SERVICE_URL/health"
echo ""
echo "To deploy frontend, run:"
echo "  export MCP_CLOUD_RUN_URL=$SERVICE_URL"
echo "  ./scripts/deploy-frontend.sh"
