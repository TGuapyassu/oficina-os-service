#!/usr/bin/env bash
# Publica os 3 microsserviços no GitHub. Publique oficina-contracts@v0.1.0 antes.
set -euo pipefail
OWNER="${GITHUB_OWNER:-TGuapyassu}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(cd "${ROOT}/.." && pwd)"
REPOS=(oficina-os-service oficina-billing-service oficina-execution-service)

if ! command -v gh >/dev/null; then
  echo "Instale gh: https://cli.github.com/" >&2
  exit 1
fi

for name in "${REPOS[@]}"; do
  dir="${PARENT}/${name}"
  [[ -d "$dir" ]] || { echo "Ausente: $dir"; exit 1; }
  cd "$dir"
  if ! git remote get-url origin >/dev/null 2>&1; then
    gh repo create "${OWNER}/${name}" --${REPO_VISIBILITY:-public} --source=. --remote=origin --push
  else
    git push -u origin main
  fi
done
echo "Contratos: pip install git+https://github.com/${OWNER}/oficina-contracts.git@v0.1.0"
