# Cassandra fundamentals — training and labs

Hands-on material for Apache Cassandra architecture concepts, using a **three-node** local cluster via Docker Compose.

## Learning path

| Module | File |
|--------|------|
| 01 — Fundamentals and deployment | [training/01-fundamentals-and-deployment.md](training/01-fundamentals-and-deployment.md) |
| 02 — Lab environment | [training/02-lab-environment.md](training/02-lab-environment.md) |
| 03 — Data modeling essentials | [training/03-data-modeling-essentials.md](training/03-data-modeling-essentials.md) |
| 04 — Masterless, peers, placement | [training/04-masterless-peers-and-placement.md](training/04-masterless-peers-and-placement.md) |
| 05 — CAP and tunable consistency | [training/05-cap-and-tunable-consistency.md](training/05-cap-and-tunable-consistency.md) |
| 06 — Gossip and topology | [training/06-gossip-and-topology.md](training/06-gossip-and-topology.md) |
| 07 — Storage engine (write/read, compaction, tombstones) | [training/07-storage-engine-write-through-read.md](training/07-storage-engine-write-through-read.md) |
| 08 — Self-healing, LWT, summary | [training/08-self-healing-lwt-and-summary.md](training/08-self-healing-lwt-and-summary.md) |

**Modules 01–05** introduce when to use Cassandra, the cluster, keyspace modeling, placement, and consistency. **Modules 06–08** go deeper into internals, gossip, the storage engine, and repairs.

More detail: [training/README.md](training/README.md).

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

Thanks to **David Leconte** for the architecture diagrams and images used in the training modules.
