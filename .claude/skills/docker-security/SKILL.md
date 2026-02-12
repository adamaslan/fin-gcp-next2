---
name: docker-security
description: Docker and container security best practices for MCP Finance including non-root users, minimal images, mamba integration, and security hardening. Use when creating Dockerfiles, containerizing applications, or when user mentions Docker, containers, or container security.
allowed-tools: Read, Write, Edit, Bash(docker *)
---

# Docker Security Best Practices

When creating Docker containers for MCP Finance, follow these security-first principles.

## Core Security Principles

### 1. **ALWAYS Run as Non-Root User**

Running containers as root is a critical security risk. If a container is compromised, the attacker has root access.

### 2. **Use Minimal Base Images**

Smaller images = smaller attack surface. Use slim/alpine variants when possible.

### 3. **Use Micromamba for Python**

Micromamba is perfect for containers - statically linked, no dependencies, faster startup.

### 4. **Multi-Stage Builds**

Separate build and runtime stages to minimize final image size.

### 5. **Scan for Vulnerabilities**

Always scan images before deployment.

---

## MCP Backend (Python) - Secure Dockerfile

### Using Micromamba (Recommended)

```dockerfile
# Stage 1: Build stage
FROM mambaorg/micromamba:1.5.6 as builder

# Copy environment file
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml

# Create environment
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Stage 2: Runtime stage
FROM mambaorg/micromamba:1.5.6

# Copy installed environment from builder
COPY --from=builder /opt/conda /opt/conda

# Set working directory
WORKDIR /app

# Copy application files with correct ownership
# CRITICAL: --chown ensures non-root ownership
COPY --chown=$MAMBA_USER:$MAMBA_USER . /app

# Container runs as 'mambauser' (UID 1000) by default - NOT ROOT
# The base image already sets USER mambauser

# Expose port (non-privileged port > 1024)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python3", "main.py"]
```

### Alternative: Minimal Python with Non-Root User

```dockerfile
# Use slim Python image (smaller than full python:3.11)
FROM python:3.11-slim as builder

# Install micromamba
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba && \
    mv bin/micromamba /usr/local/bin/ && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy environment file
COPY environment.yml /tmp/environment.yml

# Create environment
RUN micromamba create -y -f /tmp/environment.yml -p /opt/conda && \
    micromamba clean --all --yes

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user and group
# CRITICAL: This reduces attack surface
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 appuser

# Copy conda environment from builder
COPY --from=builder /opt/conda /opt/conda

# Set environment PATH
ENV PATH="/opt/conda/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application files with correct ownership
# CRITICAL: --chown=appuser:appuser
COPY --chown=appuser:appuser . /app

# Switch to non-root user
# CRITICAL: All subsequent commands run as appuser
USER appuser

# Expose non-privileged port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python3", "main.py"]
```

---

## Frontend (Next.js) - Secure Dockerfile

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps

# Install libc6-compat for Alpine
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build Next.js app
RUN npm run build

# Stage 3: Runner (FINAL STAGE - MINIMAL & SECURE)
FROM node:20-alpine AS runner

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

# Set to production
ENV NODE_ENV=production

