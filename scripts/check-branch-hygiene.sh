#!/usr/bin/env bash
set -euo pipefail

REMOTE_NAME="${SPARKBOT_BRANCH_HYGIENE_REMOTE:-origin}"
ALLOWED_BRANCH_REGEX="${SPARKBOT_ALLOWED_BRANCH_REGEX:-}"

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "${ROOT_DIR}"

if ! git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
  echo "FAIL: remote '${REMOTE_NAME}' is not configured." >&2
  exit 1
fi

remote_heads="$(git ls-remote --heads "${REMOTE_NAME}")"

if [[ -z "${remote_heads}" ]]; then
  echo "FAIL: no remote heads found for '${REMOTE_NAME}'." >&2
  exit 1
fi

unexpected_branches=()
main_found="no"

while IFS=$'	' read -r _sha ref_name; do
  branch_name="${ref_name#refs/heads/}"

  if [[ "${branch_name}" == "main" ]]; then
    main_found="yes"
    continue
  fi

  if [[ -n "${ALLOWED_BRANCH_REGEX}" && "${branch_name}" =~ ${ALLOWED_BRANCH_REGEX} ]]; then
    continue
  fi

  unexpected_branches+=("${branch_name}")
done <<< "${remote_heads}"

if [[ "${main_found}" != "yes" ]]; then
  echo "FAIL: remote '${REMOTE_NAME}' does not contain refs/heads/main." >&2
  exit 1
fi

if (( ${#unexpected_branches[@]} > 0 )); then
  echo "FAIL: unexpected public remote branches found on '${REMOTE_NAME}':" >&2
  for branch_name in "${unexpected_branches[@]}"; do
    echo "  - ${branch_name}" >&2
  done
  echo "Archive evidence and classify each branch before deleting anything." >&2
  echo "Set SPARKBOT_ALLOWED_BRANCH_REGEX only for intentional active review branches." >&2
  exit 1
fi

echo "PASS: public branch hygiene check"
echo "Remote '${REMOTE_NAME}' has only refs/heads/main plus any explicitly allowed branches."
