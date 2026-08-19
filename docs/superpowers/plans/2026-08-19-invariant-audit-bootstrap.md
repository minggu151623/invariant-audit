# InvariantAudit Workspace Bootstrap Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax (- [ ]) for tracking.

**Goal:** Bootstrap a privacy-checked public invariant-audit repository with an auditable M00 milestone, canonical state, logs, findings, commits, and one end-of-session ARA record.
**Architecture:** Markdown owns human research narrative; state/workspace.yaml owns machine-readable state; CSV and JSONL will own row data. Main moves through privacy preflight, authorized GitHub publication, namespace scaffold, M00 verification, and one final ARA epilogue.
**Tech Stack:** Git, GitHub CLI gh, GitHub public repository, Markdown, YAML, CSV/JSONL, Ruby YAML parser, ARA manager.
**Spec:** docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md

## Global Constraints

- Work only on main; preserve design commit 71b966c: docs(design): define InvariantAudit research workflow.
- Markdown is narrative source; YAML is state source; CSV/JSONL is row-data source; generated output never becomes a source of truth.
- Protocol Markdown must be committed before any result/data commit; a result commit must reference its protocol commit and pass the ancestor check.
- Meaningful changes require validation, a non-empty commit, and push after origin exists; use only research(init), research(protocol), research(results), research(reflect), or research(paper).
- Public push rejects secrets, credentials, personal data, model artifacts, raw/bulk data, caches, build output, and any single file at or above 52428800 bytes.
- ARA runs once, after the final meaningful change is validated, committed, and pushed; no research starts after ARA. This plan is the only artifact created in this turn; tasks 1 through 5 are not executed here.

## File Map

- Create .gitignore and Git-tracked markers in milestones, experiments, literature, figures, content, paper, and state.
- Create milestones/M00-bootstrap.md, state/workspace.yaml, state/log.md, state/findings.md, and the ARA seed files under ara/ specified in Task 5 at the final epilogue.

---

### Task 1: Preflight privacy

**Files:** Read-only entire repository; no file writes. **Authority:** Local inspection is allowed. Do not create, authenticate, or push a public repository until the user has authorized those external actions.

- [ ] **Step 1: Confirm branch, cleanliness, history, and remote state.**
    git status --short --branch
    git branch --show-current
    git log --format=%H%x09%s -n 2
    git remote -v
  Expected: branch main, clean worktree, HEAD is the plan commit followed by design commit 71b966c, and no remote output.
- [ ] **Step 2: Run repository hygiene checks.**
    git diff --check
    git ls-files -oi --exclude-standard
    git grep -nEI '(gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----|xox[baprs]-[0-9A-Za-z-]{10,})' -- .
    find . -type f -not -path './.git/*' -exec stat -f '%z %N' {} + | awk '$1 >= 52428800 {print}'
  Expected: diff check and large-file scan exit 0 with no output; tracked-file scan has no output; secret scan exits 1 with no matches.

### Task 2: Install/authenticate gh and create the public repository

**Files:** GitHub account, GitHub repository invariant-audit, and local origin remote; no research files. **Authority:** Execute only after explicit user authorization for GitHub login, public repository creation, and push.

- [ ] **Step 1: Ensure GitHub CLI authentication.**
    command -v gh || brew install gh
    gh auth status --hostname github.com || gh auth login --hostname github.com --git-protocol ssh --web
  Expected: gh is available and gh auth status reports a valid github.com login.
- [ ] **Step 2: Verify the target name is unused, then create and push it.**
    gh repo view invariant-audit --json nameWithOwner,isPrivate,url
    gh repo create invariant-audit --public --source=. --remote=origin --push
  Expected: the first command exits 1 because the target is absent; the second creates a public repository, adds origin, and pushes current main without changing content.
- [ ] **Step 3: Verify public visibility and remote alignment.**
    gh repo view invariant-audit --json nameWithOwner,isPrivate,url
    git remote get-url origin
    test "$(git ls-remote origin refs/heads/main | cut -f1)" = "$(git rev-parse HEAD)"
  Expected: isPrivate is false, origin ends in /invariant-audit.git, and the remote main hash equals local HEAD.

### Task 3: Scaffold workspace, validate, commit, and push

**Files:** Create .gitignore; create milestones/.gitkeep, experiments/.gitkeep, literature/.gitkeep, figures/.gitkeep, content/.gitkeep, paper/.gitkeep, and state/.gitkeep. **Interfaces:** Consumes origin/main from Task 2; produces the seven tracked research namespaces. Do not create ara/ before the final session epilogue.

- [ ] **Step 1: Create namespaces and the exact ignore rules.**
    mkdir -p milestones experiments literature figures content paper state
    touch milestones/.gitkeep experiments/.gitkeep literature/.gitkeep figures/.gitkeep content/.gitkeep paper/.gitkeep state/.gitkeep
  Put exactly these entries in .gitignore: .DS_Store, .env, .env.*, .venv/, __pycache__/, *.py[cod], .pytest_cache/, .mypy_cache/, build/, dist/, and .coverage.
- [ ] **Step 2: Validate the scaffold and stage only its files.**
    git diff --check
    find milestones experiments literature figures content paper state -name .gitkeep -type f -print | sort
    git add .gitignore milestones/.gitkeep experiments/.gitkeep literature/.gitkeep figures/.gitkeep content/.gitkeep paper/.gitkeep state/.gitkeep
    test -n "$(git diff --cached --name-only)"
  Expected: seven marker paths print in sorted order, diff check is clean, and the staged-name test exits 0.
