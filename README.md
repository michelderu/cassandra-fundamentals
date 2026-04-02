# Cassandra training — architecture and data modeling

## About Apache Cassandra

[Apache Cassandra](https://cassandra.apache.org/) is an open source, **distributed wide-column** database designed for **massive scale**, **high availability**, and **predictable low latency** on commodity hardware or in the cloud. It uses a **masterless**, peer-to-peer topology: every node can serve reads and writes, and data is replicated across the cluster with **tunable consistency** so applications can trade latency against how many replicas must agree on each operation.

People use Cassandra as an **operational data store** for live workloads—time series and metrics, event logging, product catalogs, session and profile data, messaging back ends, IoT ingestion, and increasingly **AI/ML** and retrieval-style pipelines where throughput and uptime matter more than ad-hoc relational joins. The project describes it as trusted by **thousands of companies** with large active data sets; release testing includes clusters of up to **1,000 nodes**. A public case study on the Cassandra site quotes **Bloomberg** serving **more than 20 billion requests per day** on a **~1 PB** dataset across **1,700+** nodes. The **2024 Apache Cassandra user survey** published **140** responses on use cases, deployment size, and experience. See [References](#references) for links.

![References](assets/references.png)

## This repository

This repo is **hands-on training** in two parts:

1. **Architecture** — You run a **three-node** cluster (Docker Compose) and work through **internals and operations** in [`architecture/`](architecture/README.md): placement, consistency, gossip, the storage engine, and repairs / LWT. Each module uses a short **Terms** table where needed (**CQL**, **RF**, **CL**, **CAP**, **LSM**, etc.).
2. **Data modeling** — A **seven-module** track in [`data-modeling/`](data-modeling/README.md) teaches **query-first** schema design: partition keys, clustering, denormalization, and anti-patterns. It uses **blueprint-style** diagrams (`assets/modeling-*.png`) and includes **hands-on labs in each module** on the **same Docker Compose cluster** ([`docker-compose.yml`](docker-compose.yml)). Create `lab_ks` / `events` per [architecture/02-lab-environment.md](architecture/02-lab-environment.md) before module **02**; see [data-modeling/README.md](data-modeling/README.md#hands-on-labs-by-module) for the lab index.

You can complete **architecture** first, then **data modeling**, or jump to data modeling if you already run Cassandra—still use Compose and [module 02](architecture/02-lab-environment.md) for the shared schema before the hands-on exercises.

## Learning path

### Architecture (cluster labs)

| Module | File |
|--------|------|
| 01 — Architecture and deployment | [architecture/01-architecture-and-deployment.md](architecture/01-architecture-and-deployment.md) |
| 02 — Lab environment | [architecture/02-lab-environment.md](architecture/02-lab-environment.md) |
| 03 — Masterless, peers, placement | [architecture/03-masterless-peers-and-placement.md](architecture/03-masterless-peers-and-placement.md) |
| 04 — CAP and tunable consistency | [architecture/04-cap-and-tunable-consistency.md](architecture/04-cap-and-tunable-consistency.md) |
| 05 — Gossip and topology | [architecture/05-gossip-and-topology.md](architecture/05-gossip-and-topology.md) |
| 06 — Storage engine (write/read, compaction, tombstones) | [architecture/06-storage-engine-write-through-read.md](architecture/06-storage-engine-write-through-read.md) |
| 07 — Self-healing, LWT, summary | [architecture/07-self-healing-lwt-and-summary.md](architecture/07-self-healing-lwt-and-summary.md) |

**Modules 01–04** cover when to use Cassandra, the lab cluster, placement on the ring, and consistency. **Modules 05–07** go deeper into gossip, the storage engine, and self-healing / LWT.

### Data modeling (blueprint track)

Index and order: **[data-modeling/README.md](data-modeling/README.md)**.

| Module | File |
|--------|------|
| 01 — Intro and paradigm | [data-modeling/01-intro-and-paradigm.md](data-modeling/01-intro-and-paradigm.md) |
| 02 — Process and primary key | [data-modeling/02-process-and-primary-key.md](data-modeling/02-process-and-primary-key.md) |
| 03 — Placement and partition health | [data-modeling/03-placement-and-partition-health.md](data-modeling/03-placement-and-partition-health.md) |
| 04 — Clustering and wide partitions | [data-modeling/04-clustering-and-wide-partitions.md](data-modeling/04-clustering-and-wide-partitions.md) |
| 05 — Tombstones and denormalization | [data-modeling/05-tombstones-and-denormalization.md](data-modeling/05-tombstones-and-denormalization.md) |
| 06 — Anti-patterns | [data-modeling/06-anti-patterns.md](data-modeling/06-anti-patterns.md) |
| 07 — Checklist, labs, blueprint | [data-modeling/07-checklist-labs-and-blueprint.md](data-modeling/07-checklist-labs-and-blueprint.md) |

## Prerequisites

- Docker Desktop or Docker Engine **with Compose v2**
- About **4 GB** free RAM for the stack (heap capped at 512 MB per node in `docker-compose.yml`)

## Start the lab cluster

```bash
docker compose up -d
```

If your installation only provides Compose v1:

```bash
docker-compose up -d
```

Wait until all nodes show **UN** (up/normal):

```bash
docker exec cassandra-1 nodetool status
```

Connect with **cqlsh** (from any node):

```bash
docker exec -it cassandra-1 cqlsh cassandra-1 9042
```

The host maps **port 9042** to `cassandra-1` for drivers connecting from your machine (e.g. `127.0.0.1:9042`).

## Stop and reset

```bash
docker compose down
```

To wipe data volumes and start clean:

```bash
docker compose down -v
```

## References

1. Apache Software Foundation, *Apache Cassandra* (homepage: scale, testing, and user quotes). [https://cassandra.apache.org/](https://cassandra.apache.org/)
2. Apache Cassandra community, *2024 User Survey Results* (October 2024, n=140). [https://cassandra.apache.org/_/blog/2024-User-Survey.html](https://cassandra.apache.org/_/blog/2024-User-Survey.html)

Thanks to **David Leconte** for the architecture diagrams and images used in the cluster-lab modules.
