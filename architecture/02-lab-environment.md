# 02 — Lab environment

This module gets the **Docker Compose** cluster running and prepares a shared **keyspace** for later labs.

**Terms used here:**

| Term | Meaning |
|------|---------|
| **docker compose** | Start/stop the stack. |
| **nodetool status** | Shows which nodes are **UN** (up/normal = healthy and serving traffic). |
| **cqlsh** | Cassandra Query Language shell (interactive; run inside a container). |
| **Keyspace** | Named bucket for tables plus replication settings. |
| **RF** | Replication factor (how many copies of each partition). |
| **UN** | Up / Normal. |

## Container runtime options

This lab expects a Docker-compatible CLI (`docker` + `docker compose`). You can run it with several local container stacks:

| Option | Works with this lab? | Notes |
|--------|-----------------------|-------|
| **Docker Engine + Compose v2** | **Yes (recommended baseline)** | Native Linux setup; simplest path in most dev environments. |
| **Docker Desktop** | **Yes** | Common on macOS/Windows, but often restricted or disallowed in enterprise environments due to licensing or policy. |
| **Podman CLI** | **Yes** | Rootless and enterprise-friendly; CLI is similar but not identical to Docker. Use `podman compose` or a Docker-compatible wrapper. |
| **Podman Desktop** | **Yes** | GUI on top of Podman; good alternative where Docker Desktop is not approved. Verify Compose support and socket compatibility. |
| **Colima (macOS/Linux VM helper)** | **Yes** | Runs a lightweight VM and exposes a Docker-compatible daemon; useful if you cannot use Docker Desktop. |
| **Rancher Desktop / Lima-based setups** | **Usually** | Can work if Docker-compatible mode is enabled and `docker compose` is available. |

### Enterprise policy notes

- If your company does not allow **Docker Desktop**, use **Docker Engine** (Linux) or **Podman/Podman Desktop**.
- For Podman-based setups, ensure the Docker-compatible socket/alias is enabled so lab commands keep working.
- If your runtime does not provide `docker compose`, translate commands to the equivalent (`podman compose`, etc.).

### Helper options (Podman compatibility)

If you use Podman but want to run this guide without changing every command, use one of these helpers:

```bash
# Shell wrapper (current session)
docker() { podman "$@"; }
```

```bash
# Persist wrapper for bash
echo 'docker() { podman "$@"; }' >> ~/.bashrc
source ~/.bashrc
```

If aliases are blocked by policy, run a wrapper script or just replace `docker`/`docker compose` with `podman`/`podman compose` manually.

### If your environment needs Colima

Use Colima when Docker Desktop is not allowed but you still want Docker-compatible commands.

```bash
# Install (macOS examples)
brew install colima docker docker-compose

# Start Colima VM
colima start

# Verify Docker CLI talks to Colima
docker context show
docker version
docker compose version
```

If `docker` cannot reach the daemon after `colima start`, switch to the Colima context:

```bash
docker context use colima
```

Then run this lab exactly as written:

```bash
docker compose up -d
docker exec cassandra-1 nodetool status
```

If resources are tight, start Colima with more memory/CPU (example):

```bash
colima start --cpu 4 --memory 6
```

**Prerequisites:** A Docker-compatible runtime with Compose support, plus ~4 GB RAM free. See the [repository README](../README.md).

---

## Concepts (brief)

Before hands-on work, you need a real cluster: **three Cassandra peers** on one machine, isolated by Docker networking. The lab uses **RF = 3** to match three nodes (three copies of each partition). See the **Terms** table above for tools and abbreviations.

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

[03-masterless-peers-and-placement.md](03-masterless-peers-and-placement.md) — placement and the ring. Full path: [repository README](../README.md#learning-path).