- [ ] **Step 3: Commit and push the non-empty scaffold.**
    git commit -m "research(init): scaffold InvariantAudit workspace namespaces"
    git push origin main
  Expected: the commit contains exactly the scaffold files, origin/main advances, and git status --short --branch reports clean main.

### Task 4: Record M00, canonical state, log, and findings

**Files:** Create milestones/M00-bootstrap.md, state/workspace.yaml, state/log.md, and state/findings.md. **Interfaces:** Consumes the Task 3 scaffold commit; produces an active M00 record and canonical state with design_commit 71b966c and scaffold_commit set to the exact output of git rev-parse HEAD before Task 4 edits.

- [ ] **Step 1: Write the M00 record.** Use the exact headings ID, Status, Goal, Completion criteria, Evidence, Limitations, and Next gate. Set ID to M00, Status to active, state that no experiment has a protocol or result yet, link the design spec, all seven namespace paths, and the Task 3 commit, and require a protocol commit before any result/data commit.
- [ ] **Step 2: Write canonical state and append-only Markdown records.** state/workspace.yaml must contain schema_version 1, workspace_id invariant-audit, branch main, spec_path docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md, canonical_state_path state/workspace.yaml, source roles narrative markdown/state yaml/row_data csv-or-jsonl, and M00 path/status/evidence. state/log.md records the bootstrap date, exact commit IDs, validation commands, and push result. state/findings.md records that the workspace is initialized, no result exists, the protocol-before-results gate is open, and public content is not yet eligible.
- [ ] **Step 3: Validate YAML and staged content.**
    ruby -e 'require "yaml"; YAML.load_file(ARGV.fetch(0)); puts "valid YAML"' state/workspace.yaml
    git diff --check
    git add milestones/M00-bootstrap.md state/workspace.yaml state/log.md state/findings.md
    test -n "$(git diff --cached --name-only)"
  Expected: Ruby prints valid YAML, diff check is clean, and only the four named files are staged.
- [ ] **Step 4: Commit and push M00 state.**
    git commit -m "research(init): record M00 bootstrap state"
    git push origin main
  Expected: a non-empty commit is pushed and state/workspace.yaml still identifies main and M00 as active.

### Task 5: Final validation and ARA epilogue

**Files:** Modify milestones/M00-bootstrap.md and state/workspace.yaml; create/update ara/PAPER.md, ara/logic/problem.md, ara/logic/claims.md, ara/logic/concepts.md, ara/logic/experiments.md, ara/logic/solution/architecture.md, ara/logic/solution/algorithm.md, ara/logic/solution/constraints.md, ara/logic/solution/heuristics.md, ara/logic/related_work.md, ara/src/environment.md, ara/trace/exploration_tree.yaml, ara/trace/sessions/session_index.yaml, ara/trace/sessions/2026-08-19_001.yaml, ara/evidence/README.md, and ara/staging/observations.yaml. **Interfaces:** Consumes the pushed active M00; produces verified M00, end-of-session provenance, a clean main worktree, and an origin/main equal to local HEAD.

- [ ] **Step 1: Run final pre-ARA gates.**
    test "$(git branch --show-current)" = main
    git diff --check
    git status --porcelain
    git grep -nEI '(gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----|xox[baprs]-[0-9A-Za-z-]{10,})' -- .
    find . -type f -not -path './.git/*' -exec stat -f '%z %N' {} + | awk '$1 >= 52428800 {print}'
    for commit in $(git rev-list 71b966c..HEAD); do test -n "$(git diff-tree --no-commit-id --name-only -r "$commit")" || exit 1; done
  Expected: main, clean diff checks, no status/secrets/large-file output, and every post-design commit has at least one changed path. No experiments files exist yet, so no protocol ancestry check is needed.
- [ ] **Step 2: Verify M00 and push the verification commit.** Set M00 and its state entry to verified, add every validation path as evidence, then run git diff --check, git add milestones/M00-bootstrap.md state/workspace.yaml, test -n "$(git diff --cached --name-only)", git commit -m "research(reflect): verify M00 bootstrap milestone", and git push origin main. Record this commit ID in both M00 and state before the ARA commit.
- [ ] **Step 3: Run the ARA manager only now.** It must read the full session, preserve user/ai-suggested/ai-executed provenance, append rather than overwrite, create the listed ara paths, and record that no research starts after ARA. Validate every YAML file with Ruby, stage only M00/state ARA changes, require a non-empty staged diff, commit with research(reflect): record end-of-session ARA provenance, and push origin main.
    git add milestones/M00-bootstrap.md state/workspace.yaml ara/
- [ ] **Step 4: Verify the closing state.**
    ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p) }; puts "valid YAML"' state/workspace.yaml ara/trace/exploration_tree.yaml ara/trace/sessions/session_index.yaml ara/trace/sessions/2026-08-19_001.yaml ara/staging/observations.yaml
    test "$(git ls-remote origin refs/heads/main | cut -f1)" = "$(git rev-parse HEAD)"
    git status --short --branch
  Expected: valid YAML, remote/local hashes match, and output is clean main; no commit or research action follows ARA.
