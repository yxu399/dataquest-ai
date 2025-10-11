# CI/CD Workflows

## Overview

This directory contains GitHub Actions workflows for continuous integration and deployment of DataQuest AI.

## Reusable Actions

### Setup Frontend (`actions/setup-frontend/action.yml`)

Composite action that consolidates common setup steps for frontend jobs:
- Checks out code
- Sets up Node.js 20 with npm caching
- Installs dependencies with `npm ci`

**Benefits:**
- Reduces duplication across workflow jobs
- Ensures consistent setup across all frontend CI steps
- Single source of truth for Node.js version and cache configuration

## Workflows

### 1. Backend CI (`backend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (backend files only)
- Pull requests to `main` or `develop` (backend files only)

**Jobs:**

#### Lint & Format Check
- Runs Ruff linter for code quality
- Checks code formatting consistency
- **Status:** Lenient (temporary - see Issues)

#### Test
- Runs pytest test suite
- Runs advanced LangGraph agent tests
- Uses PostgreSQL 16 service container
- **Requirements:** `ANTHROPIC_API_KEY` secret for full test coverage

#### Security Scan
- Runs `safety` for dependency vulnerabilities
- Runs TruffleHog for secret detection
- **Status:** Lenient for safety (temporary - see Issues)

#### Type Check
- Runs mypy for static type checking
- **Status:** Lenient (temporary - see Issues)

#### Build & Verify
- Verifies `uv.lock` is up to date
- Uploads build artifacts
- **Dependencies:** Requires all previous jobs to pass

**Performance Optimizations:**
- ✅ uv global cache enabled (fast dependency installation)
- ✅ Parallel job execution
- ✅ Conditional path-based triggering

### 2. Frontend CI (`frontend-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches (frontend files only)
- Pull requests to `main` or `develop` (frontend files only)
- Changes to setup-frontend composite action

**Jobs:**

#### Lint & Type Check
- Runs ESLint for code quality
- Runs TypeScript type checking with `tsc --noEmit`
- **Status:** ESLint lenient (temporary - see Issues)

#### Test
- Runs Vitest test suite
- Automatically passes when no tests found (Vitest default behavior)
- Will enforce test passes once test files are added

#### Security Scan
- Runs `npm audit` for dependency vulnerabilities
- Runs TruffleHog for secret detection
- **Status:** Lenient for npm audit (temporary)

#### Build & Verify
- Builds production bundle with Vite
- Verifies dist directory exists
- Uploads build artifacts
- **Dependencies:** Requires all previous jobs to pass

**Performance Optimizations:**
- ✅ npm cache enabled (fast dependency installation)
- ✅ Parallel job execution
- ✅ Conditional path-based triggering
- ✅ Composite action reduces duplication

## Configuration Required

### GitHub Secrets

Add these secrets in your repository settings (Settings → Secrets and variables → Actions):

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key for LangGraph agent tests | Yes |

### GitHub Issues to Create

Before making CI strict, create these technical debt issues (see `.github-issues-to-create.md`):

1. **Fix Ruff linting errors** (Priority: Medium)
2. **Fix Ruff formatting** (Priority: Low)
3. **Add type hints and fix mypy errors** (Priority: Medium)
4. **Create `.safety-policy.yml`** (Priority: High)

Once issues are resolved, remove `continue-on-error: true` from each step.

## Making CI Strict (Roadmap)

Current state: **Lenient** (allows issues to not block PRs)

Target state: **Strict** (all checks must pass)

### Phase 1: Security (High Priority)
1. Run `uv run safety check` locally
2. Create `.safety-policy.yml` for vetted exceptions
3. Remove `continue-on-error` from security job
4. ✅ Security issues now block merges

### Phase 2: Linting & Type Checking (Medium Priority)
1. Fix all Ruff linting errors
2. Add type hints to core modules
3. Remove `continue-on-error` from lint and type-check jobs
4. ✅ Code quality issues now block merges

### Phase 3: Formatting (Low Priority)
1. Run `uv run ruff format .`
2. Commit formatted code
3. Remove `continue-on-error` from format check
4. ✅ Formatting enforced

## Local Development

### Backend - Run checks locally before pushing:

```bash
cd backend

# Linting
uv run ruff check .

# Formatting
uv run ruff format --check .

# Type checking
uv run mypy app/ --ignore-missing-imports

# Security
uv run safety check

# Tests
uv run pytest tests/ -v
uv run python test_advanced_agents.py
```

### Backend - Fix issues automatically:

```bash
# Auto-format code
uv run ruff format .

# Auto-fix some linting issues
uv run ruff check . --fix
```

### Frontend - Run checks locally before pushing:

```bash
cd frontend

# Linting
npm run lint

# Type checking
npx tsc --noEmit

# Security
npm audit

# Tests
npm test

# Build
npm run build
```

### Frontend - Fix issues automatically:

```bash
# Auto-fix ESLint issues
npm run lint -- --fix
```

## CI Performance

### Backend CI
**Expected run times:**
- Lint & Format: ~30s (with cache)
- Test: ~2min (includes PostgreSQL setup)
- Security: ~30s
- Type check: ~20s
- Build: ~15s

**Total:** ~3-4 minutes (parallel execution)

### Frontend CI
**Expected run times:**
- Lint & Type Check: ~30s (with cache)
- Test: ~10s (Vitest with no tests)
- Security: ~20s
- Build: ~30s

**Total:** ~1-2 minutes (parallel execution)

## Troubleshooting

### Backend CI Issues

#### Cache not working
- Ensure `uv.lock` is committed
- Check `enable-cache: true` is present
- Verify `cache-dependency-glob` path is correct

#### Tests failing in CI but passing locally
- Check environment variables (especially `DATABASE_URL`)
- Ensure PostgreSQL service is running
- Verify Python version matches (3.13)

#### Advanced agent tests skipped
- Add `ANTHROPIC_API_KEY` to repository secrets
- Tests will automatically run when secret is available

### Frontend CI Issues

#### Cache not working
- Ensure `package-lock.json` is committed
- Check `cache: 'npm'` is present in setup-node
- Verify `cache-dependency-path` points to correct location

#### Build failing
- Run `npm run build` locally to reproduce
- Check for TypeScript errors with `npx tsc --noEmit`
- Verify all dependencies are in package.json

#### Composite action not found
- Ensure `.github/actions/setup-frontend/action.yml` exists
- Check that workflow references it correctly: `uses: ./.github/actions/setup-frontend`
- Verify action.yml has proper `runs.using: 'composite'` configuration

## Next Steps

1. ✅ Backend CI implemented
2. ✅ Frontend CI implemented
3. ⏳ Docker build workflow (pending)
4. ⏳ Deployment workflow (pending)

---

**Questions?** See `.github-issues-to-create.md` for technical debt roadmap.
