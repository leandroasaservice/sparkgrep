# 🚀 CI/CD Deployment Checklist

Use this checklist to ensure your CI/CD pipeline is properly configured and secure.

## ✅ Pre-Deployment Setup

### 1. Repository Configuration

- [ ] **Repository created** on GitHub
- [ ] **Admin permissions** configured for maintainers
- [ ] **Branch protection** enabled for main branch
- [ ] **CODEOWNERS** file configured
- [ ] **Issue templates** added

### 2. Required Secrets Configuration

Navigate to `Settings` → `Secrets and variables` → `Actions`:

- [ ] **SONAR_TOKEN** - SonarCloud integration token
- [ ] **GITGUARDIAN_API_KEY** - GitGuardian secret scanning API key
- [ ] **CODECOV_TOKEN** (optional) - Enhanced coverage reporting

### 3. External Service Setup

#### SonarCloud

- [ ] **Account created** at [sonarcloud.io](https://sonarcloud.io/)
- [ ] **Repository imported** to SonarCloud
- [ ] **Quality Gate configured** (80% coverage minimum)
- [ ] **Token generated** and added to GitHub secrets

#### GitGuardian

- [ ] **Account created** at [dashboard.gitguardian.com](https://dashboard.gitguardian.com/)
- [ ] **Repository connected** to GitGuardian
- [ ] **API key generated** and added to GitHub secrets
- [ ] **Scanning rules configured**

## ✅ Security Configuration

### 1. Branch Protection Rules

Configure for `main` branch in `Settings` → `Branches`:

- [ ] **Require pull request reviews** (minimum 1)
- [ ] **Require review from code owners** ✅
- [ ] **Require status checks** before merging:
  - [ ] `CI Pipeline / ci`
  - [ ] `CI Pipeline / ci-status`
- [ ] **Require conversation resolution** ✅
- [ ] **Restrict pushes that create files** ✅
- [ ] **Require linear history** ✅

### 2. Security Settings

In `Settings` → `Security`:

- [ ] **Dependency alerts** enabled
- [ ] **Security advisories** enabled
- [ ] **Token scanning** enabled
- [ ] **Secret scanning** enabled
- [ ] **Private vulnerability reporting** enabled

### 3. Access Control

- [ ] **Organization admins** can trigger manual CI
- [ ] **Code owners** required for protected files
- [ ] **Two-factor authentication** enforced
- [ ] **Audit log** monitoring enabled

## ✅ Workflow Validation

### 1. File Structure Check

Verify these files exist:

- [ ] `.github/workflows/ci.yml` - Main CI pipeline
- [ ] `.github/workflows/security-daily.yml` - Daily security scans
- [ ] `.github/CODEOWNERS` - Code ownership rules
- [ ] `.github/ISSUE_TEMPLATE/security_report.md` - Security issue template
- [ ] `sonar-project.properties` - SonarCloud configuration
- [ ] `pyproject.toml` - Project configuration with coverage settings

### 2. Configuration Validation

```bash
# Test YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
python -c "import yaml; yaml.safe_load(open('.github/workflows/security-daily.yml'))"

# Test coverage configuration
pytest --cov=sparkgrep --cov-report=xml --dry-run

# Test security tools
bandit --version
safety --version
ggshield --version
```

### 3. Local Testing

- [ ] **Tests pass locally**: `pytest tests/`
- [ ] **Coverage ≥ 80%**: `pytest --cov=sparkgrep --cov-fail-under=80`
- [ ] **No security issues**: `bandit -r src/`
- [ ] **No dependency vulnerabilities**: `safety check`
- [ ] **Code quality**: `ruff check .`

## ✅ First Deployment Test

### 1. Test Manual Trigger

1. Go to `Actions` → `CI Pipeline` → `Run workflow`
2. Trigger with admin account
3. Verify all steps complete successfully
4. Check that artifacts are uploaded

### 2. Test PR Workflow

1. Create feature branch: `git checkout -b test/ci-setup`
2. Make small change and commit
3. Create pull request to main
4. Verify CI pipeline triggers
5. Approve PR as admin
6. Verify pipeline completes successfully

### 3. Test Security Scanning

1. Go to `Actions` → `Daily Security Scan` → `Run workflow`
2. Select "full" scan type
3. Verify all security tools run
4. Check security reports in artifacts

## ✅ Quality Gates Verification

### 1. Coverage Enforcement

Test that pipeline fails with low coverage:

```bash
# Temporarily reduce test coverage and commit
# Verify pipeline fails with coverage < 80%
# Restore full coverage
```

### 2. Security Enforcement

Test security failure scenarios:

```bash
# Add test secret to code
echo "api_key = 'sk-1234567890abcdef'" >> src/test_security.py
git add . && git commit -m "Test security failure"
git push
# Verify pipeline fails due to secret detection
# Remove test file and push fix
```

### 3. Code Quality Enforcement

Test quality gate enforcement:

```bash
# Add intentional code quality issues
# Verify SonarCloud fails the build
# Fix issues and verify pipeline passes
```

## ✅ Monitoring Setup

### 1. Notification Configuration

- [ ] **Email notifications** for workflow failures
- [ ] **Slack/Teams integration** (if applicable)
- [ ] **Security alert notifications** configured
- [ ] **SonarCloud notifications** enabled

### 2. Metrics Tracking

Set up monitoring for:

- [ ] **Pipeline success rate** (target: >95%)
- [ ] **Security scan results** (target: 0 critical/high)
- [ ] **Code coverage trend** (target: ≥80%)
- [ ] **Build time performance** (target: <10 minutes)

### 3. Regular Reviews

Schedule regular reviews:

- [ ] **Weekly**: Review failed builds and security alerts
- [ ] **Monthly**: Update dependencies and scan tools
- [ ] **Quarterly**: Security audit and access review
- [ ] **Annually**: Complete security policy review

## ✅ Documentation Updates

### 1. Project Documentation

- [ ] **README.md** updated with CI badges
- [ ] **CONTRIBUTING.md** includes CI requirements
- [ ] **Security policy** documented
- [ ] **Setup guide** for new contributors

### 2. Team Training

- [ ] **Onboarding guide** for new team members
- [ ] **Security awareness** training completed
- [ ] **CI/CD best practices** documented
- [ ] **Incident response** procedures defined

## 🚨 Troubleshooting Common Issues

### Workflow Permission Issues

```bash
# Error: User does not have admin permissions
# Solution: Add user to admin group or update repository permissions
# Solution: Verify workflow_dispatch permissions for manual triggers
```

### SonarCloud Integration Issues

```bash
# Error: SonarCloud analysis failed
# Check: SONAR_TOKEN is valid and project exists
# Check: sonar-project.properties configuration
# Solution: Verify project key matches repository
# Solution: Check if SonarCloud project is properly configured
```

### Security Scan Failures

```bash
# Error: GitGuardian API rate limit
# Solution: Check API usage and upgrade plan if needed

# Error: Bandit false positives
# Solution: Add # nosec comments or update .bandit config
```

### Coverage Issues

```bash
# Error: Coverage below 80%
# Solution: Run `task test` locally to check coverage
# Solution: Add more tests or exclude non-testable code
# Check: pyproject.toml coverage configuration
```

### Task Command Issues

```bash
# Error: Task not found
# Solution: Install Task: `sudo snap install task --classic`

# Error: Virtual environment issues
# Solution: Check environment: `task env`
# Solution: Recreate environment: `task venv:recreate`

# Error: Build failures
# Solution: Clean and rebuild: `task build:recreate`
```

## 📞 Support Resources

- **GitHub Actions**: [docs.github.com/actions](https://docs.github.com/en/actions)
- **SonarCloud**: [docs.sonarcloud.io](https://docs.sonarcloud.io/)
- **GitGuardian**: [docs.gitguardian.com](https://docs.gitguardian.com/)
- **Task**: [taskfile.dev](https://taskfile.dev/)
- **Task Commands**: [TASK_COMMANDS.md](TASK_COMMANDS.md)
- **Security Issues**: Use security issue template

---

**✅ Deployment Complete!**

Once all checklist items are completed, your CI/CD pipeline will be:

- ✅ **Secure** with comprehensive scanning
- ✅ **Automated** with admin controls
- ✅ **Monitored** with quality gates
- ✅ **Documented** with clear procedures
