# 03 — Data modeling essentials

Topics: **partition key**, **clustering keys**, **query patterns**, **denormalization** — tied to the shared lab table `lab_ks.events` from [02-lab-environment.md](02-lab-environment.md).

Prerequisite: keyspace and `events` table created ([02](02-lab-environment.md)).

---

## Partition key vs clustering key

In CQL, the **PRIMARY KEY** has two roles:

1. **Partition key** — the first part of the key. All rows with the same partition key are stored **together** on the same replicas (same **partition**). It is the unit of **distribution** and **atomicity** within a partition.
2. **Clustering key(s)** — following columns in the `PRIMARY KEY` definition. They **order** rows **inside** a partition and let you **range-scan** within that partition.

Example from the lab:

```sql
PRIMARY KEY (user_id, event_time)
```

| Part | Column | Role |
|------|--------|------|
| Partition key | `user_id` | Hashing places this user’s events on the ring; all events for one user live in **one partition**. |
| Clustering key | `event_time` | Rows for that user are **sorted** by `event_time` on disk, supporting time-range queries **per user**. |

**Rule of thumb:** You can efficiently query by **partition key** (and optional clustering bounds). You **cannot** efficiently query “all users for one timestamp” with this model—**that** would require a different table (different partition key) or a secondary index (with tradeoffs).

---

## Query patterns that work

**Allowed (efficient) examples** — same `user_id`, constrain `event_time` if needed:

```sql
SELECT * FROM events
WHERE user_id = 123e4567-e89b-12d3-a456-426614174000;

SELECT * FROM events
WHERE user_id = 123e4567-e89b-12d3-a456-426614174000
  AND event_time >= '2024-01-01 00:00:00+0000'
  AND event_time < '2025-01-01 00:00:00+0000';
```

**Problematic without another table:**

```sql
-- Typically NOT efficient as a full partition scan across the cluster:
SELECT * FROM events WHERE event_time = '2024-06-01 00:00:00+0000';
```

`event_time` is not the partition key, so the coordinator cannot know which partition(s) to hit without scanning—**model for the queries you need**.

---

## Denormalization (table-per-query)

Relational databases often **normalize** (one canonical table, join at read). Cassandra favors **denormalization**: **one table shape per query pattern** you need at scale, accepting duplicate data for different access paths.

Examples:

- **Feed by user** — `PRIMARY KEY (user_id, event_time)` (what you have).
- **Feed by global time** — if required, a **separate** table with `PRIMARY KEY ((bucket), event_time, user_id)` or similar, **written when events are inserted** (application or batch).

**Tradeoff:** Faster reads for known patterns and no cross-partition joins; **more writes** and **application logic** to keep redundant tables consistent.

---

## Lab A — Inspect sort order

**Goal:** See clustering order within one partition.

```sql
USE lab_ks;

INSERT INTO events (user_id, event_time, payload) VALUES
  (123e4567-e89b-12d3-a456-426614174010, '2024-06-01 12:00:00+0000', 'second');

INSERT INTO events (user_id, event_time, payload) VALUES
  (123e4567-e89b-12d3-a456-426614174010, '2024-06-01 10:00:00+0000', 'first');

SELECT event_time, payload FROM events
WHERE user_id = 123e4567-e89b-12d3-a456-426614174010;
```

**Deliverable:** Confirm rows return in **clustering key order** (default **ASC** for `event_time` unless you defined `CLUSTERING ORDER BY`).

---

## Lab B — Query that matches the model vs one that does not

1. Run a **good** query: `SELECT` by `user_id` only (or with `event_time` range).
2. In training only, try `ALLOW FILTERING` on a non-key column or pattern your instructor allows—observe warnings or performance.

**Deliverable:** One sentence: why **partition key first** matters for performance.

---

## Lab C — Sketch a second table (paper or comment)

Suppose you need “latest 10 events **globally**” in addition to “events **per user**.”

**Deliverable:** Briefly describe a second table’s `PRIMARY KEY` that could support that read (denormalized), and what the application would do on **insert**.

---

## Next

[04-masterless-peers-and-placement.md](04-masterless-peers-and-placement.md) — how partition keys map to the ring.
