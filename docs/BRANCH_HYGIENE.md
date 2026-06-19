# Branch Hygiene

The public Sparkbot repository keeps `main` as the only long-lived public branch. Feature, documentation, and operations branches should be short-lived review branches created from fresh `main`.

## Expectations

- Keep `main` as the only long-lived public branch.
- Start future work from current `main`.
- Merge only fresh, reviewed branches that fit the current public contracts.
- Delete merged branches after verifying they are ancestors of `main`.
- Do not push retired unsafe branches back to the public remote.
- Do not merge or cherry-pick retired unsafe branches.
- Restart unsafe runtime, provider, connector, credential, model, persistence, or policy-enforcement work from fresh `main` under the current public contracts.

## Check Remote Heads

Run this release-manager check before starting new public product work and after deleting retired branches:

```bash
bash scripts/check-branch-hygiene.sh
```

By default, the check passes only when `origin/main` is the only remote head. It uses `git ls-remote` and does not modify the repository.

For an intentional active review branch, allow a branch-name pattern explicitly:

```bash
SPARKBOT_ALLOWED_BRANCH_REGEX='^(docs|ops|product)/public-safe-review$' \
  bash scripts/check-branch-hygiene.sh
```

Use the allowlist only for active review branches that are expected to remain temporarily visible on the public remote.

## If An Unexpected Branch Appears

Do not delete it immediately. First:

- Fetch and verify the current remote heads.
- Archive the branch head, changed files, diff stat, and full diff.
- Compare the branch against current `main`.
- Classify the branch as stale merged, unsafe unmergeable, active review, or unknown.
- Delete only branches that are clearly stale merged or unsafe unmergeable.
- Leave unknown or active review branches in place and report them.

Retired unsafe branches should be treated as evidence only. If a retired idea is still useful, extract the public-safe intent into a new branch from fresh `main`.
