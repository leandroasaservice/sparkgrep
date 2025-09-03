#!/bin/bash
set -euo pipefail

# create-git-tag.sh
# Creates and pushes git tag after successful CI for deployment actions
# Usage: ./create-git-tag.sh <version> <action>

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

create_tag() {
    local version="$1"
    local action="$2"

    # Only create tags for deployment actions
    if [[ "$action" != "deploy-test-pypi" && "$action" != "deploy-production-pypi" ]]; then
        log_info "Skipping tag creation for action: $action"
        return 0
    fi

    log_info "Creating git tag for deployment action: $action"

    # Configure git
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"

    TAG="v$version"

    # Check if tag already exists
    if git tag -l "$TAG" | grep -q "$TAG"; then
        log_warn "Tag $TAG already exists, skipping tag creation"
        return 0
    fi

    # Create and push tag
    git tag -a "$TAG" -m "Release $version - CI completed successfully"
    git push origin "$TAG"

    log_info "✅ Created and pushed tag: $TAG"
}

main() {
    local version="${1:-}"
    local action="${2:-}"

    if [[ -z "$version" ]]; then
        log_error "Version parameter is required"
        echo "Usage: $0 <version> <action>"
        exit 1
    fi

    if [[ -z "$action" ]]; then
        log_error "Action parameter is required"
        echo "Usage: $0 <version> <action>"
        exit 1
    fi

    create_tag "$version" "$action"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
