# 06 — Anti-patterns and performance traps

Topics: **secondary indexes**, **`ALLOW FILTERING`**, **lightweight transactions (LWT) and hot keys**, **labs: filter + index + LWT**.

**Terms:**

| Term | Meaning |
|------|---------|
| **Secondary index** | An index that is **distributed** with caveats: traditional secondary indexes are often poor for **high-cardinality** “find anywhere in the cluster” queries—can fan out to **every** node. However, the newer **Storage-Attached Index (SAI)** is designed for efficiency and scalability, making it a **good choice** for many secondary index use cases, especially for flexible queries requiring more than just primary or clustering keys. |
| **LWT** | Lightweight transaction (`IF`, `IF NOT EXISTS`) using **Paxos**-style rounds—**several** round-trips vs a normal write ([07-self-healing-lwt-and-summary.md](../architecture/07-self-healing-lwt-and-summary.md)). |

**Previous:** [05-tombstones-and-denormalization.md](05-tombstones-and-denormalization.md). **Next:** [07-checklist-labs-and-blueprint.md](07-checklist-labs-and-blueprint.md).

---

## When convenience becomes a trap

**Secondary indexes**

- Useful in **narrow** cases (often **low cardinality**, or scoped queries where the index is not doing a cluster-wide probe).
- **Trap:** High-cardinality lookups “by email across the whole database” via secondary index → **fan-out** to many nodes → high latency and load. Prefer a table whose **partition key** matches the lookup.

**`ALLOW FILTERING`**

- Tells the coordinator it may **scan** tables to satisfy predicates on **non-partition-key** columns.
- **Trap:** On large data sets this becomes **full partition or cluster scans**. Treat production use with extreme skepticism—often a sign the **schema is wrong** for that query.

**Lightweight transactions**

- Give **linearizable** conditional updates (compare-and-set semantics).
- **Cost:** Roughly **~4×** the round-trips of a simple write in typical discussions—use **sparingly**.
- **Trap:** **Hot partition** + **frequent LWT** → **contention** and tail latency. Prefer idempotent designs and partition keys that spread serializing work.

![Anti-patterns and performance traps](../assets/modeling-anti-patterns.png)

**Takeaways:** If the hot query needs a column, that column usually belongs in a **primary key** or a **dedicated denormalized table**, not behind an index + filter as the main path.

> **Note:** While Cassandra has historically offered only eventual and timeline consistency (using LWTs for strongly consistent updates), **Cassandra 6** (in preview as of 2024) introduces full **ACID transactional support** via the new **Accord** protocol. Accord brings true distributed transactions—atomic, consistent, isolated, and durable—directly to Cassandra, allowing multi-row and multi-partition transactions with strong guarantees. This fundamental change will unlock more flexible modeling and application patterns, reducing the need for workarounds formerly required for transactional workloads.

---

## Lab A — `ALLOW FILTERING` vs index

**Goal:** Feel why **non-key** filters are dangerous at scale.

**Environment:** [Docker Compose](README.md#lab-cluster-docker-compose); `lab_ks.events` with varied `payload` values.

1. `USE lab_ks;`
2. Pick a `payload` you know exists. Run:

   ```sql
   SELECT * FROM events WHERE payload = 'your-payload-here' ALLOW FILTERING;
   ```

   Also try it without `ALLOW FILTERING`.

3. **Optional — secondary index:** `CREATE INDEX IF NOT EXISTS ON events (payload);` then repeat the `SELECT` **without** `ALLOW FILTERING` (behavior depends on Cassandra version; note any warning or coordinator fan-out in [tracing](https://cassandra.apache.org/doc/latest/cassandra/tools/cqlsh.html)).

4. **Optional — SAI (Storage-Attached Index):** If your Cassandra version supports **SAI** (Cassandra 4.0+ with SAI enabled, or DataStax Enterprise), create an SAI index instead of the traditional secondary index:

   ```sql
   -- For SAI, syntax may vary slightly by version; commonly:
   CREATE CUSTOM INDEX IF NOT EXISTS ON events (payload)
       USING 'StorageAttachedIndex';
   ```
   
   Then re-run the same `SELECT` query **without** `ALLOW FILTERING`.  
   **Observe:** SAI indexes are much more efficient and scalable for flexible queries, as they avoid the fan-out and coordinator load typical of classic secondary indexes.  
   **Note:** SAI is the **recommended** approach for secondary indexing as of Cassandra 4.0+ and DataStax Astra DB, offering improved performance and operational simplicity for real-world workloads.


**Deliverable:** Why could this be a poor primary access pattern for huge tables even if it “works” in the lab?

---

## Lab B — Lightweight transaction (optional)

**Goal:** See conditional write **cost** (Paxos rounds) — use **sparingly**.

**Environment:** same cluster.

1. Create a tiny scratch table:

   ```sql
   USE lab_ks;
   CREATE TABLE IF NOT EXISTS dm_lwt_demo (
     id uuid PRIMARY KEY,
     v int
   );
   ```

2. Insert with a condition:

   ```sql
   INSERT INTO dm_lwt_demo (id, v) VALUES (123e4567-e89b-12d3-a456-4266141740aa, 0) IF NOT EXISTS;
   ```

3. Run the same `INSERT ... IF NOT EXISTS` again and observe `[applied]` vs `false`.

**Deliverable:** One line: when would you use LWT vs application-level idempotency? ([architecture/07-self-healing-lwt-and-summary.md](../architecture/07-self-healing-lwt-and-summary.md))

---

## Next

[07-checklist-labs-and-blueprint.md](07-checklist-labs-and-blueprint.md) — pre-flight checklist, capstone visuals, and labs.
