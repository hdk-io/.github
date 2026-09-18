# HDK.io Infrastructure Architecture

```mermaid
flowchart TB
    U[Users / Mobile / Web]

    subgraph EDGE[Edge]
      DNS[DNS]
      CDN[CDN + WAF + DDoS Protection]
    end

    subgraph K8S[Managed Kubernetes]
      ING[Ingress / Gateway]

      subgraph APP[Application Workloads]
        API[API / Web Pods\nHPA + Multiple Replicas]
        JOB[Job Producer]
      end

      subgraph WORKERS[Processing Node Pool]
        IMG[Image Processing Workers\nAutoscaled by Queue Depth]
      end

      subgraph PLATFORM[Platform Services]
        OTEL[OpenTelemetry Collector]
        MET[Metrics / Logs Agents]
        ESO[External Secrets Operator]
        GITOPS[Argo CD / Flux]
      end
    end

    subgraph DATA[Managed Data Services]
      PG[(PostgreSQL\nHA + PITR)]
      REDIS[(Redis)]
      QUEUE[(Durable Queue)]
      OBJ[(Object Storage)]
    end

    subgraph OBS[Observability]
      PROM[Prometheus]
      GRAF[Grafana]
      LOGS[Central Logs]
      TRACE[Tracing Backend]
      ALERT[Alerting]
    end

    subgraph CICD[Supply Chain / CI-CD]
      GH[GitHub]
      CI[CI Pipeline\nTest + Scan + SBOM]
      REG[Container Registry\nSigned Images]
    end

    U --> DNS --> CDN --> ING
    ING --> API
    API --> PG
    API --> REDIS
    API --> OBJ
    API --> JOB --> QUEUE
    QUEUE --> IMG
    IMG --> OBJ
    IMG --> PG

    API --> OTEL
    IMG --> OTEL
    OTEL --> TRACE

    MET --> PROM --> GRAF
    MET --> LOGS
    PROM --> ALERT

    ESO --> API
    ESO --> IMG

    GH --> CI --> REG
    REG --> GITOPS
    GITOPS --> K8S

    OBJ --> CDN
```

## Environment isolation

```mermaid
flowchart LR
    DEV[dev namespace / cluster]
    STG[staging namespace / cluster]
    PROD[prod namespace / cluster]
    PREVIEW[PR / Preview Namespaces]

    DEV --> STG --> PROD
    PREVIEW -. ephemeral validation .-> DEV
```

Production uses isolated credentials, data services, buckets, secrets, and deployment controls. Review environments never receive production credentials or production data.
