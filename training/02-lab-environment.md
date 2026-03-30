# 02 — Lab environment

This module gets the **Docker Compose** cluster running and prepares a shared **keyspace** for later labs.

**Prerequisites:** Docker with Compose v2, ~4 GB RAM free. See [../README.md](../README.md).

---

## Concepts (brief)

Before hands-on work, you need a real cluster: **three Cassandra peers** on one machine, isolated by Docker networking. You will use:

- **`docker compose`** — start/stop the stack.
- **`nodetool status`** — see which nodes are **UN** (up/normal).
- **`cqlsh`** — interactive CQL shell (run inside a container).
- **Keyspace** — replication scope; we use **RF = 3** to match three nodes.

---

## Lab A — Start the cluster and verify health

1. From the project root (`cassandra-fundamentals`):

   ```bash
   docker compose up -d
   ```

2. Wait until all three nodes report **UN**:

   ```bash
   docker exec cassandra-1 nodetool status
   ```

   You should see three rows with **State** = `UN` and addresses for `cassandra-1`, `cassandra-2`, `cassandra-3`.

3. Open **cqlsh** on the first node:

   ```bash
   docker exec -it cassandra-1 cqlsh cassandra-1 9042
   ```

4. Inspect cluster metadata:

   ```sql
   SELECT cluster_name, release_version FROM system.local;
   ```

   **Deliverable:** Paste or note the `cluster_name` (should match `training-lab` from Compose) and `release_version`.

---

## Lab B — Create the shared training keyspace and table

In **cqlsh**, run:

```sql
CREATE KEYSPACE IF NOT EXISTS lab_ks
  WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
  };

USE lab_ks;

CREATE TABLE IF NOT EXISTS events (
  user_id uuid,
  event_time timestamp,
  payload text,
  PRIMARY KEY (user_id, event_time)
) WITH compaction = {
  'class': 'SizeTieredCompactionStrategy'
};
```

If your server rejects `SimpleStrategy`, drop and recreate the keyspace using `NetworkTopologyStrategy` with the datacenter name from `nodetool status` (often `datacenter1`):

```sql
DROP KEYSPACE IF EXISTS lab_ks;

CREATE KEYSPACE lab_ks
  WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
  };

USE lab_ks;

CREATE TABLE IF NOT EXISTS events (
  user_id uuid,
  event_time timestamp,
  payload text,
  PRIMARY KEY (user_id, event_time)
) WITH compaction = {
  'class': 'SizeTieredCompactionStrategy'
};
```

**Why `SimpleStrategy` here:** Single logical datacenter in this lab; three replicas, one per node.

**Deliverable:** `DESCRIBE KEYSPACE lab_ks;` shows `replication_factor: 3` (SimpleStrategy) or `datacenter1: 3` (NetworkTopologyStrategy).

---

## Lab C — Connect from the host (optional)

Drivers can use `127.0.0.1:9042` (mapped to `cassandra-1`). Example with Python (if you install `cassandra-driver`):

```bash
pip install cassandra-driver
```

```python
from cassandra.cluster import Cluster
cluster = Cluster(["127.0.0.1"], port=9042)
session = cluster.connect("lab_ks")
print(session.execute("SELECT release_version FROM system.local").one())
```

**Deliverable:** One successful read from the host, or skip if you stay on cqlsh-only.

---

## Troubleshooting

| Symptom | What to try |
|--------|-------------|
| Only one UN node | Wait 1–2 minutes; check `docker compose logs cassandra-2`. |
| `Connection refused` on 9042 | Confirm `docker compose ps` shows containers **running**. |
| Out of memory | Increase Docker memory or lower `MAX_HEAP_SIZE` in `docker-compose.yml`. |

---

## Next

[03-data-modeling-essentials.md](03-data-modeling-essentials.md) — modeling on `events`. Then [04](04-masterless-peers-and-placement.md) → [05](05-cap-and-tunable-consistency.md). Full path: [../README.md](../README.md#learning-path).
