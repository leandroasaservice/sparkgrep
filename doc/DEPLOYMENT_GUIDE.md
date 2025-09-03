# SparkGrep Deployment Guide

This guide explains how to deploy SparkGrep packages to PyPI using the automated CI/CD pipeline.

## Overview

The CI/CD pipeline combines continuous integration and deployment in a single workflow with three main actions:

1. **CI Only** - Run tests, security scans, and build packages (default for PRs)
2. **Deploy to Test PyPI** - Deploy to test.pypi.org for validation
3. **Deploy to Production PyPI** - Deploy to pypi.org for public release

## Prerequisites

### Required Secrets

Configure the following secrets in your GitHub repository:

- **For SonarCloud**: `SONAR_TOKEN` - SonarCloud integration token
- **For GitGuardian**: `GITGUARDIAN_API_KEY` - GitGuardian secret scanning API key
- **For PyPI**: Uses OIDC trusted publishing (no API tokens needed)
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

### OIDC Trusted Publishing Setup

This project uses OIDC trusted publishing instead of API tokens for enhanced security:

1. **Test PyPI Setup**:
   - Go to <https://test.pypi.org/manage/publishing/>
   - Add trusted publisher for your repository
   - Environment: leave blank for any environment

2. **Production PyPI Setup**:
   - Go to <https://pypi.org/manage/publishing/>
   - Add trusted publisher for your repository
   - Environment: leave blank for any environment

## Deployment Process

### Step 1: Deploy to Test PyPI

The CI/CD pipeline automatically runs CI when you trigger a deployment, so no separate CI run is needed.

1. Go to the **Actions** tab in your repository
2. Select the **"CI/CD Pipeline"** workflow
3. Click **"Run workflow"**
4. Configure the deployment:
   - **Action**: `deploy-test-pypi`
   - **Reason**: Enter a description (e.g., "Testing release 0.1.0a1")
5. Click **"Run workflow"**

#### What happens during Test PyPI deployment

- ✅ Runs change detection (checks if Python files changed)
- ✅ Performs GitGuardian secret scanning in parallel
- ✅ Runs full CI pipeline using Task commands:
  - `task venv` - Creates virtual environment
  - `task build:install` - Builds and installs package
  - `task test` - Runs comprehensive test suite
- ✅ Runs SonarQube analysis for code quality
- ✅ Creates git tag `v{version}` after successful CI
- ✅ Downloads build artifacts and deploys to test.pypi.org
- ✅ Uses OIDC trusted publishing for secure deployment

### Step 2: Validate Test Deployment

After successful test deployment:

1. Test install the package:

   ```bash
   pip install --index-url https://test.pypi.org/simple/ sparkgrep=={version}
   ```

2. Verify the package works as expected

3. Check the created git tag:

   ```bash
   git fetch --tags
   git tag -l "v*"
   ```

### Step 3: Deploy to Production PyPI

Once you've validated the test deployment:

1. Go to the **Actions** tab in your repository
2. Select the **"CI/CD Pipeline"** workflow
3. Click **"Run workflow"**
4. Configure the deployment:
   - **Action**: `deploy-production-pypi`
   - **Reason**: Enter a description (e.g., "Production release 0.1.0a1")
5. Click **"Run workflow"**

#### What happens during Production PyPI deployment

- ✅ Validates admin permissions
- ✅ Runs same CI pipeline as test deployment
- ✅ Checks that git tag exists for the version
- ✅ Downloads the same artifacts from CI stage
- ✅ Deploys package to pypi.org using OIDC trusted publishing
- ✅ No automatic GitHub release creation (manual process)

## Version Management

### Version Format

Versions follow semantic versioning and are defined in `pyproject.toml`:

```toml
[project]
version = "0.1.0a1"  # Format: MAJOR.MINOR.PATCH[PRERELEASE]
```

### Pre-release Indicators

- `a` - Alpha (e.g., "0.1.0a1")
- `b` - Beta (e.g., "0.1.0b1")
- `rc` - Release Candidate (e.g., "0.1.0rc1")

Pre-releases are automatically marked as "prerelease" in GitHub releases.

## Concurrency and Permissions

### Workflow Concurrency

The pipeline uses GitHub's concurrency controls:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}-${{ github.event.inputs.action || 'ci' }}
  cancel-in-progress: true
```

This ensures only one workflow runs per branch and action type.

### Required Permissions

The workflow requires specific permissions:

- `contents: write` - For creating tags and releases
- `pull-requests: read` - For PR approval checking
- `actions: read` - For downloading artifacts
- `issues: write` - For creating issues (rollback scenarios)
- `id-token: write` - For OIDC trusted publishing

## Troubleshooting

### Common Issues

#### "Permission denied" errors

- Ensure you have admin permissions on the repository
- Only repository/organization admins can trigger deployments

#### "Build artifacts not found"

- Ensure the CI portion of the pipeline completed successfully
- Check that the build-packages job ran and uploaded artifacts

#### "Tag already exists"

- Check if the version was already deployed
- Update version in `pyproject.toml` before retrying

### Manual Deployment Troubleshooting

If deployment fails, check these common issues:

1. **Verify workflow permissions**:
   - Check that OIDC trusted publishing is configured
   - Ensure repository has necessary permissions

2. **Check CI dependencies**:

   ```bash
   # Verify Task is available in CI
   task --version

   # Check virtual environment setup
   task env
   ```

3. **Version conflicts**:

   ```bash
   # Check if version already exists on PyPI
   pip index versions sparkgrep
   ```

## Security Notes

- OIDC trusted publishing eliminates need for long-lived API tokens
- Deployments require admin permissions through GitHub's workflow_dispatch
- GitGuardian secret scanning runs on every commit
- All deployment activities are logged and auditable
- Secrets are never exposed in logs or artifacts
- SonarQube analysis ensures code quality before deployment

## Monitoring

### Deployment Status

Monitor deployments through:

- GitHub Actions workflow logs
- Email notifications (if configured)
- PyPI project pages:
  - Test: <https://test.pypi.org/project/sparkgrep/>
  - Production: <https://pypi.org/project/sparkgrep/>

### Release Tracking

Track releases through:

- GitHub Releases page
- Git tags (`git tag -l "v*"`)
- PyPI version history
- Deployment workflow artifacts

## Best Practices

1. **Always test on Test PyPI first** - Never deploy directly to production
2. **Use descriptive deployment reasons** - Helps with audit trails
3. **Verify test installations** - Test the package thoroughly before production
4. **Monitor deployment status** - Watch the workflow logs for any issues
5. **Keep API tokens secure** - Rotate tokens periodically
6. **Update version numbers** - Increment version in `pyproject.toml` for each release

---

For more information about the CI/CD pipeline, see [CI_SETUP.md](CI_SETUP.md).
