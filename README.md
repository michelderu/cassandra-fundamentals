# Cassandra fundamentals — training and labs

## About Apache Cassandra

[Apache Cassandra](https://cassandra.apache.org/) is an open source, **distributed wide-column** database designed for **massive scale**, **high availability**, and **predictable low latency** on commodity hardware or in the cloud. It uses a **masterless**, peer-to-peer topology: every node can serve reads and writes, and data is replicated across the cluster with **tunable consistency** so applications can trade latency against how many replicas must agree on each operation.

People use Cassandra as an **operational data store** for live workloads—time series and metrics, event logging, product catalogs, session and profile data, messaging back ends, IoT ingestion, and increasingly **AI/ML** and retrieval-style pipelines where throughput and uptime matter more than ad-hoc relational joins. The project describes it as trusted by **thousands of companies** with large active data sets; release testing includes clusters of up to **1,000 nodes**. A public case study on the Cassandra site quotes **Bloomberg** serving **more than 20 billion requests per day** on a **~1 PB** dataset across **1,700+** nodes. The **2024 Apache Cassandra user survey** published **140** responses on use cases, deployment size, and experience. See [References](#references) for links.

![References](assets/references.png)

## This repository

This repo is **hands-on training** in two parts:

1. **Fundamentals** — You run a **three-node** cluster (Docker Compose) and work through **architecture and operations** in [`training/fundamentals/`](training/fundamentals/README.md): placement, consistency, gossip, the storage engine, and repairs / LWT. Each module uses a short **Terms** table where needed (**CQL**, **RF**, **CL**, **CAP**, **LSM**, etc.).
2. **Data modeling** — A separate **seven-module** track in [`data-modeling/`](data-modeling/README.md) teaches **query-first** schema design: partition keys, clustering, denormalization, and anti-patterns. It uses **blueprint-style** diagrams (`assets/dm-*.png`) and assumes you understand the fundamentals (especially partitions, replication, and reads/writes).

You can complete **fundamentals** first, then **data modeling**, or jump to data modeling if you already run Cassandra and mainly need the modeling narrative (the labs still use the shared `lab_ks` keyspace from [module 02](training/fundamentals/02-lab-environment.md)). A short index of both tracks lives under [`training/README.md`](training/README.md).

## Learning path

### Fundamentals (cluster labs)

| Module | File |
|--------|------|
| 01 — Fundamentals and deployment | [training/fundamentals/01-fundamentals-and-deployment.md](training/fundamentals/01-fundamentals-and-deployment.md) |
| 02 — Lab environment | [training/fundamentals/02-lab-environment.md](training/fundamentals/02-lab-environment.md) |
| 03 — Masterless, peers, placement | [training/fundamentals/03-masterless-peers-and-placement.md](training/fundamentals/03-masterless-peers-and-placement.md) |
| 04 — CAP and tunable consistency | [training/fundamentals/04-cap-and-tunable-consistency.md](training/fundamentals/04-cap-and-tunable-consistency.md) |
| 05 — Gossip and topology | [training/fundamentals/05-gossip-and-topology.md](training/fundamentals/05-gossip-and-topology.md) |
| 06 — Storage engine (write/read, compaction, tombstones) | [training/fundamentals/06-storage-engine-write-through-read.md](training/fundamentals/06-storage-engine-write-through-read.md) |
| 07 — Self-healing, LWT, summary | [training/fundamentals/07-self-healing-lwt-and-summary.md](training/fundamentals/07-self-healing-lwt-and-summary.md) |

**Modules 01–04** cover when to use Cassandra, the lab cluster, placement on the ring, and consistency. **Modules 05–07** go deeper into gossip, the storage engine, and self-healing / LWT.

### Data modeling (blueprint track)

Index and order: **[data-modeling/README.md](data-modeling/README.md)**.

| Module | File |
|--------|------|
| DM 01 — Intro and paradigm | [data-modeling/01-intro-and-paradigm.md](data-modeling/01-intro-and-paradigm.md) |
| DM 02 — Process and primary key | [data-modeling/02-process-and-primary-key.md](data-modeling/02-process-and-primary-key.md) |
| DM 03 — Placement and partition health | [data-modeling/03-placement-and-partition-health.md](data-modeling/03-placement-and-partition-health.md) |
| DM 04 — Clustering and wide partitions | [data-modeling/04-clustering-and-wide-partitions.md](data-modeling/04-clustering-and-wide-partitions.md) |
| DM 05 — Tombstones and denormalization | [data-modeling/05-tombstones-and-denormalization.md](data-modeling/05-tombstones-and-denormalization.md) |
| DM 06 — Anti-patterns | [data-modeling/06-anti-patterns.md](data-modeling/06-anti-patterns.md) |
| DM 07 — Checklist, labs, blueprint | [data-modeling/07-checklist-labs-and-blueprint.md](data-modeling/07-checklist-labs-and-blueprint.md) |

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

Thanks to **David Leconte** for the architecture diagrams and images used in the fundamentals training modules.
