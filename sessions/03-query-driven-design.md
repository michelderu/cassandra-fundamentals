# Session 3 — Query-driven design

**Phase 2.** Development teams, architects, technical leads.

**Duration:** 2 hours.

**Purpose:** Design tables from access patterns so each production query hits a known partition and that partition stays bounded.

**Requires:** Phase 1 vocabulary (partition, RF, CL, SSTable) and `lab_ks.events` from session 1. If this group did not sit Phase 1, spend the first 15 minutes on [session 1, sections 4 and 5](01-common-foundation.md) and cut the optional clustering-order lab below.

## You leave able to

- Reject a design that starts from entities and joins.
- Split a primary key into partition key and clustering columns, including a composite partition key.
- Run the CQL for “this user’s events after time T” and point at the replicas with `getendpoints`.
- Spot a hot or wide partition and name bucketing before you reach for an index.

## Agenda

| Minutes | Block |
|---------|--------|
| 0–20 | Query-first rule |
| 20–40 | Four steps and the primary key |
| 40–75 | Lab — one partition, many rows, one range |
| 75–95 | Hot partitions and wide partitions |
| 95–115 | Lab — endpoints and clustering order |
| 115–120 | Write one query on paper |

**If you are behind:** skip lab B (clustering order). Do not skip the range query.

---

## 1. The rule

Relational habit: entities, normal forms, indexes, then whatever SQL you need, including joins.

Cassandra habit: list the queries first. Each production query becomes a table (or a materialized path) whose primary key **is** that query. If you cannot write it as equality on the partition key plus an optional range on clustering columns, in order, you do not have a Cassandra query yet.

**Golden rule:** one table per production access pattern.

![Relational vs Cassandra](../assets/modeling-relational-vs-cassandra.png)

Reference: [data-modeling/01](../data-modeling/01-intro-and-paradigm.md). The connectivity lab in that file is session 1; do not repeat it.

---

## 2. Four steps, then the key

1. **Access patterns** — frequency, latency, and whether the read must see the latest write (`QUORUM` / `LOCAL_QUORUM` vs `ONE`).
2. **Partition key** — equality lookup that selects one partition, or a small bounded set of them.
3. **Clustering columns** — order and uniqueness inside the partition.
4. **Another table** when a second pattern needs a different partition key. Session 4 writes both tables. Duplication is the design, not a mistake.

![Four-step process](../assets/modeling-four-step-process.png)

`events` is already step 2 and 3 for “this user’s events, ordered by time”:

```sql
PRIMARY KEY (user_id, event_time)
```

A **composite** partition key groups columns in extra parentheses. All of them are hashed together; clustering still follows:

```sql
PRIMARY KEY ((user_id, day), event_time)
```

That is how you stop one user from owning an unbounded partition when history is long. `(day)` alone is the opposite problem: every writer for “today” hits one partition. Session 4’s day table uses `(day, bucket)` for that reason.

![Primary key structure](../assets/modeling-primary-key-structure.png)

Reference: [data-modeling/02](../data-modeling/02-process-and-primary-key.md).

---

## 3. Lab — describe, insert, range

**About 35 minutes.** `cqlsh` on any node:

```sql
USE lab_ks;
DESCRIBE TABLE events;
```

Name the partition key and the clustering column from the output before you insert.

Pick one UUID and reuse it. Three rows, same user, different comments:

```sql
INSERT INTO events (user_id, event_time, payload)
VALUES (123e4567-e89b-12d3-a456-4266141740bb, '2024-06-01 12:00:00+0000', 'morning');

INSERT INTO events (user_id, event_time, payload)
VALUES (123e4567-e89b-12d3-a456-4266141740bb, '2024-06-01 15:00:00+0000', 'afternoon');

INSERT INTO events (user_id, event_time, payload)
VALUES (123e4567-e89b-12d3-a456-4266141740bb, '2024-06-02 09:00:00+0000', 'next-day');

SELECT * FROM events
WHERE user_id = 123e4567-e89b-12d3-a456-4266141740bb;
```

