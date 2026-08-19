# InvariantAudit Workspace Bootstrap Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax (- [ ]) for tracking.

**Goal:** Bootstrap a privacy-checked public InvariantAudit repository with a documented research direction, auditable state, safe publication gates, and evidence-driven end-of-session provenance.
**Architecture:** Markdown is the human research source; YAML is machine-readable state; CSV/JSONL is row data. The workflow is privacy preflight, owner-qualified GitHub publication, documented scaffold, M00 direction, validation, and one final ARA epilogue.
**Tech Stack:** Git, GitHub CLI gh, GitHub public repository, Markdown, YAML, CSV/JSONL, Ruby YAML parser, ARA manager.
**Spec:** docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md

## Global Constraints

- Work only on main; preserve 71b966c docs(design): define InvariantAudit research workflow and the existing plan commits.
- This turn changes only this plan locally; do not execute tasks, authenticate gh, create a repository, push, or cause any other external side effect.
- README and Markdown records own narrative; state/workspace.yaml owns state; research-state.yaml only points to that canonical state; CSV/JSONL owns row data.
- Protocol Markdown must be committed before any result/data commit; each result must reference its protocol commit and pass git merge-base --is-ancestor.
- Every meaningful change needs validation, a non-empty commit, and push after origin exists; use only approved research commit patterns.
- Public push rejects secrets, credentials, personal data, model artifacts, raw/bulk data, caches, build output, and files at or above 52428800 bytes.
- ARA runs once after the final meaningful change is validated, committed, and pushed; no research starts after ARA.

## File Map

- Root: README.md, .gitignore, LICENSE, research-state.yaml, research-log.md, and findings.md.
- Directories and indexes: milestones/README.md, experiments/README.md, literature/README.md, data/README.md, figures/README.md, content/README.md, content/x/README.md, content/linkedin/README.md, and paper/README.md.
- M00/state: milestones/M00-research-direction.md and state/workspace.yaml; no marker files replace indexes.
- ARA: ara/ is created or updated only by the ARA skill at the final epilogue and only for actual session evidence.

---

### Task 1: Preflight privacy

**Files:** Read-only repository inspection; no file writes. **Authority:** local checks are allowed; public GitHub actions require separate user authorization during plan execution.

- [ ] **Step 1: Confirm branch, history, cleanliness, and remote.**
    git status --short --branch
    git branch --show-current
    git log --format=%H%x09%s -n 4
    git remote -v
  Expected: clean main; history contains design commit 71b966c and the current plan commits; no remote output.
- [ ] **Step 2: Run privacy and artifact scans.**
    git diff --check
    git ls-files -oi --exclude-standard
    git grep -nEI '(gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----|xox[baprs]-[0-9A-Za-z-]{10,})' -- .
    find . -type f -not -path './.git/*' -exec stat -f '%z %N' {} + | awk '$1 >= 52428800 {print}'
  Expected: diff, untracked-file, and large-file checks are clean; secret scan exits 1 with no matches.

### Task 2: Authenticate gh and publish the owner-qualified public repository

**Files:** GitHub account, owner-qualified repository, and origin remote; no research files. **Authority:** run only with explicit user authority for login, public creation, and push.

- [ ] **Step 1: Ensure gh authentication without assuming an account.**
    command -v gh || brew install gh
    gh auth status --hostname github.com || gh auth login --hostname github.com --git-protocol https --web
  Expected: gh auth status succeeds for github.com.
- [ ] **Step 2: Resolve the exact owner and reject an ambiguous same-name lookup.**
    github_owner="$(gh api user --jq .login)"
    test -n "$github_owner"
    gh repo view "$github_owner/invariant-audit" --json nameWithOwner,isPrivate,url --jq '.nameWithOwner + " " + (.isPrivate|tostring)'
  Expected: github_owner equals the authenticated login; the repository view exits 1 when absent. If it exists, stop and obtain an explicit reuse decision before any create or push.
- [ ] **Step 3: Create and verify only owner/invariant-audit.**
    gh repo create "$github_owner/invariant-audit" --public --source=. --remote=origin --push
    gh repo view "$github_owner/invariant-audit" --json nameWithOwner,isPrivate,url
    test "$(git remote get-url origin | sed -E 's#^(git@github.com:|https://github.com/)##; s#\.git$##')" = "$github_owner/invariant-audit"
    test "$(git ls-remote origin refs/heads/main | cut -f1)" = "$(git rev-parse HEAD)"
  Expected: exact owner/name, isPrivate false, origin points to that owner/name, and remote main equals local HEAD.

