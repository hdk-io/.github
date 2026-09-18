# HDK.io Infrastructure Design

## Goals

This infrastructure is designed for an initial workload of roughly **10–50 active users**, while keeping a clear path to significantly higher concurrency and image-processing throughput.

Primary goals:

- Production-ready Kubernetes foundation.
- Strong security boundaries and least-privilege access.
- High availability for critical services.
- Horizontal scaling for API and image-processing workloads.
- Separate `dev`, `staging`, and `prod` environments.
- Additional isolated environments for review/preview workloads where practical.
- Observable, auditable infrastructure with metrics, logs, traces, and security events.
- Infrastructure concerns stay in this repository/project; application/backend-specific decisions remain in the Roamory backend project.

## Environment Model

### Development

- Low-cost shared Kubernetes resources.
- Reduced replica counts.
- Relaxed availability requirements.
- Suitable for integration testing and developer validation.

### Staging

- Mirrors production topology where practical.
- Used for release validation, migrations, load tests, and security checks.
- Separate secrets, databases, object storage, and external integrations from production.

### Production

- High-availability Kubernetes workloads.
- Multiple replicas for stateless services.
- Pod anti-affinity / topology spread across nodes or availability zones.
- Horizontal Pod Autoscaling.
- PodDisruptionBudgets for critical services.
- Restricted network access and workload identities.
- Dedicated production data services and backups.

### Review / Preview

- Ephemeral namespaces per pull request or feature branch when useful.
- Strict quotas and automatic cleanup.
- No production credentials or production data.

## Kubernetes Platform

Recommended baseline:

- Managed Kubernetes where possible.
- At least two worker nodes for non-production and three for production when HA is required.
- Separate node pools for:
  - General API workloads.
  - Image-processing / CPU-heavy workers.
  - Optional GPU workloads if image processing later requires acceleration.
- Cluster Autoscaler or provider equivalent.
- Horizontal Pod Autoscaler for API and workers.
- Vertical Pod Autoscaler in recommendation mode initially.
- Resource requests and limits required for all workloads.
- Priority classes for critical system components.

## Edge and Traffic

- DNS managed through a provider supporting API-driven records.
- CDN/WAF in front of public endpoints.
- TLS terminated at the edge and/or Kubernetes ingress.
- Kubernetes ingress controller or Gateway API.
- Rate limiting at edge and application gateway.
- DDoS protection from cloud/CDN provider.

Traffic flow:

1. User request reaches DNS/CDN/WAF.
2. CDN serves cacheable/static content.
3. Dynamic traffic reaches Kubernetes ingress.
4. Ingress routes to API/web services.
5. Services use PostgreSQL, Redis, queues, and object storage.
6. Image-processing jobs are submitted asynchronously to workers.

## Application Workloads

### API / Web

- Stateless deployments.
- Minimum 2 replicas in production once HA is required.
- HPA driven by CPU, memory, request rate, and/or latency.
- Readiness, liveness, and startup probes.

### Image Processing

Image processing should not block request threads.

- API uploads original media directly or through presigned URLs to object storage.
- API submits a job to a durable queue.
- Worker deployments consume jobs asynchronously.
- Workers scale independently from API pods.
- Processing outputs are written back to object storage.
- CDN serves transformed images.

This separates user-facing latency from compute-heavy work and permits aggressive worker autoscaling.

## Data Layer

### PostgreSQL

Prefer a managed PostgreSQL service.

- Automated backups and point-in-time recovery.
- Multi-zone HA for production when justified by traffic and availability targets.
- TLS enforced.
- Private network connectivity.
- Separate databases/users per environment.
- Connection pooling through PgBouncer or provider equivalent.

### Redis

Use for:

- Caching.
- Distributed locks where necessary.
- Short-lived sessions/state.
- Rate-limit counters.

Do not treat Redis as the authoritative store for durable business data unless explicitly designed for it.

### Object Storage

Use S3-compatible object storage for:

- Original images.
- Processed images/thumbnails.
- Export artifacts.
- Backup artifacts where applicable.

Enable:

- Bucket versioning where appropriate.
- Encryption at rest.
- Lifecycle policies.
- Private buckets with presigned access.
- CDN access via restricted origin identity.

## Queue

A durable queue decouples API requests from processing workers.

Possible implementations:

- Cloud-managed queue.
- RabbitMQ.
- Redis Streams where operationally appropriate.

For high-scale image processing, a managed queue is preferred to reduce operational overhead.

## Security

### Identity and Access

- SSO/MFA for human access.
- Least-privilege IAM.
- No shared administrator credentials.
- Workload identity instead of static cloud keys where supported.
- Short-lived credentials.
- Separate identities per environment.

### Kubernetes Security

