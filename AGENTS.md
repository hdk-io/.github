# Repository Guidelines

## Project Structure & Module Organization

Organization governance lives in `.github/workflows/required-pr-policy.yml`, `docs/ci-governance.md`, `docs/repository-structure.md` and `docs/decisions/`. Scanner tests live in `tests/`; `profile/README.md` is the public organization entry point. This repository owns CI/security/naming/contribution conventions, not service builds or runtime deployment.

## Task Workspace

Use `/Users/khanhhuynh/Work/AI_tasks/<task-name>/` as the working folder for each task. Keep isolated worktrees, scratch files, build/test output, logs, screenshots, generated evidence, and task-local state there. Create a distinct task name and preserve existing task directories. Commit source and configuration in the owning repository; put versioned designs, requirements, plans, runbooks, and verification summaries under `docs/`. Keep secrets out of Git and terminal output.

## Build, Test, and Development Commands

Use Python 3 with the policy's `PyYAML==6.0.3` installed. Activate the environment so test subprocesses use it too:

```sh
python3 -I -m unittest discover -s tests -v
git diff --check
```

## Coding Style & Testing Guidelines

Pin remote Actions to full 40-character SHAs; use named jobs/steps and read-only permissions. Keep the independent `HDK.io Policy` and `repository-ci` / `Repository CI` interfaces stable. Test actual embedded scanners with malformed and fail-open fixtures; parse structure rather than matching YAML text. Current local-action/Docker exemptions do not prove transitive pinning.

## Commit & Pull Request Guidelines

Use focused `ci:`, `fix:` or `docs:` commits. Explain policy impact, scanner tests and any ruleset migration. Cross-repository changes follow [HDK-ADR-001 rev 2](docs/decisions/2026-09-30-repository-ownership.md); put detailed design under `docs/`, not here.

## Security & Configuration

Policy tests protect every enrolled repository. Verify source-repository gates, bypasses, issuing-app binding, runner isolation and actual inherited rulesets before claiming enforcement. Inaccessible organization settings are unverified. Preserve credential-free PR validation; do not dispatch deployments or change live settings merely to test documentation.
