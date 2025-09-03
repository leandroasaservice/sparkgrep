# CI/CD Pipeline Setup Guide

This guide explains how to set up and configure the comprehensive CI/CD pipeline for SparkGrep.

## 🔧 Required Secrets

Configure the following secrets in your GitHub repository settings (`Settings` → `Secrets and variables` → `Actions`):

### Required Secrets

| Secret | Purpose | How to Get |
|--------|---------|------------|
| `SONAR_TOKEN` | SonarCloud integration | [SonarCloud Account Tokens](https://sonarcloud.io/account/security) |
| `GITGUARDIAN_API_KEY` | Secret scanning | [GitGuardian API Keys](https://dashboard.gitguardian.com/api/v1/auth/user/github_login/authorize?utm_source=github&utm_medium=social&utm_campaign=github_signup) |

### Optional Secrets

| Secret | Purpose | How to Get |
|--------|---------|------------|
| `CODECOV_TOKEN` | Enhanced coverage reporting | [Codecov](https://codecov.io/) |

## 🛡️ Security Configuration

### 1. SonarCloud Setup

1. **Create SonarCloud Account**
   - Visit [SonarCloud.io](https://sonarcloud.io/)
   - Sign in with your GitHub account
   - Import your repository

2. **Configure Quality Gate**
   - Go to your project → Quality Gates
   - Set coverage threshold to **≥ 80%**
   - Enable security hotspot detection
   - Set maintainability rating to **A**

3. **Generate Token**
   - Go to Account → Security
   - Generate a new token
   - Add as `SONAR_TOKEN` secret in GitHub

### 2. GitGuardian Setup

1. **Create GitGuardian Account**
   - Visit [GitGuardian Dashboard](https://dashboard.gitguardian.com/)
   - Connect your GitHub account
   - Add your repository

2. **Generate API Key**
   - Go to API → Personal Access Tokens
   - Create new token with scope: `scan`
   - Add as `GITGUARDIAN_API_KEY` secret in GitHub

### 3. Branch Protection Rules

Configure branch protection for `main`:

```yaml
# In GitHub Settings → Branches → Add rule
Branch name pattern: main
Restrictions:
  ✅ Require a pull request before merging
  ✅ Require approvals: 1
  ✅ Require review from code owners
  ✅ Require status checks to pass before merging
    ✅ CI Pipeline / ci
  ✅ Require conversation resolution before merging
  ✅ Restrict pushes that create files
```

## 🚦 CI Pipeline Overview

### Trigger Conditions

| Trigger | Condition | Permission Required |
|---------|-----------|-------------------|
| Push | Push to `main` branch | Automatic |
| Pull Request | PR to `main` branch | Automatic |
| Manual Dispatch | Workflow dispatch with action selection | Admin only |

### Pipeline Stages

1. **Change Detection**
   - Checks if Python-related files changed (`tests/`, `src/`, `requirements.txt`)
   - For manual triggers, always runs all tests
   - For PR/push, only runs if relevant files changed

2. **Security Scanning**
   - **GitGuardian**: Secret detection and scanning
   - Runs in parallel with main pipeline
   - **Failure condition**: Any secrets detected

3. **Test and Build**
   - Python 3.12 matrix testing
   - Task-based build system
   - Creates virtual environment using `task venv`
   - Builds and installs package with `task build:install`
   - Runs comprehensive tests with `task test`
   - **Failure condition**: Any test failures

4. **Quality Analysis**
   - SonarCloud analysis with coverage reports
   - Quality gate evaluation
   - Technical debt assessment

5. **Artifact Management**
   - Upload build artifacts (distribution packages)
   - Store artifacts for 15 days
   - Create git tags for deployment actions

6. **Deployment** (Manual only)
   - Deploy to Test PyPI or Production PyPI
   - Uses trusted publishing with OIDC
   - Downloads artifacts from build stage

### Failure Conditions

The pipeline **FAILS** if:

- ❌ **Coverage < 80%**
- ❌ **Critical security vulnerabilities found**
- ❌ **Tests fail**
- ❌ **Linting errors**
- ❌ **SonarCloud quality gate fails**
- ❌ **Unauthorized access attempt**

## 📊 Security Monitoring

### Manual Deployment Actions

The CI/CD pipeline supports three workflow dispatch actions:

- **ci-only** (default): Run CI tests and quality checks only
- **deploy-test-pypi**: Deploy to test.pypi.org after successful CI
- **deploy-production-pypi**: Deploy to pypi.org after successful CI

### Security Issue Management

When vulnerabilities are detected:

1. **Automatic issue creation** with details
2. **Admin notification** via GitHub
3. **Security reports** attached as artifacts
4. **Prioritized by severity** (Critical/High/Medium/Low)

### Manual Workflow Triggers

Admins can trigger workflows manually:

```bash
# Via GitHub Actions UI
Actions → CI/CD Pipeline → Run workflow
Select action: ci-only | deploy-test-pypi | deploy-production-pypi
Provide reason: "Description of manual trigger"
```

## 🔒 Admin Controls

### Who Can Approve PRs?

Only users listed in `CODEOWNERS`:

- `@leandroasaservice` (organization admin)

### Who Can Trigger Manual CI?

Only organization/repository admins can:

- Trigger manual CI runs
- Override security failures (not recommended)
- Modify protected files

### Protected Files

The following files require admin approval:

```text
/.github/workflows/     # CI/CD pipelines
/.github/CODEOWNERS     # Code ownership
/.github/ISSUE_TEMPLATE/ # Issue templates
/sonar-project.properties # SonarCloud config
/.pre-commit-config.yaml # Pre-commit hooks
/pyproject.toml         # Project configuration
/requirements.txt       # Dependencies
/ruff.toml             # Linting config
/taskfile.dist.yaml     # Task configuration
```

## 🚨 Emergency Procedures

### Critical Vulnerability Response

1. **Immediate**: Stop all deployments
2. **Assess**: Review vulnerability details in security reports
3. **Fix**: Address vulnerability in emergency branch
4. **Test**: Run security scans on fix
5. **Deploy**: Emergency merge with admin approval

### Pipeline Failure Response

1. **Check logs**: Review workflow logs for specific failure
2. **Security failures**: Address vulnerabilities immediately
3. **Coverage failures**: Add tests to reach 80% threshold
4. **Quality failures**: Fix code quality issues

### Access Control Issues

1. **Unauthorized access**: Review and update CODEOWNERS
2. **Permission escalation**: Audit GitHub permissions
3. **Security breach**: Rotate all secrets immediately

## 📈 Monitoring & Alerts

### Key Metrics

Monitor these metrics:

- **Coverage trend**: Should stay ≥ 80%
- **Security rating**: Should be A
- **Vulnerability count**: Should be 0 critical/high
- **Technical debt**: Should trend downward

### Alert Channels

- **GitHub Issues**: Automatic security issues
- **Email**: SonarCloud quality gate failures
- **Workflow**: Failed CI pipeline notifications

## 🔧 Troubleshooting

### Common Issues

#### Pipeline fails with "Permission denied"

- Check if user has admin permissions
- Verify CODEOWNERS configuration

#### SonarCloud analysis fails

- Verify `SONAR_TOKEN` is valid
- Check SonarCloud project configuration

#### GitGuardian scan fails

- Verify `GITGUARDIAN_API_KEY` is valid
- Check API rate limits

#### Coverage below 80%

- Add more tests (`task test` to check locally)
- Remove unused code
- Check coverage exclusions in `pyproject.toml`

#### Task/Build failures

- Verify Task is installed: `task --version`
- Check virtual environment: `task env`
- Rebuild environment: `task venv:recreate`

### Debug Commands

```bash
# Using Task (recommended)
task quality  # Run all quality checks
task test     # Run tests only
task security # Run security scan
task lint     # Run linting

# Manual commands
.venv/bin/python -m pytest --cov=sparkgrep --cov-report=term-missing
.venv/bin/bandit -r src/
.venv/bin/ruff check src/

# SonarCloud local analysis (requires sonar-scanner)
sonar-scanner -Dsonar.login=$SONAR_TOKEN
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [GitGuardian Documentation](https://docs.gitguardian.com/)
- [Task Documentation](https://taskfile.dev/)
- [Task Commands Reference](TASK_COMMANDS.md)
