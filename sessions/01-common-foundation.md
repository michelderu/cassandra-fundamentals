# Session 1 — Common foundation

**Phase 1.** Developers, platform engineers, SRE, and support.

**Duration:** 2 hours.

**Purpose:** A shared picture of Cassandra and of DSE, then proof on a cluster that any node can coordinate and that a partition key chooses the replicas.

**Cluster:** open-source Cassandra in Docker Compose. DSE is discussion only. The explanation for this session is in this file.

## You leave able to

- Say when Cassandra fits, and when a relational store or a warehouse fits better.
- Tell OSS Cassandra, DSE, HCD, and Astra apart without claiming they are different data models.
- Start the lab cluster, read `UN`, and create `lab_ks` at RF 3.
- Explain masterless placement: partition key → token → replicas.

## Agenda

| Minutes | Block |
|---------|--------|
| 0–15 | What it is good at |
| 15–35 | OSS, DSE, HCD, Astra |
| 35–70 | Lab — cluster and schema |
| 70–95 | Masterless ring |
| 95–120 | Lab — coordinator and endpoints |

**If you are behind:** skip the optional ring command in the last lab. Do not skip `getendpoints`.

---

## 1. What Cassandra is for

Words the rest of the course uses without stopping:

| Term | Meaning |
|------|---------|
| **CQL** | Cassandra Query Language. It looks like SQL and then refuses joins and ad-hoc filters. |
| **RF** | Replication factor. How many copies of each partition the keyspace stores. |
| **CL** | Consistency level. How many of those replicas must answer a given read or write. |
| **DC** | Datacenter. A failure domain the snitch names, and a key in `NetworkTopologyStrategy`. |

Cassandra is an **operational data store** for live applications: predictable latency at large scale. It is not the warehouse. You can export from it into an analytics stack. You do not run the batch questions here. Typical fits: events, time series, catalogs, sessions, messaging metadata, IoT ingest.

| Need | How this design meets it |
|------|--------------------------|
| Scale out | Add nodes. There is no single writer to scale up. |
| Low latency | `LOCAL_QUORUM` or `ONE` trades how many replicas must agree for how fast you return. |
| High availability | Copies on nodes, racks, and datacenters. A lost node is survived when RF and the consistency level were chosen for that loss. |
| More than one region | Each datacenter holds its own replicas. `LOCAL_QUORUM` means a quorum **in the coordinator’s datacenter**, so the request does not wait on the other region. |

Poor fits, said plainly:

- Rich ad-hoc joins. The model is query-first and denormalized. Sessions 3 and 4 are that model.
- Multi-key serializable transactions as the default way to write the domain. A lightweight transaction is a compare-and-set on one partition. Session 4 shows one, and why it is not a SQL habit.
- A small dataset with no availability requirement. A single-node SQL database is simpler.

Session 2 is the internals underneath this: placement, gossip, the log-structured storage engine, repair. That picture is the same on open-source Cassandra and on DSE. What changes is who runs the nodes, and which extra products share them.

---

## 2. OSS, DSE, HCD, Astra

Same CQL, same drivers, same partition rules. The difference is who runs the nodes and which extra products sit beside the database.

**Apache Cassandra (this lab).** You install and operate it. You own upgrades, repair, backups, and capacity.

**DataStax Enterprise (explain, do not lab).** A supported Cassandra distribution you still operate. The line most estates run is DSE 6.8 / 6.9 on a Cassandra 4.x core. Beyond the database, depending on what is enabled:

- OpsCenter and Lifecycle Manager for repair, backup, and metrics. Newer DataStax operations planes use Mission Control.
- Authentication, authorization, and encryption, often tied to LDAP or Kerberos.
- Workloads that share the same nodes: DSE Search (Solr), DSE Analytics (Spark), DSE Graph. They change capacity planning. A DSE node is not “Cassandra plus a logo” once Search or Analytics is on.

A correct schema and a correct driver configuration from this course are the right ones for DSE contact points. Nothing in the labs requires an OpsCenter UI or a Search index.

**HCD.** DataStax’s self-managed, Kubernetes-native platform, on-premises or in your cloud account. You still operate the stack. You are buying supported packaging and operational tooling (Mission Control in that ecosystem) where a fully vendor-hosted database plane is not allowed: regulated industries, hybrid cloud, data-residency rules. Licensing and support come with that packaging.

**Astra DB.** DataStax-operated Cassandra-compatible database-as-a-service on the major public clouds. Provisioning, patching, scaling, and the SLA are largely theirs. You give up low-level topology. You gain a shorter path to a CQL endpoint. Region choice and price follow the service.

| | OSS (labs) | DSE | HCD | Astra |
|--|------------|-----|-----|-------|
| Who operates | You | You, with a vendor build | You, supported platform | DataStax |
| Where | Your machines | Your machines or clusters | Often on-prem or your cloud | DataStax cloud |
| Extra products | None | Search, Analytics, Graph, ops tooling | Platform features | Managed service |
| Best when | Full control of the binary | Supported Cassandra on infrastructure you run | Self-managed Kubernetes | Fastest path to managed CQL |
| In this room | Every lab | Talk only | Talk only | Talk only |

