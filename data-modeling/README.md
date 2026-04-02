# Data modeling track

Work through this track (**01–07**) after the **architecture** modules (**01–07**), or in parallel once you know the cluster basics. Diagrams live in [`../assets`](../assets) as descriptive PNGs (`modeling-*.png`, e.g. `modeling-blueprint-title.png`, `modeling-partition-token-ring.png`).

## Lab cluster (Docker Compose)

**All hands-on labs use the same three-node stack** as the architecture track. From the **repository root** (where [`docker-compose.yml`](../docker-compose.yml) lives):

1. **Prerequisites:** Docker with Compose v2, ~4 GB free RAM — [../README.md](../README.md#prerequisites).
2. **Start:** `docker compose up -d` — [../README.md](../README.md#start-the-lab-cluster).
3. **Health:** `docker exec cassandra-1 nodetool status` until every node is **UN**.
4. **cqlsh:** `docker exec -it cassandra-1 cqlsh cassandra-1 9042`
5. **Schema:** Create keyspace `lab_ks` and table `events` with [architecture/02-lab-environment.md](../architecture/02-lab-environment.md) (Lab B). Module **01** also walks through a minimal connectivity check; you need `lab_ks` before most later labs.

**Stop / reset:** [../README.md](../README.md#stop-and-reset).

## Hands-on labs by module

| Module | Lab focus |
|--------|-----------|
| [01](01-intro-and-paradigm.md) | Connect via Docker Compose; confirm cluster metadata in `cqlsh`. |
| [02](02-process-and-primary-key.md) | `DESCRIBE` primary key; insert rows; partition vs clustering. |
| [03](03-placement-and-partition-health.md) | `nodetool getendpoints` for a partition key. |
| [04](04-clustering-and-wide-partitions.md) | Range on `event_time`; optional `CLUSTERING ORDER BY` demo table. |
| [05](05-tombstones-and-denormalization.md) | `DELETE` + read; `events_by_day` + dual write. |
| [06](06-anti-patterns.md) | `ALLOW FILTERING`; optional secondary index; optional LWT. |
| [07](07-checklist-labs-and-blueprint.md) | Checklist + capstone labs (placement, predicates, denormalization). |

| # | File | Focus |
|---|------|--------|
| 01 | [01-intro-and-paradigm.md](01-intro-and-paradigm.md) | Blueprint intro; relational vs Cassandra; golden rule |
| 02 | [02-process-and-primary-key.md](02-process-and-primary-key.md) | Four-step process; partition vs clustering |
| 03 | [03-placement-and-partition-health.md](03-placement-and-partition-health.md) | Consistent hashing; `getendpoints`; hot vs even load |
| 04 | [04-clustering-and-wide-partitions.md](04-clustering-and-wide-partitions.md) | Clustering ranges; wide partition risks |
| 05 | [05-tombstones-and-denormalization.md](05-tombstones-and-denormalization.md) | Tombstones; fan-out to multiple tables |
| 06 | [06-anti-patterns.md](06-anti-patterns.md) | Secondary indexes; `ALLOW FILTERING`; LWT |
| 07 | [07-checklist-labs-and-blueprint.md](07-checklist-labs-and-blueprint.md) | Checklist; blueprint; capstone labs |

Course overview: [../README.md](../README.md#learning-path).
