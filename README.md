# Cassandra fundamentals — training and labs

Hands-on material for Apache Cassandra architecture concepts, with a **three-node** local cluster via Docker Compose.

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

## Training modules

| Module | File |
|--------|------|
| Lab environment and workflow | [training/01-lab-environment.md](training/01-lab-environment.md) |
| Masterless, peers, data placing | [training/02-masterless-peers-and-placement.md](training/02-masterless-peers-and-placement.md) |
| CAP and tunable consistency | [training/03-cap-and-tunable-consistency.md](training/03-cap-and-tunable-consistency.md) |
| Gossip and topology | [training/04-gossip-and-topology.md](training/04-gossip-and-topology.md) |
| Storage engine: write path → reads, compaction, tombstones | [training/05-storage-engine-write-through-read.md](training/05-storage-engine-write-through-read.md) |
| Self-healing, LWT, summary | [training/06-self-healing-lwt-and-summary.md](training/06-self-healing-lwt-and-summary.md) |

Thanks to **David Leconte** for the architecture diagrams and images used in the training modules.