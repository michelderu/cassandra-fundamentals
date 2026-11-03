# Session 2 — Consistency, topology, and storage

**Phase 1.** Same audience as session 1.

**Duration:** 2 hours.

**Purpose:** Decide how much agreement a request needs, see how nodes learn membership, and follow one write onto disk. Then stop a node and watch consistency and hints, still on open-source Cassandra.

**Requires:** `lab_ks.events` from [session 1](01-common-foundation.md).

## You leave able to

- Choose `ONE`, `QUORUM` / `LOCAL_QUORUM`, or `ALL` and say what breaks when a node is down.
- Read a snitch and a datacenter, and say why `LOCAL_QUORUM` exists.
- Trace a write: commit log, memtable, SSTable, compaction, tombstone — at architecture depth.
- Name hinted handoff, read repair, and anti-entropy repair, and see a hint directory once.

## Agenda

| Minutes | Block |
|---------|--------|
| 0–20 | CAP and consistency levels |
| 20–45 | Lab — `ONE` vs `QUORUM`, one trace |
| 45–65 | Gossip, snitch, multi-DC |
| 65–80 | Lab — `describecluster` and the snitch |
| 80–100 | Storage engine, plus a flush |
| 100–120 | Lab — one node down |

**If you are behind:** skip the trace in the first lab. Do not skip the node-down lab.

---

## 1. CAP and tunable consistency

Under a network partition you do not get perfect linearizability and an answer from every side. Cassandra keeps serving (availability, partition tolerance) and lets each statement say how many replicas must agree.

For RF = 3, a quorum is 2. **R + W > RF** means the read set and the write set overlap, so a successful read sees the latest successful write. `QUORUM` + `QUORUM` does that. `ONE` + `ONE` does not.

| Level | RF = 3, one DC | Use when |
|-------|----------------|----------|
| `ONE` | 1 replica | Lowest latency, stale reads are acceptable |
| `QUORUM` | 2 of 3 | Default for correctness inside one DC |
| `LOCAL_QUORUM` | Quorum **in the coordinator’s DC** | Production multi-DC. Same as `QUORUM` in this lab |
| `ALL` | Every replica | Rare. Any down replica fails the statement |

DSE uses the same levels. A Search query is not a consistency level; do not treat it as one.

![CAP — Cassandra in AP space](../assets/architecture-cap-theorem.png)

![Tunable consistency](../assets/architecture-tunable-consistency.png)

Reference: [architecture/04](../architecture/04-cap-and-tunable-consistency.md).

---

## 2. Lab — feel a consistency level

**About 25 minutes.** In `cqlsh` on `cassandra-1`:

```sql
USE lab_ks;

CONSISTENCY ONE;
SELECT * FROM events LIMIT 5;

CONSISTENCY QUORUM;
SELECT * FROM events LIMIT 5;
```

The prompt shows the level. On a healthy cluster both succeed. The difference shows up in the trace and when a node is down.

```sql
CONSISTENCY QUORUM;
TRACING ON;

INSERT INTO events (user_id, event_time, payload)
VALUES (123e4567-e89b-12d3-a456-426614174001, toTimestamp(now()), 'trace-quorum');

TRACING OFF;
```

**You should see** the coordinator write to replicas and wait until quorum acknowledges. Name that in one sentence. A second trace at `ONE` is optional and is the first thing to cut.

---

## 3. Gossip and topology

Gossip spreads membership, health, schema, and the token map. It is the control plane, not the data path. The failure detector uses a suspicion score (phi accrual) so a single delayed packet does not mark a node dead.

The **snitch** tells Cassandra which rack and datacenter a node is in. **NetworkTopologyStrategy** uses that to place replicas. Clients use `LOCAL_*` levels so a request does not wait for the other region.

This lab is one DC on purpose. The snitch is already `GossipingPropertyFileSnitch`, which is what you keep when a second DC appears. `SimpleSnitch` would throw that information away.

DSE clusters use the same gossip and the same snitch model. OpsCenter watches this state; it does not replace it.

![Gossip and failure detection](../assets/architecture-gossip-failure-detection.png)

![Topology and multi-DC](../assets/architecture-topology-multi-dc.png)

Reference: [architecture/05](../architecture/05-gossip-and-topology.md).

---

## 4. Lab — name, partitioner, snitch

**About 15 minutes.** On the host:

