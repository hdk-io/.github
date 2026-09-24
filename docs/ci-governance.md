# HDK.io CI governance design

Status: initial implementation

## Purpose

HDK.io repositories need one organization-level merge policy without forcing every
repository to use the same build system, language, test layout, or deployment workflow.
The governance model therefore standardizes **merge-gate interfaces**, not repository
implementation details.

This design applies to infrastructure, application, and service repositories that are
explicitly enrolled in the protected CI policy.

## Goals

- enforce common pull-request policy from the `hdk-io` organization;
- keep repository-specific build, test, lint, integration, and smoke jobs inside each
  repository;
- expose one stable repository-owned required check named `Repository CI`;
- expose one centrally owned required workflow/check named `HDK.io Policy`;
- support GitHub merge queue by requiring PR validation workflows to handle
  `merge_group`;
- keep deployment, promotion, preview-management, and other privileged workflows out of
  the default-branch merge gate;
- make future repository onboarding a property assignment rather than ruleset editing.

## Non-goals

- centralize all repository CI commands in shell scripts;
- require all repositories to use Make, npm, SwiftPM, Gradle, or any other common runner;
- make manual/deployment workflows block pull-request merges;
- grant the organization policy workflow deployment credentials;
- encode application-specific test logic in the organization `.github` repository.

## Architecture

```text
                         hdk-io organization ruleset
                                  |
                   +--------------+--------------+
                   |                             |
                   v                             v
          HDK.io required policy          Repository CI status
          centrally controlled            repository controlled
                   |                             |
     hdk-io/.github/.github/              repo/.github/workflows/
     workflows/required-pr-policy.yml     <repository validation>.yml
                   |                             |
          HDK.io Policy                    repository-ci
                                                 |
                              +------------------+------------------+
                              |                  |                  |
                            build               test              lint/...
```

The two gates have different ownership:

1. **HDK.io Policy** is defined in `hdk-io/.github` and attached to repositories by an
   organization ruleset. Individual repositories cannot redefine this workflow.
2. **Repository CI** is a final aggregator job in the repository's own PR validation
   workflow. The jobs it aggregates are repository-specific.

## Stable repository CI contract

Every enrolled repository MUST expose a job with this exact machine and display
contract:

```yaml
jobs:
  repository-ci:
    name: Repository CI
```

The job MUST:

- depend on every repository-specific job required to merge;
- run with `if: ${{ always() }}` so upstream failure or skip cannot accidentally make
  the required check disappear;
- fail unless all required dependencies conclude `success`;
- remain credential-free and perform no deployment or production mutation.

The repository PR validation workflow MUST support both:

```yaml
on:
  pull_request:
  merge_group:
```

Repositories MAY also run the same validation on `push` or `workflow_dispatch`.

Internal jobs remain free to use meaningful repository-specific names. For example,
infrastructure may validate manifests and run disposable Kind smoke tests while a Swift
service may compile, lint, and test. Only the final `Repository CI` interface is common.

## Organization policy workflow

`.github/workflows/required-pr-policy.yml` is the source workflow for the organization
ruleset's **Require workflows to pass before merging** rule.

The initial policy is intentionally small and technology-neutral. It verifies that:

- the target repository exposes the `repository-ci` / `Repository CI` contract;
- the validation workflow supports `pull_request` and `merge_group`;
- remote GitHub Actions and reusable workflows referenced by repository workflow files
  are pinned to full 40-character commit SHAs.

Local actions (`./...`) are allowed. Docker action references are not evaluated by the
initial pinning rule and may be governed separately later.

The policy workflow itself has read-only repository permission and receives no
deployment secrets.

## Workflow ownership boundary

PR merge validation and privileged mutation are separate concerns.

| Workflow type | Merge gate | Credentials |
| --- | --- | --- |
| PR build/test/lint/validation | aggregated by `Repository CI` | read-only/minimum |
| Organization policy | `HDK.io Policy` | read-only |
| Environment preparation | no | protected environment |
| Preview create/retire | no | sandbox/nonproduction only |
| Publish/deploy/promote | no direct PR gate; separately authorized | protected environment |
| Scheduled maintenance | no | task-specific |

A repository MUST NOT satisfy `Repository CI` by calling a deployment workflow or by
requiring live production credentials.

## Repository targeting

Define the organization custom property:

```text
ci-policy = protected | excluded
```

Recommended initial configuration:

- default: `excluded`;
- values editable by organization actors;
- assign `protected` to production-bearing infrastructure, service, and application
  repositories after they implement the contract.

The organization ruleset targets repositories where `ci-policy=protected`. This keeps
rollout explicit and avoids accidentally blocking governance/template repositories.

## Organization ruleset

Create one branch ruleset named:

```text
HDK.io — Protected default branch
```

Target:

- repositories with `ci-policy=protected`;
- the repository default branch.

Required rules:

- require a pull request before merging;
- require conversation resolution;
- block branch deletion;
- block non-fast-forward/force pushes;
- require the `Repository CI` status check from GitHub Actions;
- require branches to be up to date before merging;
- require `.github/workflows/required-pr-policy.yml` from `hdk-io/.github@main` to
  pass before merging.

Approval count and stale-approval behavior are organization policy choices and can be
enabled without changing the CI contract.

Do not add repository-internal job names such as `Swift test`, `Validate manifests`,
or `Verify preview workflow` to the organization ruleset.

## Rollout

1. Merge this specification and the central policy workflow into `hdk-io/.github`.
2. Add the `Repository CI` aggregator and `merge_group` trigger to
   `hdk-io/infrastructure`.
3. Create `ci-policy` and assign `protected` to infrastructure.
4. Create the organization ruleset in **Evaluate** mode first.
5. Confirm rule-suite results for normal PRs and merge-group events.
6. Change the ruleset to **Active** after successful evaluation.
7. Onboard each service/application repository by implementing the same final job
   contract, then set `ci-policy=protected`.

A repository is not enrolled until its required checks are visible and passing on at
least one pull request.

## Failure semantics

- Any required internal job failure makes `Repository CI` fail.
- Any required internal job skip makes `Repository CI` fail unless the repository
  explicitly removes that job from the aggregator contract.
- Missing `Repository CI` is a policy failure.
- Removing `merge_group` support is a policy failure.
- Introducing an unpinned remote action is a policy failure.
- Deployment workflow failure does not block an unrelated PR unless that deployment is
  deliberately added to the repository CI dependency graph.

## Change management

`Repository CI` and `HDK.io Policy` are public interfaces between repositories and
organization governance. Rename them only together with the organization ruleset.

Repository-specific jobs may be renamed or reorganized without ruleset changes as long
as `repository-ci` continues to aggregate the complete merge-critical dependency set.

Changes to the central policy workflow should be reviewed as organization governance
changes because they affect every enrolled repository.
