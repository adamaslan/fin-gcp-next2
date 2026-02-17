# Next Steps: Options Analysis Pipeline

## 1. Connect to Next.js Frontend

Add an API route that reads from the `options_analysis` Firestore collection:

```typescript
// src/app/api/options-analysis/route.ts
import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const symbol = searchParams.get('symbol');
  const db = getFirestore();
  const doc = await db.collection('options_analysis').doc(symbol!).get();
  if (!doc.exists) return Response.json({ error: 'Not found' }, { status: 404 });
  return Response.json({ success: true, data: doc.data() });
}
```

Display in the MCP Control Center by adding an `OptionsAnalysisCard` component that fetches from this endpoint and renders risk, sentiment, IV, and vehicle recommendation.

## 2. Schedule Automated Runs

**Option A — Cloud Scheduler + Cloud Run Job:**

```bash
# Deploy run_analysis.py as a Cloud Run Job
gcloud run jobs create options-analysis \
  --source=./nubackend1 --command="python,run_analysis.py,--from-firestore"

# Schedule daily at 9:30 AM ET (market open)
gcloud scheduler jobs create http options-analysis-daily \
  --schedule="30 13 * * 1-5" --uri="CLOUD_RUN_JOB_URL" --http-method=POST
```

**Option B — GitHub Actions cron:**

```yaml
on:
  schedule:
    - cron: '30 13 * * 1-5'  # 9:30 AM ET weekdays
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - run: python run_analysis.py --from-firestore
```

## 3. Migrate to Embedded Arrays

The reader already supports both formats. To migrate storage:

```bash
# Re-run pipeline WITHOUT --store-contracts (default = embedded arrays)
cd nubackend1 && mamba activate fin-ai1
python run_pipeline.py --max-expirations 3
```

This overwrites expirations with calls/puts as arrays instead of sub-collections, reducing documents from ~4,500 to ~225. No code changes needed — `firestore_reader.py` tries embedded arrays first, falls back to sub-collections automatically.