```bash
docker exec cassandra-1 nodetool describecluster
docker exec cassandra-1 nodetool gossipinfo | head -40
docker exec cassandra-1 grep -E '^endpoint_snitch' /etc/cassandra/cassandra.yaml
```

**You should see** cluster name `training-lab`, `Murmur3Partitioner`, peer entries in gossip, and `GossipingPropertyFileSnitch`.

`nodetool failuredetector` is optional. Phi values are the suspicion scores from the diagram.

---

## 5. Storage engine, one flush

A write appends to the **commit log** (durability) and lands in a **memtable** (memory). A flush freezes that memtable into an immutable **SSTable**. Reads merge the memtable and the SSTables, skip files with a Bloom filter, and resolve duplicates by timestamp (last write wins). Compaction merges files so reads touch fewer of them. A **delete writes a tombstone**; it does not punch a hole in an old SSTable. Session 4 spends lab time on tombstones and TTL. This session only needs the picture.

![Write path — LSM](../assets/architecture-storage-write-path-lsm.png)

![Flush to SSTables](../assets/architecture-storage-memtable-flush.png)

![Read path](../assets/architecture-storage-read-path.png)

![Compaction](../assets/architecture-storage-compaction.png)

![Tombstones](../assets/architecture-storage-tombstones.png)

**Lab, about 10 minutes.**

```sql
USE lab_ks;
INSERT INTO events (user_id, event_time, payload)
VALUES (aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee, toTimestamp(now()), 'flush-lab');
```

```bash
docker exec cassandra-1 nodetool flush lab_ks events
docker exec cassandra-1 sh -c 'ls /var/lib/cassandra/data/lab_ks/events-*/ | head'
```

**You should see** a `*-Data.db` file. That is the SSTable from the diagram, on this node.

Reference, including compaction and a delete you are not running today: [architecture/06](../architecture/06-storage-engine-write-through-read.md).

---

## 6. Lab — stop one node

**About 20 minutes.** Throwaway cluster only. RF is 3 and every partition includes all three nodes, so `cassandra-3` is a replica for every key.

**Hints and repair, said before you type.** If a replica is down, the coordinator can store a **hint** and replay it when the node returns. **Read repair** fixes a stale replica when a read notices disagreement. **`nodetool repair -pr`** compares data without waiting for a client read. You will see the hint directory. You will not run repair in this session; the command and the warning live in [architecture/07](../architecture/07-self-healing-lwt-and-summary.md). LWT waits until session 4.

![Hints and repair](../assets/architecture-hints-repair.png)

```bash
docker compose stop cassandra-3
```

Wait until `nodetool status` on `cassandra-1` shows `cassandra-3` as down (often 30–60 seconds). The first statement at `ALL` can sit until a timeout if the failure detector has not convicted the node yet.

In `cqlsh` on `cassandra-1`:

```sql
USE lab_ks;

CONSISTENCY ALL;
INSERT INTO events (user_id, event_time, payload)
VALUES (123e4567-e89b-12d3-a456-426614174010, toTimestamp(now()), 'all-should-fail');
```

That insert fails: `ALL` needs the down replica.

```sql
CONSISTENCY ONE;
INSERT INTO events (user_id, event_time, payload)
VALUES (123e4567-e89b-12d3-a456-426614174011, toTimestamp(now()), 'one-should-succeed');
```

That insert succeeds. The coordinator (`cassandra-1`) should hold a hint for `cassandra-3`:

```bash
docker exec cassandra-1 sh -c 'ls -la /var/lib/cassandra/hints/'
```

Bring the node back:

```bash
docker compose start cassandra-3
docker exec cassandra-1 nodetool status
```

Wait for **UN**. List the hints directory again. Replay is asynchronous; empty immediately is fine, empty a minute later is the point.

Set the shell back before you leave:

```sql
CONSISTENCY QUORUM;
```

**Say this once:** availability won because the client asked for `ONE`. The missing replica catches up from a hint, from read repair, or from `nodetool repair`. DSE’s repair service schedules that last path. The mechanism is still repair.

![Architect’s summary](../assets/architecture-summary.png)

---

## Close

Three questions, spoken, no new commands:

1. Why is there no master in this cluster?
2. What does RF 3 plus quorum reads and writes guarantee about overlap?
3. Name two ways replicas converge without the client reading (hints, read repair, or anti-entropy repair — any two).

**Next:** Phase 2 starts at [session 3](03-query-driven-design.md). Phase 1 is done.

**Not this session:** primary-range repair, compaction strategy tuning, LWT, TTL, driver code.
