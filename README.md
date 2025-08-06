# SparkGrep

![Static Badge](https://img.shields.io/badge/preview-red)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=coverage)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=bugs)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=sparkgrep&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=sparkgrep)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-greenb.svg)](https://github.com/PyCQA/bandit)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Pre-commit hook that detects debugging leftovers in Apache Spark applications.

## 🎯 Purpose

SparkGrep helps maintain clean Apache Spark codebases by detecting common debugging leftovers and performance anti-patterns that developers often forget to remove before committing code.

### 🔍 What it Detects

- **`display()` calls** - Jupyter/Databricks debugging function
- **`.show()` methods** - DataFrame inspection calls
- **`.collect()` without assignment** - Potential performance issues
- **`.count()` without assignment** - Unnecessary computations
- **Custom patterns** - User-defined patterns via configuration

## 🚀 Installation

```bash
pip install sparkgrep
```

## 📋 Usage

### As a Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/leandroasaservice/sparkgrep
    rev: v0.1.0a1  # Use this preview version.
    hooks:
      - id: sparkgrep
```

### Command Line

```bash
# Check specific files
sparkgrep src/my_script.py notebook.ipynb

# Check with additional patterns
sparkgrep --additional-patterns "debug_print:Debug print statement" src/

# Disable default patterns and use only custom ones
sparkgrep --disable-default-patterns --additional-patterns "my_pattern:My description" src/
```

----

## 🛡️ Security & Quality

This project maintains high security and code quality standards:

### 🔒 Security Measures

- **Daily security scans** with Bandit, Safety, and GitGuardian
- **Automated vulnerability detection** and issue creation
- **Admin-protected CI/CD** pipelines
- **Dependency vulnerability monitoring**

### 📊 Code Quality

- **80% minimum code coverage** enforced in CI
- **SonarCloud integration** for continuous code quality analysis
- **Automated testing** on every PR
- **Code formatting** with Ruff

----



## 📁 Project Structure

```sh
sparkgrep/
├── src/sparkgrep/          # Main package
│   ├── cli.py              # Command-line interface
│   ├── patterns.py         # Pattern definitions
│   ├── file_processors.py  # File processing logic
│   └── utils.py            # Utility functions
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── .github/                # GitHub configuration
│   ├── workflows/          # CI/CD pipelines
│   └── ISSUE_TEMPLATE/     # Issue templates
└── docs/                   # Documentation
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with tests
4. **Ensure** all checks pass (`task test`, security scans)
5. **Submit** a pull request

### Contribution Guidelines

- **Tests required** for all new features
- **Security scans** must pass
- **Code coverage** must remain ≥ 80%
- **Admin approval** required for all PRs to main
- **Follow** existing code style and patterns
See [CONTRIBUTING.md](doc/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/leandroasaservice/sparkgrep/issues)
- **Discussions**: [GitHub Discussions](https://github.com/leandroasaservice/sparkgrep/discussions)
- **Documentation**: [Project Docs](doc/)

---

**Made with ❤️ for the Apache Spark community**
