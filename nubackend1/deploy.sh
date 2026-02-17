#!/bin/bash
# Deploy options-mcp-backend to Cloud Run with env vars
# Usage: bash deploy.sh

set -euo pipefail

PROJECT="ttb-lang1"
SERVICE="options-mcp-backend"
REGION="us-central1"
ENV_FILE="$(dirname "$0")/.env.cloud-run"

# Load env vars from file
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found. Create it with your secrets."
  echo "Required keys: GEMINI_API_KEY, FINHUB_API_KEY, GCP_PROJECT_ID"
  exit 1
fi

# Build comma-separated env vars string from file
ENV_VARS=""
while IFS='=' read -r key value; do
  # Skip empty lines and comments
  [[ -z "$key" || "$key" == \#* ]] && continue
  if [ -n "$ENV_VARS" ]; then
    ENV_VARS="${ENV_VARS},${key}=${value}"
  else
    ENV_VARS="${key}=${value}"
  fi
done < "$ENV_FILE"

echo "Deploying $SERVICE to $PROJECT ($REGION)..."
echo "Env vars: $(echo "$ENV_VARS" | sed 's/=[^,]*/=***/g')"

# Deploy from source with env vars baked in
gcloud run deploy "$SERVICE" \
  --project="$PROJECT" \
  --region="$REGION" \
  --source="$(dirname "$0")" \
  --set-env-vars="$ENV_VARS" \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=300 \
  --max-instances=3

echo ""
echo "Deployment complete!"
echo "Service URL: $(gcloud run services describe $SERVICE --project=$PROJECT --region=$REGION --format='value(status.url)')"
echo ""
echo "Verify: curl -s \$(gcloud run services describe $SERVICE --project=$PROJECT --region=$REGION --format='value(status.url)')/"
