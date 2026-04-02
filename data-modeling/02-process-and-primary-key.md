# 02 — Modeling process and primary key structure

Topics: **four-step process**, **partition key vs clustering**, **lab `events` example**, **labs: DESCRIBE + insert rows**.

**Terms:**

| Term | Meaning |
|------|---------|
| **Composite partition key** | Multiple columns in parentheses as the first `PRIMARY KEY` component, e.g. `PRIMARY KEY ((user_id, day), …)` — all listed columns identify **one** partition. |
| **Simple partition key** | A single column as the partition key: `PRIMARY KEY (user_id, …)`. |

**Previous:** [01-intro-and-paradigm.md](01-intro-and-paradigm.md). **Next:** [03-placement-and-partition-health.md](03-placement-and-partition-health.md).

---

## Cassandra data modeling process

Work **in order**:

1. **List access patterns** — For each pattern, note read/write frequency, **latency budget**, and whether you need **strong** or **eventual** behavior (tie to **CL** in [04-cap-and-tunable-consistency.md](../architecture/04-cap-and-tunable-consistency.md)).
2. **Choose partition key(s)** — So the query **narrows to one partition** (or a small, bounded set). Avoid cluster-wide scans.
3. **Define clustering columns** — **Row order** and uniqueness **inside** the partition (e.g. `event_time DESC` for “latest first”).
4. **Duplicate data when needed** — If two patterns need **different partition keys**, use **two tables** (or a carefully chosen materialized path). Accept denormalization.

![Cassandra data modeling process](../assets/modeling-four-step-process.png)

**Takeaway:** If you cannot express a pattern as **known partition key + optional range on clustering**, you are still in purely relational thinking.

---

## Primary key: partitioning and clustering

The `PRIMARY KEY` has two roles:

- **Partition key** — Hashed to a **token** on the ring; decides **which replicas** store the partition. All rows sharing the same partition key live in **one partition** on disk.
- **Clustering key(s)** — Follow the partition key; define **sort order** on disk (default ascending; override with `CLUSTERING ORDER BY`) and **uniqueness** of each row within the partition.

Example aligned with the lab table `events` ([02-lab-environment.md](../architecture/02-lab-environment.md)):

```sql
PRIMARY KEY (user_id, event_time)
```

Here `user_id` is the partition key and `event_time` is the clustering key. If you use a **composite** partition key, extra parentheses group those columns, e.g. `PRIMARY KEY ((user_id, day), event_time)`.

![Primary key structure: partitioning and clustering](../assets/modeling-primary-key-structure.png)

**Takeaways:** **Partitioning** answers *where* data lives in the cluster; **clustering** answers *how rows are ordered* inside that partition.

---

## Lab A — Inspect primary key on `events`

**Goal:** See partition key vs clustering in **CQL metadata**.

**Environment:** [Docker Compose lab stack](README.md#lab-cluster-docker-compose) with `lab_ks` / `events` from [architecture/02-lab-environment.md](../architecture/02-lab-environment.md).

1. In **cqlsh**: `USE lab_ks;` then `DESCRIBE TABLE events;`
2. From the output, name the **partition key** column(s) and **clustering** column(s).

**Deliverable:** One sentence each: what the partition key controls, what clustering controls.

---

## Lab B — Insert rows and read within one partition

**Goal:** Same `user_id`, multiple `event_time` values — one **partition**, many **rows**.

**Environment:** same as Lab A ([README](README.md#lab-cluster-docker-compose), [architecture/02](../architecture/02-lab-environment.md)).

1. Pick a fixed `user_id` UUID (use `uuid()` once and copy the value, or paste a literal UUID).
2. Insert **two** rows with the same `user_id` and **different** `event_time` / `payload` values.
3. Query:

   ```sql
   SELECT * FROM events WHERE user_id = <your-uuid>;
   ```

**Deliverable:** Confirm rows appear in **clustering** order (`event_time` ascending by default). How would you ask for “events after time T” in one partition?

---

## Next

[03-placement-and-partition-health.md](03-placement-and-partition-health.md) — consistent hashing, placement, and healthy vs hot partitions.
