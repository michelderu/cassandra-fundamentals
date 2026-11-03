# Cassandra training — architecture and data modeling

## About Apache Cassandra

[Apache Cassandra](https://cassandra.apache.org/) is an open source, **distributed wide-column** database designed for **massive scale**, **high availability**, and **predictable low latency** on commodity hardware or in the cloud. It uses a **masterless**, peer-to-peer topology: every node can serve reads and writes, and data is replicated across the cluster with **tunable consistency** so applications can trade latency against how many replicas must agree on each operation.

People use Cassandra as an **operational data store** for live workloads—time series and metrics, event logging, product catalogs, session and profile data, messaging back ends, IoT ingestion, and increasingly **AI/ML** and retrieval-style pipelines where throughput and uptime matter more than ad-hoc relational joins. The project describes it as trusted by **thousands of companies** with large active data sets; release testing includes clusters of up to **1,000 nodes**. A public case study on the Cassandra site quotes **Bloomberg** serving **more than 20 billion requests per day** on a **~1 PB** dataset across **1,700+** nodes. The **2024 Apache Cassandra user survey** published **140** responses on use cases, deployment size, and experience. See [References](#references) for links.

![References](assets/references.png)

## This repository

This repo is a **four-session course** (2 hours each) on one **three-node** open-source Cassandra cluster ([`docker-compose.yml`](docker-compose.yml)). **DSE is explained, not labbed.** The same CQL, drivers, and data model apply when the contact points are DSE nodes.

| Phase | Session | Who | File |
|-------|---------|-----|------|
| **1 — Common foundation** | 1 — What it is, where data lives | Developers, platform, SRE, support | [sessions/01-common-foundation.md](sessions/01-common-foundation.md) |
| **1 — Common foundation** | 2 — Consistency, topology, storage | Same | [sessions/02-consistency-topology-storage.md](sessions/02-consistency-topology-storage.md) |
| **2 — Application developer** | 3 — Query-driven design | Developers, architects, tech leads | [sessions/03-query-driven-design.md](sessions/03-query-driven-design.md) |
| **2 — Application developer** | 4 — CQL, drivers, tombstones, TTL | Same | [sessions/04-cql-drivers-performance.md](sessions/04-cql-drivers-performance.md) |

Index: [sessions/README.md](sessions/README.md). Slide deck: [slides/cassandra-data-labs.pptx](slides/cassandra-data-labs.pptx) — import into Google Slides with [slides/README.md](slides/README.md).

Follow the four session files in order, and the deck with them. Each session holds the explanation and the lab for those two hours. `architecture/` and `data-modeling/` are the earlier split of the same material, kept so nothing was thrown away. You do not need them to teach.

## Start the lab cluster

From the repository root, with Docker Compose v2:

```bash
docker compose up -d
docker exec cassandra-1 nodetool status
```

Wait until all three nodes show **UN**, then:

```bash
docker exec -it cassandra-1 cqlsh cassandra-1 9042
```

Create `lab_ks` and `events` in [session 1](sessions/01-common-foundation.md). Later sessions assume that schema.

## Stop and reset

Stop and keep data:

```bash
docker compose stop
```

Remove containers and keep volumes:

```bash
docker compose down
```

Wipe lab data:

```bash
docker compose down -v
```

## Prerequisites

- Docker Desktop or Docker Engine **with Compose v2**
- About **6 GB** free RAM for the stack (`MAX_HEAP_SIZE` is **1G** per node in `docker-compose.yml`; three heaps plus off-heap need more than 4 GB)

## References

1. Apache Software Foundation, *Apache Cassandra* (homepage: scale, testing, and user quotes). [https://cassandra.apache.org/](https://cassandra.apache.org/)
2. Apache Cassandra community, *2024 User Survey Results* (October 2024, n=140). [https://cassandra.apache.org/_/blog/2024-User-Survey.html](https://cassandra.apache.org/_/blog/2024-User-Survey.html)

Thanks to **David Leconte** for the architecture images used in the Architecture modules.
