---
name: db-seed
description: Populate database with test data for development including users, stocks, and transactions
---

Seed the MCP Finance database with realistic test data for development.

## Prerequisites

Ensure database is migrated and accessible:
```bash
cd nextjs-mcp-finance
npx drizzle-kit status
```

## Step 1: Create Seed Script

Create `scripts/seed-db.ts`:

```typescript
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { users, stocks, transactions, favorites } from '@/lib/db/schema';

const connectionString = process.env.DATABASE_URL!;
const sql = postgres(connectionString);
const db = drizzle(sql);

async function seed() {
  console.log('🌱 Seeding database...');

  // Clear existing data (development only!)
  console.log('Clearing existing data...');
  await db.delete(transactions);
  await db.delete(favorites);
  await db.delete(stocks);
  await db.delete(users);

  // Seed users
  console.log('Seeding users...');
  const testUsers = await db.insert(users).values([
    {
      id: 'user_test1',
      email: 'test1@example.com',
      name: 'Test User 1',
      createdAt: new Date(),
      updatedAt: new Date(),
    },
    {
      id: 'user_test2',
      email: 'test2@example.com',
      name: 'Test User 2',
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  ]).returning();

  // Seed stocks
  console.log('Seeding stocks...');
  const testStocks = await db.insert(stocks).values([
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: '150.25',
      change: '1.25',
      changePercent: '0.84',
      marketCap: '2500000000000',
      volume: '75000000',
      updatedAt: new Date(),
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      price: '140.50',
      change: '-0.75',
      changePercent: '-0.53',
      marketCap: '1800000000000',
      volume: '25000000',
      updatedAt: new Date(),
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      price: '380.00',
      change: '2.50',
      changePercent: '0.66',
      marketCap: '2800000000000',
      volume: '30000000',
      updatedAt: new Date(),
    },
  ]).returning();

  // Seed transactions
  console.log('Seeding transactions...');
  await db.insert(transactions).values([
    {
      userId: testUsers[0].id,
      symbol: 'AAPL',
      type: 'buy',
      quantity: 10,
      price: '148.00',
      total: '1480.00',
      createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
    },
    {
      userId: testUsers[0].id,
      symbol: 'GOOGL',
      type: 'buy',
      quantity: 5,
      price: '138.00',
      total: '690.00',
      createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
    },
    {
      userId: testUsers[1].id,
      symbol: 'MSFT',
      type: 'buy',
      quantity: 8,
      price: '375.00',
      total: '3000.00',
      createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
    },
  ]);

  // Seed favorites
  console.log('Seeding favorites...');
  await db.insert(favorites).values([
    {
      userId: testUsers[0].id,
      symbol: 'AAPL',
      createdAt: new Date(),
    },
    {
      userId: testUsers[0].id,
      symbol: 'MSFT',
      createdAt: new Date(),
    },
  ]);

  console.log('✅ Database seeded successfully!');
  await sql.end();
}

seed().catch((error) => {
  console.error('❌ Seeding failed:', error);
  process.exit(1);
});
```

## Step 2: Add Script to package.json

```json
{
  "scripts": {
    "db:seed": "tsx scripts/seed-db.ts"
  }
}
```

## Step 3: Run Seed Script

```bash
cd nextjs-mcp-finance
npm run db:seed
```

**Expected Output:**
```
🌱 Seeding database...
Clearing existing data...
Seeding users...
Seeding stocks...
Seeding transactions...
Seeding favorites...
✅ Database seeded successfully!
```

## Step 4: Verify Seeded Data

```bash
# Open Drizzle Studio
npx drizzle-kit studio
```

Or query directly:
```bash
node -e "
const { drizzle } = require('drizzle-orm/postgres-js');
const postgres = require('postgres');
const sql = postgres(process.env.DATABASE_URL);
const db = drizzle(sql);

db.query.users.findMany().then(users => {
  console.log('Users:', users.length);
  sql.end();
});
"
```

## Seed Data Contents

### Users (2)
- `test1@example.com` - Test User 1
- `test2@example.com` - Test User 2

### Stocks (3)
- AAPL - Apple Inc.
- GOOGL - Alphabet Inc.
- MSFT - Microsoft Corporation

### Transactions (3)
- User 1: Bought 10 AAPL @ $148
- User 1: Bought 5 GOOGL @ $138
- User 2: Bought 8 MSFT @ $375

### Favorites (2)
- User 1 favorites: AAPL, MSFT

## Advanced Seeding

### Seed More Data

Modify the script to add more records:
```typescript
// Generate 100 transactions
for (let i = 0; i < 100; i++) {
  await db.insert(transactions).values({
    userId: testUsers[i % 2].id,
    symbol: ['AAPL', 'GOOGL', 'MSFT'][i % 3],
    type: i % 2 === 0 ? 'buy' : 'sell',
    quantity: Math.floor(Math.random() * 50) + 1,
    price: (Math.random() * 200 + 100).toFixed(2),
    total: '0', // Calculate based on quantity * price
    createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
  });
}
```

### Seed from CSV

```typescript
import { readFileSync } from 'fs';

const csvData = readFileSync('data/stocks.csv', 'utf-8');
const lines = csvData.split('\n').slice(1); // Skip header

for (const line of lines) {
  const [symbol, name, price] = line.split(',');
  await db.insert(stocks).values({
    symbol,
    name,
    price,
    // ... other fields
  });
}
```

## Seed Different Environments

### Development
```bash
DATABASE_URL="postgresql://localhost/mcp_finance_dev" npm run db:seed
```

### Testing
```bash
DATABASE_URL="postgresql://localhost/mcp_finance_test" npm run db:seed
```

### Staging
```bash
DATABASE_URL=$STAGING_DATABASE_URL npm run db:seed
```

**⚠️ NEVER seed production database!**

## Reset and Reseed

```bash
# Reset database and reseed
npm run db:reset && npm run db:migrate && npm run db:seed
```

## Common Issues

### "Cannot connect to database"
- Check `DATABASE_URL` in `.env.local`
- Ensure PostgreSQL is running
- Verify database exists

### "Table does not exist"
- Run migrations first: `npm run db:migrate`
- Check schema is up to date

### "Duplicate key error"
- Clear existing data first
- Or use `ON CONFLICT` in insert statements

### "Permission denied"
- Database user needs INSERT permissions
- Grant permissions: `GRANT ALL ON DATABASE mcp_finance TO your_user;`

## Best Practices

### For Development
- ✅ Seed realistic test data
- ✅ Include edge cases
- ✅ Vary creation dates
- ✅ Include different user types

### For Testing
- ✅ Seed minimal necessary data
- ✅ Keep data consistent
- ✅ Reset before each test run
- ✅ Use factories/fixtures

### For Production
- ❌ NEVER seed production
- ❌ NEVER clear production data
- ✅ Use migrations for schema
- ✅ Use admin tools for data

## Seed Script Checklist

- [ ] Script is idempotent (safe to run multiple times)
- [ ] Clears existing test data
- [ ] Seeds users
- [ ] Seeds stocks
- [ ] Seeds transactions
- [ ] Seeds relationships (favorites)
- [ ] Logs progress
- [ ] Handles errors
- [ ] Verifies results

---

**Pro Tip**: Create different seed scripts for different scenarios (minimal, full, edge-cases) and run them as needed during development.