Rows come back in `event_time` order. That order was fixed at schema time.

```sql
SELECT * FROM events
WHERE user_id = 123e4567-e89b-12d3-a456-4266141740bb
  AND event_time > '2024-06-01 13:00:00+0000';
```

**You should see** two rows, not a scan of other users. The partition key is equality. The clustering column is a range. Both predicates are required in that order. A filter on `payload` is session 4’s anti-pattern, not this query.

---

## 4. Hot partitions and wide partitions

Placement follows the partition key. RF and CL do not spread a bad key. A **hot** partition is one key that takes a disproportionate share of operations; its replicas run hot and the rest of the cluster looks idle. A **wide** partition is one key with a huge number of rows or a huge payload; reads, repair, and compaction all suffer.

Mitigations you should be able to say:

- **Bucketing** — add a bucket or a time shard to the partition key: `(user_id, day)` or `(day, bucket)`.
- **TTL** — only when the product may forget the row. Session 4 labs it. Expiry becomes a tombstone, so it is not free.
- **Cardinality** — “one row per country” or “one partition per current hour for the whole product” will not scale.

![Token ring](../assets/modeling-partition-token-ring.png)

![Healthy vs hot partitions](../assets/modeling-healthy-vs-hot-partitions.png)

![Clustering order](../assets/modeling-clustering-order.png)

![Wide partitions](../assets/modeling-wide-partitions.png)

Clustering supports `=`, `>`, `<`, and `BETWEEN` in primary-key order. It does not sort by an arbitrary column at read time.

Reference: [data-modeling/03](../data-modeling/03-placement-and-partition-health.md), [data-modeling/04](../data-modeling/04-clustering-and-wide-partitions.md).

---

## 5. Lab — where it lives, and DESC order

**About 20 minutes.**

**A. Endpoints.** Same key as the inserts above, from the host:

```bash
docker exec cassandra-1 nodetool getendpoints lab_ks events 123e4567-e89b-12d3-a456-4266141740bb
```

Say which part of the primary key was hashed (only `user_id`) and which part only ordered rows (`event_time`).

Insert a **second** user id (change the last hex digit) and run `getendpoints` again if you want to see that another key can map to the same three nodes in this three-node RF-3 lab. In a larger cluster the sets differ. Do not “fix” a model because this lab returned every node.

**B. Optional — `CLUSTERING ORDER BY`.** Cut this first if the clock is short.

```sql
CREATE TABLE IF NOT EXISTS dm_cluster_demo (
  demo_id uuid,
  seq int,
  note text,
  PRIMARY KEY (demo_id, seq)
) WITH CLUSTERING ORDER BY (seq DESC);

INSERT INTO dm_cluster_demo (demo_id, seq, note)
VALUES (123e4567-e89b-12d3-a456-426614174000, 1, 'first');
INSERT INTO dm_cluster_demo (demo_id, seq, note)
VALUES (123e4567-e89b-12d3-a456-426614174000, 2, 'second');

SELECT * FROM dm_cluster_demo
WHERE demo_id = 123e4567-e89b-12d3-a456-426614174000;
```

`2` comes back before `1`. “Latest first” in a UI is a schema choice, not an `ORDER BY` you invent in the query. `event_time DESC` is the same idea on a real events table.

---

## 6. Paper check (5 minutes)

Write the CQL, not the prose, for: **the 20 latest events for one known user**.

A passing answer restricts `user_id` with equality. Latest-first needs `CLUSTERING ORDER BY (event_time DESC)` on the table, or the application reverses an ascending result and risks reading more than 20 rows. `LIMIT 20` without the partition key is not an answer.

---

## Close

**Next:** [session 4](04-cql-drivers-performance.md) — the second table, tombstones, TTL, the driver, and the queries you must not ship.

**Not this session:** `ALLOW FILTERING`, index creation, dual writes, Python. The checklist in [data-modeling/07](../data-modeling/07-checklist-labs-and-blueprint.md) is the take-home, not another lab hour.