### Task 3: Scaffold the documented workspace and commit/push it

**Files:** Create exactly README.md, .gitignore, LICENSE, research-state.yaml, research-log.md, findings.md, milestones/README.md, experiments/README.md, literature/README.md, data/README.md, figures/README.md, content/README.md, content/x/README.md, content/linkedin/README.md, and paper/README.md. **Interfaces:** create directories milestones experiments literature data figures content/x content/linkedin paper state; do not use marker files.

- [ ] **Step 1: Create directories and root documentation.**
    mkdir -p milestones experiments literature data figures content/x content/linkedin paper state
  README.md must state the title InvariantAudit; research question How can semantic and state invariants be validated while calibrating false positives and false negatives?; local-only scope; no paid API; no external GPU; Status: preliminary; links to the spec, this plan, milestones/README.md, and findings.md; and No overclaim: public claims require verified milestone evidence and human review.
  .gitignore must contain exactly .DS_Store, .env, .env.*, .venv/, __pycache__/, *.py[cod], .pytest_cache/, .mypy_cache/, build/, dist/, coverage/, and .coverage.
  research-state.yaml must contain schema_version: 1, canonical_state_path: state/workspace.yaml, and pointer_only: true, with no duplicated research state.
  research-log.md starts with # Research log and records that bootstrap has no experiment or result. findings.md starts with # Findings and records that no public claim is eligible before verification.
- [ ] **Step 2: Write canonical license and every index role.** Require non-empty git config user.name; LICENSE begins with MIT License, then a blank line, then Copyright (c) 2026 followed by that exact value, followed by the canonical MIT text unchanged. Each index contains the stated role and source of truth:
  milestones/README.md: milestone records and verification evidence; Markdown records are the source of truth and YAML mirrors status.
  experiments/README.md: protocols, runs, results, and linked data; Markdown is narrative source and CSV/JSONL is row-data source.
  literature/README.md: literature notes and citations; Markdown notes and cited sources are the source of truth.
  data/README.md: reviewable row data and metadata; CSV/JSONL is the source of truth and interpretation stays in Markdown.
  figures/README.md: figure specifications and artifacts; source Markdown and result/data commits are the source of truth.
  content/README.md: external drafts from verified milestones; Markdown is source and human review is required.
  content/x/README.md: X drafts tied to a verified milestone and verification commit; no automatic posting.
  content/linkedin/README.md: LinkedIn drafts tied to a verified milestone and verification commit; no automatic posting.
  paper/README.md: paper Markdown, outline, appendix, and provenance; Markdown claims require verified milestone or literature evidence.
- [ ] **Step 3: Validate and stage exactly the scaffold.**
    test -n "$(git config user.name)"
    git diff --check
    git add README.md .gitignore LICENSE research-state.yaml research-log.md findings.md milestones/README.md experiments/README.md literature/README.md data/README.md figures/README.md content/README.md content/x/README.md content/linkedin/README.md paper/README.md
    test -n "$(git diff --cached --name-only)"
  Expected: all required files exist, all requested directories exist, staged names equal the exact list, and no marker file is staged.
- [ ] **Step 4: Commit and push the non-empty scaffold.**
    git commit -m "research(init): scaffold InvariantAudit research workspace"
    git push origin main
  Expected: origin/main advances with the documented scaffold and clean main follows.

### Task 4: Record M00 research direction and canonical state

**Files:** Create/update milestones/M00-research-direction.md, research-state.yaml, state/workspace.yaml, research-log.md, and findings.md. **Interfaces:** consumes the Task 3 scaffold commit; produces active M00 state with exact paths and provenance.