**Check for the room (2 minutes, no cluster):** From a status page, which facts are plain Cassandra (`UN`, load, tokens) and which appear only because the estate bought DSE (OpsCenter repair service, a Search core, a Spark worker on the Cassandra nodes)?

---

## 3. Lab — cluster and schema

**About 35 minutes.** From the repository root.

The lab needs a Docker-compatible CLI (`docker` and `docker compose`). Docker Engine on Linux is the baseline. Docker Desktop is the usual macOS and Windows path, and some companies ban it. Podman (rootless; on a Mac or Windows it runs inside Podman Machine) and Colima (a small VM plus the Docker CLI) are the substitutes. If the CLI is `podman` rather than `docker`, either type `podman compose` where this file says `docker compose`, or for this shell only:

```bash
docker() { podman "$@"; }
```

Colima, when that is the chosen VM: `colima start --cpu 4 --memory 6`, then `docker context use colima` if the CLI is not talking to it. One runtime is enough. The commands below do not change.

```bash
docker compose up -d
docker exec cassandra-1 nodetool status
```

Wait until three rows show **UN**. Then:

```bash
docker exec -it cassandra-1 cqlsh cassandra-1 9042
```

```sql
SELECT cluster_name, release_version FROM system.local;
```

`cluster_name` is `training-lab`.

The snitch in Compose is `GossipingPropertyFileSnitch` and the only datacenter is `datacenter1`, so the keyspace uses `NetworkTopologyStrategy` (not `SimpleStrategy`, which ignores DC and rack).

```sql
CREATE KEYSPACE IF NOT EXISTS lab_ks
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
);
```

`user_id` is the partition key. `event_time` orders rows inside that partition. RF 3 on three nodes means every partition has a replica on every node — say that out loud; session 2’s failure lab depends on it.

```sql
DESCRIBE KEYSPACE lab_ks;
```

**You should see** `datacenter1: 3`. If an older `SimpleStrategy` keyspace is in the way: `DROP KEYSPACE lab_ks;` and create it again.

Leave `cqlsh` open if you can. Exit with `exit` when you need the host shell.

---

## 4. Masterless ring

No node is special. There is no primary and no metadata master the cluster depends on. Every node can coordinate a request and can serve the data it owns. If one node fails, the others keep serving. You grow capacity by adding machines, not by replacing one bigger master.

On each node the storage is local: a commit log, memtables, SSTables. Those are files and memory, not roles. Role-wise the nodes are peers. They stay in agreement through replication and through gossip, which session 2 opens up. Consistency is chosen per operation, not granted by “the” writer.

![Masterless architecture](../assets/architecture-masterless.png)

A master/slave design funnels writes through one machine. That machine is the throughput ceiling and a single failure. Here every node accepts reads and writes. More nodes can mean more aggregate throughput, when the data model allows it. You scale out on ordinary servers, or on Kubernetes, instead of scaling one box up.

![Peers vs master/slave](../assets/architecture-peers-vs-master-slave.png)

Placement uses the partition key, nothing else:

- The key is hashed to a token on the ring.
- **Vnodes** give each physical machine many small token ranges instead of one big slice, so a node joining or leaving moves less data.
- Replication then picks RF distinct owners walking the ring from that token. `SimpleStrategy` only has a count, so it ignores racks and datacenters. `NetworkTopologyStrategy` has a count **per datacenter name**. Those names are whatever the snitch reports for the nodes. In this lab the snitch reports `datacenter1`, and the keyspace asks for 3 replicas there. If the strings differ, the replicas are not placed.

![Consistent hashing and vNodes](../assets/architecture-consistent-hashing-vnodes.png)

On DSE the ring works the same way. Search and Analytics do not replace the partition key. Think token ranges, RF, and consistency level. There is no primary for all writes.

---

## 5. Lab — any node coordinates, the key picks replicas

**About 25 minutes.**

**A. Second coordinator.** On the host:

```bash
docker exec -it cassandra-2 cqlsh cassandra-2 9042
```

```sql
SELECT cluster_name FROM system.local;
USE lab_ks;
DESCRIBE TABLES;
```

`events` is visible from node 2. There is no “the” primary to connect to. Drivers in session 4 still want a local DC and token-aware routing; that is load balancing, not a master.

**B. Endpoints for one key.**

```sql
INSERT INTO events (user_id, event_time, payload)
VALUES (123e4567-e89b-12d3-a456-426614174000, toTimestamp(now()), 'placement-lab');
```

On the host:

```bash
docker exec cassandra-1 nodetool getendpoints lab_ks events 123e4567-e89b-12d3-a456-426614174000
```

**You should see** three addresses. With RF 3 and three nodes that list is the whole cluster. The command still matters: in production the same key returns three out of dozens, and a different `user_id` returns a different three.

**C. Optional, one minute.**

```bash
docker exec cassandra-1 nodetool describecluster
```

Note the name and the partitioner (`Murmur3Partitioner`). Token math can wait.

---

## Close

One sentence from each role is enough: a developer names the partition key, a platform engineer names the datacenter in the keyspace (`datacenter1`, the name the snitch reports), an SRE names “no master, RF 3”, support names `UN` and `getendpoints`.

**Next:** [Session 2](02-consistency-topology-storage.md). Leave the cluster up (`docker compose stop` only if the room must reboot).

**Not this session:** schema design beyond `events`, drivers, TTL, repair, OpsCenter.
