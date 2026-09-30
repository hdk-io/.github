# HDK-ADR-001: Repository ownership and conventions

Revision 2 · Accepted; publication pending · Owner: `hdk-io/.github` · Updated: 2026-10-01.
Revision 1 established ownership on 2026-09-30; revision 2 adds concise agent guidance and documentation/stack layout. Applies to all seven repositories.

## Ownership

| Repository | Contract |
| --- | --- |
| `.github` | Organization CI, security baselines, naming and contribution conventions |
| `infrastructure` | Environments, delivery, secrets bindings, operations and qualification |
| `roamory-backend` | App API, account/sync lifecycle, authorization and deletion enforcement |
| `roamory-media` | Internal API, durable processing, moderation, storage/publication |
| `Roamory` | UX, consent interaction, local persistence and client behavior |
| `roamory-admin` | Administrative API, staff access, admin state and audit |
| `roamory-local-dev` | Reproducible local integration environments/fixtures |

Every owner implements security at its boundary. Client consent does not replace server authorization/cleanup; integration grants no ownership of another service's data. Organization naming ownership retains the existing [Actions convention](https://github.com/hdk-io/infrastructure/blob/main/docs/08-workflow-conventions.md) as its reference.

## Shared changes

One lead owner stores one decision under its existing `docs/` decision/design location; absent a convention, use `docs/decisions/<date>-<topic>.md`. All affected docs/PRs link the same ID/revision. Record contracts/producers/consumers, current/new compatibility (including data and old clients), validation, rollout/activation order and recovery/removal limits. Prefer expand/migrate/contract for mixed versions; image rollback cannot rewind a database. Supersede decisions explicitly.

## Structure and instructions

Follow [repository structure](../repository-structure.md): stack-native code layout; all designs/requirements/plans/runbooks/evidence under `docs/`; root README/AGENTS remain concise entry points. Executable OpenAPI/config/contracts, fixtures and licenses retain native locations. Preserve existing versioned/historical docs and update references when moving them.

AGENTS uses concise repository guidelines: structure, commands, coding/testing, PRs and security. Keep changing audit findings in dated evidence, not repeated instruction prose. Read linked docs only when relevant. Each Git root contains essential instructions because a workspace parent is not automatically inherited by Codex.

## Rollout and verification

Publish this decision/layout convention in `.github`, then affected repository docs/AGENTS and updated links. Workspace docs remain local unless deliberately published. This documentation revision changes no runtime contracts, permissions or deployment authority. Verify links, command accuracy, stack paths, existing contract checks and index preservation. Follow-up implementation/security changes need separate validation. To reverse this convention, supersede the decision and update references coherently; no data migration is involved.