- [ ] **Step 1: Write M00 with separated provenance.** Use headings ID, Status, User decision, Sourced evidence, Reviewer inference, Goal, Completion criteria, Limitations, and Next gate. Set ID M00 and Status active. Under User decision and Provenance user, record the user-approved pivot from generic metamorphic robustness benchmark to validating semantic/state invariants and false-positive/false-negative calibration. Under Sourced evidence, link only the design spec and real commits/files. Under Reviewer inference, label inference as reviewer inference and not evidence. State explicitly: no experiments yet, no results/data, no calibrated metrics, and no public claim eligibility.
- [ ] **Step 2: Update all five state/log paths.** Keep research-state.yaml as a machine-readable pointer to state/workspace.yaml and add workspace_id invariant-audit plus milestone_path milestones/M00-research-direction.md. state/workspace.yaml must contain schema_version 1, workspace_id invariant-audit, branch main, spec_path, canonical_state_path, research_state_pointer, design_commit 71b966c, scaffold_commit from git rev-parse HEAD before edits, and M00 path/status/provenance/evidence. Append exact date, commit message, validation commands, and push result to research-log.md; update findings.md with the pivot, evidence boundary, limitations, and protocol-before-results gate.
- [ ] **Step 3: Validate, commit, and push the direction record.**
    ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p) }; puts "valid YAML"' research-state.yaml state/workspace.yaml
    git diff --check
    git add milestones/M00-research-direction.md research-state.yaml state/workspace.yaml research-log.md findings.md
    test -n "$(git diff --cached --name-only)"
    git commit -m "research(reflect): record M00 research direction"
    git push origin main
  Expected: valid YAML, only the five named files staged, non-empty commit, and origin/main contains the M00 direction.

### Task 5: Final validation and evidence-driven ARA epilogue

**Files:** Update only milestones/M00-research-direction.md, research-state.yaml, state/workspace.yaml, research-log.md, and findings.md for M00; ARA paths are created or updated only when the ARA skill requires them from actual session evidence.

- [ ] **Step 1: Run final privacy, path, history, and protocol gates.**
    for path in README.md .gitignore LICENSE research-state.yaml research-log.md findings.md milestones/README.md experiments/README.md literature/README.md data/README.md figures/README.md content/README.md content/x/README.md content/linkedin/README.md paper/README.md milestones/M00-research-direction.md state/workspace.yaml; do test -f "$path" || exit 1; done
    git diff --check
    git status --porcelain
    git grep -nEI '(gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----|xox[baprs]-[0-9A-Za-z-]{10,})' -- .
    find . -type f -not -path './.git/*' -exec stat -f '%z %N' {} + | awk '$1 >= 52428800 {print}'
    for commit in $(git rev-list 71b966c..HEAD); do test -n "$(git diff-tree --no-commit-id --name-only -r "$commit")" || exit 1; done
  Expected: every new path exists, main is clean before the verification edit, no secret/large-file output, and every post-design commit is non-empty. For any future result, run git merge-base --is-ancestor with its recorded protocol and result commits.
- [ ] **Step 2: Verify M00 without a self-referential hash.** Before the verification commit, change M00 and state status to verified, add validation paths, and record only the planned subject research(reflect): verify M00 research direction in M00, research-state.yaml, state/workspace.yaml, research-log.md, and findings.md. Do not write the verification hash before the commit. Stage only those paths, commit research(reflect): verify M00 research direction, push origin main, then capture verification_commit with git rev-parse HEAD for Step 3.
- [ ] **Step 3: Run ARA once, only after the final research push.** Append the exact verification_commit captured after Step 2 to M00, research-state.yaml, state/workspace.yaml, research-log.md, and findings.md in this ARA provenance commit; never create a self-referential hash. Invoke ara-research-manager at session end. Let the skill inspect actual conversation evidence and existing ara/; create or update only files its procedure requires, never fabricate empty research artifacts, and preserve provenance tags. Validate every created YAML, stage only the changed M00/state/log/finding files plus actual ara/ changes, require a non-empty staged diff, commit research(reflect): record end-of-session ARA provenance, and push origin main only when that diff exists.
    find ara -type f -name '*.yaml' -print0 | xargs -0 ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p) }; puts "valid YAML"'
    git add milestones/M00-research-direction.md research-state.yaml state/workspace.yaml research-log.md findings.md ara/
    test -n "$(git diff --cached --name-only)"
- [ ] **Step 4: Verify the closing state and stop.**
    test "$(git branch --show-current)" = main
    test "$(git ls-remote origin refs/heads/main | cut -f1)" = "$(git rev-parse HEAD)"
    git status --short --branch
  Expected: clean main, remote/local hashes match, no empty commit, no public-safety violation, and no research action follows ARA.