- Pod Security Standards: Restricted where possible.
- Non-root containers.
- Read-only root filesystem where practical.
- Drop Linux capabilities by default.
- Seccomp RuntimeDefault.
- NetworkPolicies with default-deny posture.
- RBAC scoped by namespace and responsibility.
- Admission policies to enforce security requirements.

### Secrets

- External secret manager preferred.
- Secrets synchronized into Kubernetes only when required.
- No secrets committed to Git.
- Automatic rotation for supported credentials.

### Supply Chain

- Dependency scanning.
- Secret scanning.
- Container vulnerability scanning.
- SBOM generation.
- Image signing / provenance.
- Only trusted registries permitted in production.
- Deploy immutable image digests instead of mutable tags.

## Observability

### Metrics

- Prometheus-compatible metrics.
- Grafana dashboards.
- Kubernetes/node metrics.
- API latency, throughput, saturation, and error metrics.
- Queue depth and worker processing duration.
- PostgreSQL/Redis health indicators.

### Logs

- Centralized structured logs.
- Environment, service, trace ID, request ID, and severity fields.
- Retention policy appropriate to cost and compliance.

### Traces

- OpenTelemetry instrumentation.
- Distributed tracing across edge/API/queue/workers.

### Alerting

Alerts should focus on actionable SLO symptoms:

- Elevated API error rate.
- Sustained latency.
- Queue backlog.
- Worker failures.
- Database saturation.
- Node pressure.
- Persistent volume exhaustion.
- Certificate expiry.
- Backup failures.

## Backup and Disaster Recovery

- PostgreSQL automated backups plus PITR.
- Periodic restoration tests.
- Object-storage versioning/lifecycle policies.
- Kubernetes configuration fully reproducible from Git/IaC.
- Recovery procedures documented and exercised.

## Infrastructure as Code

Recommended organization:

- Terraform/OpenTofu for cloud infrastructure.
- Helm/Kustomize for Kubernetes deployment configuration.
- GitOps controller such as Argo CD or Flux for cluster reconciliation.
- Environment-specific overlays rather than duplicated manifests.

## CI/CD

Typical pipeline:

1. Pull request checks.
2. Unit/integration tests.
3. Dependency and secret scanning.
4. Container build.
5. Vulnerability scan and SBOM.
6. Sign image.
7. Push immutable image.
8. Deploy to dev/review.
9. Promote to staging.
10. Production deployment through protected approval/promotion.
11. GitOps controller reconciles desired state.

## Initial Capacity Estimate

For approximately **10–50 active users**, a modest baseline is sufficient if image processing is asynchronous.

### Kubernetes application capacity

A practical starting point:

- 2 general-purpose worker nodes.
- Around 2–4 vCPU each.
- Around 8–16 GiB RAM each.
- Separate autoscaled image-processing workers if CPU demand grows.

Typical initial service requests:

- API pod: 250–500m CPU, 256–512 MiB RAM.
- Background worker: 500m–2 CPU, 512 MiB–2 GiB RAM depending on image transformations.
- Supporting workloads: approximately 1–2 vCPU and 2–4 GiB RAM cluster-wide for ingress, metrics, controllers, and logging agents.

These are starting estimates; real limits should be derived from load tests and production telemetry.

### Storage

Initial planning target:

- Kubernetes ephemeral/system storage: 50–100 GB per node.
- PostgreSQL: 20–50 GB initial allocation with autoscaling.
- Object storage: start around 100 GB logically, using elastic object storage rather than fixed disks.
- Logs/metrics: enforce retention and quotas because observability data may grow faster than application data.

## Scaling Path

As concurrency grows:

- Increase API replicas horizontally.
- Autoscale processing workers based on queue depth.
- Introduce dedicated image-processing node pools.
- Add database read replicas only when measured query load requires them.
- Expand Redis or move to clustered/managed tiers when cache throughput requires it.
- Use CDN caching aggressively for image delivery.
- Separate workloads across multiple clusters only after operational or isolation requirements justify the complexity.

## Infrastructure vs Backend Responsibility

Infrastructure project owns:

- Kubernetes platform.
- Networking, ingress, CDN, WAF.
- IAM and workload identity.
- Secret delivery mechanisms.
- Managed data-service provisioning.
- Queue infrastructure.
- Object storage infrastructure.
- CI/CD platform integration.
- GitOps.
- Observability platform.
- Backup infrastructure.
- Security policies and enforcement.
- Capacity/autoscaling primitives.

Roamory backend should own application-specific decisions such as:

- Image-processing algorithms.
- Business-level retry semantics.
- Database schemas.
- API-level authorization behavior.
- Domain-specific cache strategy.
- Job payload structure.
- Application-level idempotency and transactional behavior.
