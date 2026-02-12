---
name: api-test
description: Test API endpoints for MCP Finance app including authentication, data validation, and error handling. Use when testing APIs, debugging endpoints, or when user mentions API testing, endpoint testing, or API issues.
allowed-tools: Read, Bash(curl *), Bash(node *)
---

# API Testing Skill

When testing APIs for MCP Finance, follow this systematic approach.

## API Endpoints to Test

### Authentication Endpoints
- `POST /api/auth/sign-up` - User registration
- `POST /api/auth/sign-in` - User login
- `POST /api/auth/sign-out` - User logout
- `GET /api/auth/me` - Current user info

### Stock Endpoints
- `GET /api/stocks` - List all stocks
- `GET /api/stocks/[symbol]` - Get specific stock
- `POST /api/stocks/favorite` - Add favorite stock
- `DELETE /api/stocks/favorite/[id]` - Remove favorite

### Transaction Endpoints
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/[id]` - Get transaction details

### Webhook Endpoints
- `POST /api/webhooks/clerk` - Clerk webhooks
- `POST /api/webhooks/stripe` - Stripe webhooks

## Testing Approach

### 1. Start Dev Server
```bash
cd nextjs-mcp-finance
npm run dev
```

Wait for server to start (usually at http://localhost:3000).

### 2. Test Health Endpoint
```bash
curl http://localhost:3000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-18T..."
}
```

### 3. Test Authentication Required Endpoints

**Test without auth (should fail):**
```bash
curl -X GET http://localhost:3000/api/transactions \
  -H "Content-Type: application/json"
```

**Expected Response:**
```
Unauthorized (401)
```

**Test with auth:**
First, sign in via browser, get session cookie, then:
```bash
curl -X GET http://localhost:3000/api/transactions \
  -H "Content-Type: application/json" \
  -H "Cookie: __session=YOUR_SESSION_COOKIE"
```

### 4. Test POST Endpoints

**Create Transaction:**
```bash
curl -X POST http://localhost:3000/api/transactions \
  -H "Content-Type: application/json" \
  -H "Cookie: __session=YOUR_SESSION_COOKIE" \
  -d '{
    "symbol": "AAPL",
    "quantity": 10,
    "price": 150.00,
    "type": "buy"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": "...",
    "symbol": "AAPL",
    "quantity": 10,
    "price": "150.00",
    "type": "buy",
    "createdAt": "..."
  }
}
```

### 5. Test Error Handling

**Invalid Data:**
```bash
curl -X POST http://localhost:3000/api/transactions \
  -H "Content-Type: application/json" \
  -H "Cookie: __session=YOUR_SESSION_COOKIE" \
  -d '{
    "symbol": "INVALID",
    "quantity": -10
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "error": "Invalid transaction data"
}
```

**Missing Required Fields:**
```bash
curl -X POST http://localhost:3000/api/transactions \
  -H "Content-Type: application/json" \
  -H "Cookie: __session=YOUR_SESSION_COOKIE" \
  -d '{}'
```

### 6. Test Rate Limiting (if implemented)

Send multiple rapid requests:
```bash
for i in {1..20}; do
  curl -X GET http://localhost:3000/api/stocks
done
```

Check for 429 (Too Many Requests) responses.

## Automated API Testing Script

Create a test script:

```javascript
// test-api.js
const BASE_URL = 'http://localhost:3000';

async function testEndpoint(method, path, data = null, headers = {}) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${BASE_URL}${path}`, options);
    const json = await response.json();

    console.log(`${method} ${path}: ${response.status}`);
    console.log('Response:', json);

    return { status: response.status, data: json };
  } catch (error) {
    console.error(`Error testing ${path}:`, error.message);
    return { status: 0, error: error.message };
  }
}

async function runTests() {
  console.log('🧪 Starting API Tests\n');

  // Test health endpoint
  await testEndpoint('GET', '/api/health');

  // Test unauthenticated request (should fail)
  await testEndpoint('GET', '/api/transactions');

  // Add more tests here...

  console.log('\n✅ Tests complete');
}

runTests();
```

**Run it:**
```bash
node test-api.js
```

## Checklist for Each Endpoint

- [ ] **Returns correct status code**
  - 200 for successful GET
  - 201 for successful POST (created)
  - 400 for bad request
  - 401 for unauthorized
  - 404 for not found
  - 500 for server error

- [ ] **Response format is consistent**
  ```json
  {
    "success": boolean,
    "data": object | array,
    "error": string (if success: false)
  }
  ```

- [ ] **Authentication enforced**
  - Protected endpoints check auth
  - Returns 401 if not authenticated

- [ ] **Input validation works**
  - Invalid data rejected
  - Clear error messages
  - SQL injection prevented

- [ ] **Error handling is graceful**
  - No stack traces exposed
  - User-friendly messages
  - Proper logging

- [ ] **Performance is acceptable**
  - Response time < 500ms for simple queries
  - Response time < 2s for complex queries

## Common API Issues

### Issue: CORS Errors
```
Access-Control-Allow-Origin error
```

**Solution:** Check Next.js API route configuration:
```typescript
export async function GET(request: Request) {
  return Response.json(data, {
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  });
}
```

### Issue: 500 Internal Server Error
**Debug:**
```bash
# Check server logs
cd nextjs-mcp-finance
npm run dev
# Watch for errors in console
```

### Issue: Slow Response Times
**Profile:**
```bash
# Use curl with timing
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3000/api/stocks
```

**curl-format.txt:**
```
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer:  %{time_pretransfer}\n
time_redirect:  %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
```

## Integration with E2E Tests

API tests complement E2E tests:
- **E2E Tests** (`npm run test:e2e`): Test user flows
- **API Tests** (this skill): Test endpoints directly

Both should pass before deployment.

## Quick API Test Commands

```bash
# Health check
curl http://localhost:3000/api/health

# List stocks (public endpoint)
curl http://localhost:3000/api/stocks | jq

# Get specific stock
curl http://localhost:3000/api/stocks/AAPL | jq

# Test with verbose output
curl -v http://localhost:3000/api/health

# Save response to file
curl http://localhost:3000/api/stocks > response.json
```

---

**Pro Tip**: Use tools like Postman or Insomnia for interactive API testing during development.
