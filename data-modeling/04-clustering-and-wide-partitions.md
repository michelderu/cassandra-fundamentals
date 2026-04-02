# DM 04 — Clustering order and the threat of wide partitions

Topics: **range queries on clustering**, **`CLUSTERING ORDER BY`**, **wide partition risks**, **bucketing, TTL, cardinality**.

**Terms:**

| Term | Meaning |
|------|---------|
| **Wide partition** | A partition that is very large in rows or payload size; stresses reads, repair, heap, and compaction. |

**Previous:** [03-placement-and-partition-health.md](03-placement-and-partition-health.md). **Next:** [05-tombstones-and-denormalization.md](05-tombstones-and-denormalization.md).

---

## Clustering: order inside the partition

Within one partition, rows are stored in **clustering key order** (unless you override with `CLUSTERING ORDER BY`). Efficient queries typically:

1. Restrict **`WHERE`** to the **partition key** (equality).
2. Optionally bound **clustering** columns with `=`, `>`, `<`, `BETWEEN` — **in primary key order**.

Example:

```sql
WHERE user_id = ?
  AND event_time > ?
```

That hits **one partition**, then applies an efficient **range** on clustering. Clustering **does not** give arbitrary sort orders on non-key columns—you only get what you declared in the `PRIMARY KEY` and clustering options.

![Clustering: order inside the partition](../assets/dm-07-clustering-order.png)

**Takeaways:** Sort order is largely a **write-time** choice (schema); reads benefit when access patterns match.

---

## The threat of wide partitions

Partitions are not free to grow forever. **Very wide** partitions increase:

- **Reads** — More SSTable components to merge per read ([06-storage-engine-write-through-read.md](../architecture/06-storage-engine-write-through-read.md)).
- **Maintenance** — Heavier **repair** and compaction scope on that partition.
- **Resources** — **Heap** and **GC** pressure on coordinators and replicas.

**Mitigations:**

- **Bucketing** — Split logical data across more partition keys (time shards, hashes, etc.).
- **TTL** — Expire old data where the product allows it.
- **Realistic cardinality** — Model for actual volumes, not “one partition per global type.”

![The threat of wide partitions](../assets/dm-08-wide-partitions.png)

**Takeaways:** Treat unbounded partition growth as a **design bug** unless you have measured otherwise.

---

## Next

[05-tombstones-and-denormalization.md](05-tombstones-and-denormalization.md) — deletes, tombstones, and duplication across tables.