# Copy necessary files only
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run Next.js
CMD ["node", "server.js"]
```

---

## Security Checklist

### ✅ User & Permissions
- [ ] **Run as non-root user** (UID > 1000)
- [ ] **Use --chown when copying files**
- [ ] **Set USER directive before CMD**
- [ ] **Use non-privileged ports (> 1024)**
- [ ] **Read-only filesystem where possible**

### ✅ Image Security
- [ ] **Use official base images**
- [ ] **Use specific version tags (not :latest)**
- [ ] **Multi-stage builds to minimize size**
- [ ] **Scan images for vulnerabilities**
- [ ] **Sign images**

### ✅ Secrets Management
- [ ] **Never hardcode secrets in Dockerfile**
- [ ] **Use build secrets (--secret)**
- [ ] **Pass secrets via environment at runtime**
- [ ] **Use secrets management tools (Vault, etc.)**

### ✅ Network Security
- [ ] **Minimize exposed ports**
- [ ] **Use HEALTHCHECK directives**
- [ ] **Configure network policies**
- [ ] **Use TLS for communication**

### ✅ Dependencies
- [ ] **Pin versions in environment.yml**
- [ ] **Use conda-lock for reproducibility**
- [ ] **Remove build dependencies in final stage**
- [ ] **Clean package caches**

---

## Docker Compose with Security

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./mcp-finance1/cloud-run
      dockerfile: Dockerfile
    # Run as non-root
    user: "1000:1000"
    # Read-only root filesystem
    read_only: true
    # Temp directories (writable)
    tmpfs:
      - /tmp
      - /app/tmp
    # Drop all capabilities
    cap_drop:
      - ALL
    # No new privileges
    security_opt:
      - no-new-privileges:true
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    # Environment from file (not in docker-compose.yml)
    env_file:
      - .env
    ports:
      - "8000:8000"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  frontend:
    build:
      context: ./nextjs-mcp-finance
      dockerfile: Dockerfile
    user: "1001:1001"
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    env_file:
      - .env
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    # Run as postgres user (not root)
    user: postgres
    environment:
      POSTGRES_DB: mcp_finance
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
    driver: local
```

---

## Security Scanning

### Scan Images Before Deployment

```bash
# Using Trivy (recommended)
trivy image mcp-finance-backend:latest

# Using Docker Scout
docker scout cves mcp-finance-backend:latest

# Using Snyk
snyk container test mcp-finance-backend:latest
```

### Scan in CI/CD

```yaml
# GitHub Actions example
- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'mcp-finance-backend:latest'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

---

## Build Secrets (Don't Commit!)

```dockerfile
# Use build secrets for sensitive data during build
# Secrets are not stored in image layers

FROM python:3.11-slim

# Mount secret at build time
RUN --mount=type=secret,id=pip_token \
    PIP_TOKEN=$(cat /run/secrets/pip_token) && \
    pip install --index-url=https://token:${PIP_TOKEN}@pypi.example.com package
```

Build with secret:
```bash
docker build --secret id=pip_token,src=./pip-token.txt .
```

---

## Common Security Mistakes

### ❌ WRONG: Running as Root
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
CMD ["python", "main.py"]  # Runs as root!
```

### ✅ CORRECT: Non-Root User
```dockerfile
FROM python:3.11
RUN useradd -r -u 1000 appuser
WORKDIR /app
COPY --chown=appuser:appuser . .
USER appuser
CMD ["python", "main.py"]  # Runs as appuser
```

### ❌ WRONG: Hardcoded Secrets
```dockerfile
ENV API_KEY=sk_live_abc123  # NEVER DO THIS!
```

### ✅ CORRECT: Runtime Secrets
```dockerfile
# Pass at runtime
# docker run -e API_KEY=${API_KEY} image
```

### ❌ WRONG: Latest Tag
```dockerfile
FROM python:latest  # Unpredictable!
```

### ✅ CORRECT: Specific Version
```dockerfile
FROM python:3.11-slim  # Reproducible
```

---

## Testing Container Security

```bash
# Test running as non-root
docker run --rm mcp-finance-backend:latest whoami
# Should output: appuser (not root!)

# Test file permissions
docker run --rm mcp-finance-backend:latest ls -la /app
# Should show appuser:appuser ownership

# Test write access to root filesystem
docker run --rm mcp-finance-backend:latest touch /test
# Should fail with permission denied (good!)

# Inspect user
docker inspect mcp-finance-backend:latest | jq '.[0].Config.User'
# Should output: "1000" or "appuser"
```

---

## Production Deployment Checklist

- [ ] Images built with non-root user
- [ ] All secrets passed via environment (not in image)
- [ ] Images scanned for vulnerabilities
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Network policies configured
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Backup strategy in place
- [ ] Rollback plan ready

---

## Resources

### Security Tools
- **Trivy**: Container vulnerability scanner
- **Docker Scout**: Docker's built-in scanning
- **Snyk**: Security platform for containers
- **Falco**: Runtime security monitoring

### Best Practices
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

**Remember**: Security is not optional. Always run containers as non-root users and scan for vulnerabilities before deploying to production!
