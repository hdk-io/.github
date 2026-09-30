# HDK.io

## Engineering conventions

- [Organization CI governance](https://github.com/hdk-io/.github/blob/main/docs/ci-governance.md) owns the stable `HDK.io Policy` and `repository-ci` / `Repository CI` merge-gate interfaces
- [Workflow conventions](https://github.com/hdk-io/infrastructure/blob/main/docs/08-workflow-conventions.md) cover naming and privileged lifecycle boundaries
- [Infrastructure document index](https://github.com/hdk-io/infrastructure/blob/main/docs/README.md) identifies current contracts, runbooks and retained historical revisions

Service repositories own source, tests and image publication. Infrastructure owns deployment
registrations, target bindings and selected immutable releases. Current implementation and
live qualification are tracked separately in the linked infrastructure runbooks.
