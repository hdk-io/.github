# Repository structure convention

Authority: [HDK-ADR-001 rev 2](decisions/2026-09-30-repository-ownership.md). Applies to existing and new HDK.io repositories; preserve tool-required paths and public contracts.

## Shared layout

| Path | Purpose |
| --- | --- |
| `README.md` | Short overview, quickstart and link to `docs/README.md` |
| `AGENTS.md` | Concise executable guidance at each Git root |
| `docs/README.md` | Navigation and current-versus-historical authority |
| `docs/design/`, `docs/requirements/` | Human design/specifications; create only when needed |
| `docs/decisions/` | Versioned owner decisions with shared IDs/revisions |
| `docs/plans/`, `docs/runbooks/`, `docs/verification/`, `docs/audits/` | Task plans, operations and dated evidence as needed |
| `scripts/` | Maintained tooling; tests remain in stack-native test directories |
| `.github/workflows/` | Active workflows, not prose specifications |

Do not create empty directories or duplicate documents. `docs/superpowers/` and `.superpowers/` are obsolete execution layouts: do not add them, and migrate any tracked copies to `docs/design/` (specifications) and `docs/plans/` (plans) with links and indexes updated. Existing numbered infrastructure docs remain compatible retained layouts; do not rename versioned references for cosmetic uniformity. All new design/requirement prose belongs under `docs/` in its contract owner's repository. Root READMEs, fixture explanations, licenses and GitHub's `profile/README.md` are entry-point/data exceptions, not alternative specification stores. Tool scratch directories are not project specifications; reviewed artifacts belong in docs. Machine-consumed OpenAPI, config schemas, migrations and contract fixtures stay beside the code they govern.

Commands in docs run from the repository root unless stated otherwise. Rebase relative links/images after moves; update workflow/test/config references and incoming links. Keep old audit citations tied to their original revision rather than presenting them as fresh observations.

Dependency manifests stay in tooling-native locations: infrastructure's root
`requirements-dev.txt` pins Python test dependencies, alongside `Makefile`; Maven
`pom.xml` and Node `package.json`/lockfiles likewise remain at their project roots.
These executable dependency inputs are distinct from human requirement specifications
under `docs/requirements/`.

## Stack layouts

| Stack / repositories | Source and tests | Runtime/build tooling |
| --- | --- | --- |
| Java/Quarkus: backend, admin | `src/main/java/<package>/<feature>`, `src/main/resources/db/migration`, `src/test/java`, `src/test/resources` | Root `pom.xml`, Maven wrapper/`.mvn`; backend `extensions/`; Dockerfile/scripts where implemented |
| Node/TypeScript: media | `src/<feature>`, `test/`, `migrations/`, `openapi/` | Root package/lockfile/tsconfig/lint/test configs; `scripts/`, Dockerfile; generated `dist/` excluded |
| Swift/Xcode: Roamory | `Roamory/{App,Core,Platform,...}`, `RoamoryTests/`, `RoamoryUITests/` | Xcode project, `Package.swift`, `Config/`, `scripts/`; generated DerivedData/build artifacts external |
| Kubernetes/Python: infrastructure | `config/`, `k8s/`, `platform/`, `services/`, `targets/`, `releases/`; `tests/` | Root Makefile/requirements, `scripts/`; generated `.tools/.reports/.venv` excluded |
| Python/shell/Compose: local-dev | Root setup/stack/Compose for this small tool; `tests/` | External state/models/worktrees; split into packages only when size warrants |
| Governance: `.github` | `.github/workflows/`, `tests/`, `profile/` | `docs/` owns conventions and decisions |

Use domain/feature modules within each native layout. Avoid parallel `src/` + `app/` trees with overlapping responsibility. Do not move source/configuration solely to resemble another stack.

## AGENTS convention

Use `# Repository Guidelines` and short sections for structure, commands, coding/testing, commits/PRs and security/configuration. Aim for about 300–500 words per repository, fewer for small tools. Keep real commands and non-obvious guardrails; link detailed specs/runbooks rather than copying them. State standalone essentials; parent files above a Git root are not automatically discovered. No mandatory schema or frontmatter is required.

References: [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Codex /init](https://learn.chatgpt.com/docs/developer-commands?surface=cli#generate-agentsmd-with-init).
