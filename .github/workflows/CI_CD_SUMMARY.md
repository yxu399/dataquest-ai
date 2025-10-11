# CI/CD Pipeline Summary

## Overview

DataQuest AI has a comprehensive CI/CD pipeline with automated testing, building, and deployment capabilities.

## Workflows

### 1. Backend CI (`backend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (backend files)
- Pull requests to `main` or `develop` (backend files)

**Jobs:**
1. **Lint & Format Check** (3min)
   - Ruff linting (lenient - reports but doesn't fail)
   - Ruff formatting (strict - enforced)

2. **Run Tests** (4min)
   - 56 pytest tests with PostgreSQL service
   - Advanced agent tests (optional, lenient)

3. **Type Checking** (3min)
   - mypy type checking (lenient - reports but doesn't fail)

4. **Security Scan** (3min)
   - Safety check for dependency vulnerabilities (lenient)
   - TruffleHog for secret scanning (strict)

5. **Build & Verify** (3min)
   - Verify uv.lock is up to date
   - Build verification
   - Upload artifacts

**Status:** ✅ Passing

**Strictness:**
- ✅ **Strict**: Formatting, tests, secret scanning
- ⚠️ **Lenient**: Linting, type checking, security vulnerabilities

---

### 2. Frontend CI (`frontend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (frontend files)
- Pull requests to `main` or `develop` (frontend files)

**Jobs:**
1. **Lint & Type Check** (3min)
   - ESLint (lenient)
   - TypeScript type checking (lenient)

2. **Run Tests** (1min)
   - Vitest unit tests (lenient - 2 tests passing)

3. **Security Scan** (2min)
   - npm audit (lenient)
   - TruffleHog (strict)

4. **Build & Verify** (2min)
   - Vite build (strict)
   - Verify dist output
   - Upload artifacts

**Status:** ✅ Passing

**Strictness:**
- ✅ **Strict**: Build, secret scanning
- ⚠️ **Lenient**: Linting, type checking, tests, npm audit

---

### 3. Docker Build & Push (`docker-build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Release published
- Manual trigger (workflow_dispatch)

**Jobs:**
1. **Build Backend Image** (5min)
   - Multi-stage Docker build
   - Push to GitHub Container Registry (GHCR)
   - Layer caching for faster builds

2. **Build Frontend Image** (6min)
   - Multi-stage build (Node builder + Nginx)
   - Production-optimized
   - Push to GHCR

3. **Security Scan** (3min)
   - Trivy vulnerability scanning
   - Upload results to GitHub Security

4. **Integration Test** (PR only)
   - docker-compose up
   - Health checks
   - Integration tests

**Status:** ✅ Passing

**Image Tags:**
- `main` / `develop` (branch name)
- `latest` (default branch only)
- `pr-{number}` (pull requests)
- `v{version}` (releases)
- `{branch}-{sha}` (git SHA)

**Registry:** `ghcr.io/yxu399/dataquest-ai/{backend|frontend}`

---

## CI/CD Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer Commits                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
    ┌──────▼──────┐        ┌──────▼──────┐
    │ Backend CI  │        │ Frontend CI │
    │             │        │             │
    │ • Lint      │        │ • Lint      │
    │ • Test      │        │ • Test      │
    │ • Type      │        │ • Type      │
    │ • Security  │        │ • Security  │
    │ • Build     │        │ • Build     │
    └──────┬──────┘        └──────┬──────┘
           │                       │
           └───────────┬───────────┘
                       │
              ┌────────▼────────┐
              │ Docker Build &  │
              │      Push       │
              │                 │
              │ • Build Images  │
              │ • Security Scan │
              │ • Push to GHCR  │
              └────────┬────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
   ┌──────▼──────┐          ┌──────▼──────┐
   │   Backend   │          │  Frontend   │
   │   Image     │          │   Image     │
   │             │          │             │
   │ Python +    │          │ Nginx +     │
   │ FastAPI +   │          │ React SPA   │
   │ uv          │          │             │
   └─────────────┘          └─────────────┘
```

---

## Performance

### Build Times
- **Backend CI**: ~16min total (3min per job, runs in parallel)
- **Frontend CI**: ~8min total (2min per job, runs in parallel)
- **Docker Build**: ~15min total (backend + frontend in parallel)

### Optimization
- **Layer caching**: Docker builds use GitHub Actions cache
- **Dependency caching**: npm and uv caches enabled
- **Parallel execution**: All jobs run in parallel where possible
- **Path filters**: Only run workflows when relevant files change

---

## Lenient CI Philosophy

The CI pipeline uses a **progressive strictness** approach:

### Why Lenient?
1. **Don't block development** - Allow deploys while improving code quality
2. **Incremental improvement** - Fix issues over time without stopping work
3. **Visibility** - Show all issues without failing builds
4. **Flexibility** - Focus on critical issues first

### What's Strict?
- **Formatting** - Code style must be consistent
- **Tests** - All tests must pass
- **Builds** - Application must build successfully
- **Secret scanning** - No secrets in code

### What's Lenient?
- **Linting** - Shows warnings, doesn't fail
- **Type checking** - Shows type errors, doesn't fail
- **Security vulnerabilities** - Reports issues, doesn't block
- **Missing tests** - Encourages testing, doesn't require 100% coverage

### Path to Strictness
As issues are fixed:
1. Remove `continue-on-error` flags
2. Make checks strict
3. Enforce in CI
4. Document in GitHub issues

---

## Local Development

### Backend
```bash
cd backend

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .

# Run type checking
uv run mypy app/

# Build Docker image
docker build -t dataquest-backend:local .
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Run tests
npm test              # CI mode
npm run test:watch    # Watch mode

# Lint and type check
npm run lint
npx tsc --noEmit

# Build
npm run build

# Build Docker image
docker build -t dataquest-frontend:local .
```

### Full Stack
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Artifacts

### Backend CI
- **Name**: `backend-build-{sha}`
- **Contents**: `app/`, `pyproject.toml`, `uv.lock`
- **Retention**: 7 days

### Frontend CI
- **Name**: `frontend-build-{sha}`
- **Contents**: `dist/`, `package.json`, `package-lock.json`
- **Retention**: 7 days

### Docker Images
- **Registry**: GitHub Container Registry (GHCR)
- **Public**: Yes (can be made private)
- **Retention**: Configurable per tag

---

## Security

### Secret Scanning
- **Tool**: TruffleHog
- **Scope**: All commits
- **Status**: Strict (fails on secrets found)

### Vulnerability Scanning
- **Backend**: Safety (Python dependencies)
- **Frontend**: npm audit
- **Docker**: Trivy (container images)
- **Status**: Lenient (reports but doesn't fail)

### Security Tab
- Trivy results uploaded to GitHub Security tab
- View vulnerabilities in repository Security section
- SARIF format for integration with GitHub Advanced Security

---

## Monitoring

### Workflow Status
```bash
# List recent runs
gh run list --limit 10

# View specific run
gh run view {run-id}

# View logs
gh run view {run-id} --log

# View failed jobs
gh run view {run-id} --log-failed

# Re-run failed jobs
gh run rerun {run-id} --failed
```

### Badges
Add these to README.md:
```markdown
![Backend CI](https://github.com/yxu399/dataquest-ai/actions/workflows/backend-ci.yml/badge.svg)
![Frontend CI](https://github.com/yxu399/dataquest-ai/actions/workflows/frontend-ci.yml/badge.svg)
![Docker Build](https://github.com/yxu399/dataquest-ai/actions/workflows/docker-build.yml/badge.svg)
```

---

## Future Improvements

### Short Term
- [ ] Add more frontend tests
- [ ] Fix TypeScript errors incrementally
- [ ] Add backend integration tests
- [ ] Set up code coverage reporting

### Medium Term
- [ ] Add deployment workflow (CD)
- [ ] Set up staging environment
- [ ] Add E2E tests with Playwright
- [ ] Implement semantic versioning

### Long Term
- [ ] Make all lenient checks strict
- [ ] Add performance benchmarking
- [ ] Set up continuous deployment
- [ ] Add canary deployments

---

## Troubleshooting

### Workflow Failures

**Frontend build fails:**
- Check TypeScript errors: `npm run build:check`
- Check for missing dependencies: `npm install`
- Verify dist directory is created

**Backend build fails:**
- Check uv.lock is up to date: `uv lock --check`
- Run tests locally: `uv run pytest`
- Verify Python version (3.11+)

**Docker build fails:**
- Check Dockerfile syntax
- Verify all COPY paths exist
- Test build locally: `docker build .`

**Tests fail:**
- Run tests locally first
- Check database is running (for backend)
- Verify test fixtures are correct

### Cache Issues

Clear GitHub Actions cache:
```bash
# List caches
gh cache list

# Delete specific cache
gh cache delete {cache-id}

# Delete all caches
gh cache delete --all
```

---

## Contributing

When adding new workflows:
1. Use composite actions for reusable steps
2. Add path filters to avoid unnecessary runs
3. Use caching for dependencies
4. Run jobs in parallel where possible
5. Make new checks lenient initially
6. Document in this file
7. Add tests for workflow logic

---

## Contacts

- **CI/CD Issues**: Create issue with `ci/cd` label
- **Security Issues**: Use GitHub Security Advisories
- **Questions**: Open discussion in repository

---

*Last Updated: 2025-10-11*
*Version: 1.0*
