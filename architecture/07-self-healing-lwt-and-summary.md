# 07 — Self-healing (hints & repair), LWT, summary

Topics: **hinted handoff**, **read repair**, **anti-entropy repair**, **lightweight transactions (Paxos)**, **architect summary**.

**Terms:**

| Term | Meaning |
|------|---------|
| **Anti-entropy repair** | Background compare-and-sync of data between replicas (often using **Merkle trees**—hash trees of data ranges). |
| **LWT** | Lightweight transactions. |
| **Paxos** | Consensus protocol family; Cassandra uses LWT for linearizable `IF` / `IF NOT EXISTS` updates. |

**Previous:** [06-storage-engine-write-through-read.md](06-storage-engine-write-through-read.md).

---

## 13. Self-healing: hints and repairs

- **Hinted handoff:** If a replica is **temporarily down**, the coordinator may store a **hint** and deliver when the peer returns.
- **Read repair:** On read, if replicas disagree, the coordinator can **write back** the latest version to stale replicas (policy-dependent).
- **Anti-entropy repair:** `nodetool repair` compares data between nodes (via **Merkle trees** in the repair protocol) and fixes divergence without relying on a client read.

![Hints and repair](../assets/image-b5f792eb-a5bb-4a89-9dea-7eeae0ea40b7.png)

**Takeaways:** Operational hygiene: schedule **repair**; understand **read repair** impact on read latency.

---

## 14. LWT (Lightweight Transactions)

**LWT** provides **linearizable** conditional updates (`IF`, `IF NOT EXISTS`) via **Paxos-style** rounds—several network round-trips vs a normal write.

**Cost:** Often **~4×** round-trips vs a simple write—use only where needed.

![LWT and Paxos](../assets/image-0d007069-3093-4d8b-8421-705578190309.png)

**Takeaways:** Hot partitions + LWT = contention; prefer idempotent design where possible.

---

## 15. Summary

| Theme | One-liner |
|-------|-----------|
| **Write** | Append-only **LSM**; high throughput. |
| **Read** | **Merged** view; Bloom filters, caches, SSTable seeks. |
| **Scale** | **Linear**, **vNode**-based, **masterless**. |
| **Consistency** | **Tunable**; **AP**-leaning default with **eventual** convergence. |
| **Ideal fit** | **High velocity**, **geo-distributed**, **uptime**-sensitive workloads when the model fits. |

![Architect’s summary](../assets/image-e62b7935-dd49-4f58-b603-4ab0c1081926.png)

---

## Lab A — Hinted handoff (observation)

**Goal:** After a replica is **down**, see **on-disk hint files** on a live coordinator, then relate to metrics.

**Warning:** Stopping nodes is for **throwaway** lab clusters only (see [04-cap-and-tunable-consistency.md](04-cap-and-tunable-consistency.md) Lab C).

### A.1 — Stop a node, write, inspect the hints directory

1. **Stop** one replica (here `cassandra-3`):

   ```bash
   docker compose stop cassandra-3
   ```

   Wait ~30 seconds so other nodes **mark it down** (failure detector).

2. From **cqlsh on `cassandra-1`** (same as earlier labs), run **writes** that still succeed while one replica is missing. Use **`CONSISTENCY ONE`** so the coordinator does not require a quorum of live replicas:

   ```sql
   USE lab_ks;
   CONSISTENCY ONE;
   INSERT INTO events (user_id, event_time, payload)
   VALUES (uuid(), toTimestamp(now()), 'hints-lab-1');
   INSERT INTO events (user_id, event_time, payload)
   VALUES (uuid(), toTimestamp(now()), 'hints-lab-2');
   ```

   Run **several** inserts with different `user_id` values so at least one partition lists the stopped node among its replicas (RF=3; not every key uses the same three nodes). If the hints directory stays empty, add a few more rows.

3. **List hint storage** on the coordinator you used for cqlsh (here `cassandra-1`). Hints live under **`/var/lib/cassandra/hints/`** (subfolders/files are often named by **destination** identity—exact layout varies by version):

   ```bash
   docker exec cassandra-1 sh -c 'ls -la /var/lib/cassandra/hints/'
   docker exec cassandra-2 sh -c 'ls -la /var/lib/cassandra/hints/'
   ```

4. **Start** the node again and wait until `nodetool status` shows **UN**:

   ```bash
   docker compose start cassandra-3
   docker exec cassandra-1 nodetool status
   ```

5. **List hint storage** again. The folder should be empty now.

   ```bash
   docker exec cassandra-1 sh -c 'ls -la /var/lib/cassandra/hints/'
   ```

### A.2 — Hint-related metrics (names vary by version)

```bash
docker exec cassandra-1 nodetool tpstats | grep -i hint
docker exec cassandra-1 nodetool netstats
```

**Deliverable:** (1) What appeared under **`/var/lib/cassandra/hints/`** after writes while `cassandra-3` was stopped? (2) Whether **HintedHandOff** (or similar) shows up in `tpstats` and what you infer.

---

## Lab B — Repair (small scope)

**Warning:** Full cluster repair is heavy. For training, **primary range repair on one node** after you understand ops impact:

```bash
docker exec cassandra-1 nodetool repair lab_ks --full
```

On large data this is slow; with the tiny lab dataset it should finish quickly.

**Deliverable:** Paste exit code / final line from repair, or summarize “completed without error.”

**Production note:** Prefer **incremental repair** and **subrange** strategies per your Cassandra version and ops guide—not covered in detail here.

---

## Lab C — Lightweight transaction

In **cqlsh**:

```sql
USE lab_ks;

CREATE TABLE IF NOT EXISTS inventory (
  sku text PRIMARY KEY,
  qty int
);

INSERT INTO inventory (sku, qty) VALUES ('lwt-demo', 10);

UPDATE inventory SET qty = 11 WHERE sku = 'lwt-demo' IF qty = 10;
SELECT * FROM inventory;

UPDATE inventory SET qty = 99 WHERE sku = 'lwt-demo' IF qty = 10;
SELECT * FROM inventory;
```

**Deliverable:** Which `UPDATE` applied, and why? Relate to **compare-and-set** / Paxos.

---

## Lab D — Capstone checklist

Without running new commands, write a short answer for each:

1. Why is the cluster **masterless**?
2. What does **RF=3** plus **QUORUM** read+write imply about overlap?
3. Name two mechanisms that move data toward consistency **without** a client read.

---

## Next

End of the **architecture** sequence. Follow-on: **data modeling** track starting at [DM 01 — Intro and paradigm](../data-modeling/01-intro-and-paradigm.md). See the [course overview](../README.md) to revisit any module.

