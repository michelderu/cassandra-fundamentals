# 03 — Placement on the ring and partition health

Topics: **consistent hashing**, **`nodetool getendpoints`**, **RF/CL vs bad keys**, **even load vs hot partitions**, **bucketing**, **lab: `getendpoints`**.

**Terms:**

| Term | Meaning |
|------|---------|
| **Hot partition** | A partition that receives a disproportionate share of reads/writes; its replicas become a bottleneck while other nodes stay idle. |
| **Bucketing** | Splitting what would be one huge partition into many smaller ones (e.g. add `day` or `hour` to the partition key). |

**Previous:** [02-process-and-primary-key.md](02-process-and-primary-key.md). **Next:** [04-clustering-and-wide-partitions.md](04-clustering-and-wide-partitions.md).

---

## Distributed placement via consistent hashing

The **partition key** is hashed to a **token** on the ring. That token determines **which nodes** hold replicas for that data. In the lab you can see concrete endpoints with:

```bash
docker exec cassandra-1 nodetool getendpoints lab_ks events '<user_id-uuid>'
```

(See [03-masterless-peers-and-placement.md](../architecture/03-masterless-peers-and-placement.md).)

![Distributed data placement via consistent hashing](../assets/modeling-partition-token-ring.png)

**Law of placement:** **Placement and load follow the partition key.** **Replication factor (RF)** and **consistency level (CL)** do **not** fix a bad key—they only control **how many replicas** participate in each operation ([04-cap-and-tunable-consistency.md](../architecture/04-cap-and-tunable-consistency.md)).

---

## Healthy vs failing partitioning

**Good partition keys** often:

- Match a **natural query scope** (“all events for this user”).
- **Spread** read and write load across **many distinct** partition key values.

**Risky patterns:**

- **Too few partitions** (effectively everything under one key).
- **Time-only** partition keys on **high-volume** streams (all “current” traffic can hit one partition until the bucket rolls).

**Mitigation:** **Bucketing** — e.g. `(user_id, day)` instead of only `user_id` when per-user volume is huge, or combine dimensions so no single partition grows without bound.

![Diagnostic: healthy vs failing partitioning](../assets/modeling-healthy-vs-hot-partitions.png)

**Takeaways:** Even load → horizontal scale. **Hot keys** → one node (and its replicas) glow while the rest of the cluster idles.

---

## Lab — Replica endpoints (`getendpoints`)

**Goal:** Map a **partition key** value to **which nodes** store replicas.

**Environment:** [Docker Compose](README.md#lab-cluster-docker-compose) cluster; `lab_ks.events` populated (e.g. 02 Lab B).

1. In **cqlsh**, ensure you have at least one row with a **known** `user_id`, or insert one:

   ```sql
   USE lab_ks;
   INSERT INTO events (user_id, event_time, payload)
   VALUES (123e4567-e89b-12d3-a456-426614174000, toTimestamp(now()), 'dm03-placement');
   ```

2. On the **host** (not inside cqlsh), run (use the same UUID as a bare string):

   ```bash
   docker exec cassandra-1 nodetool getendpoints lab_ks events 123e4567-e89b-12d3-a456-426614174000
   ```

**Deliverable:** List the endpoints returned. **Optional:** Change `user_id` to a different UUID, insert again, run `getendpoints` for that key — compare how endpoints differ (token distribution).

---

## Next

[04-clustering-and-wide-partitions.md](04-clustering-and-wide-partitions.md) — clustering order and wide partitions.
