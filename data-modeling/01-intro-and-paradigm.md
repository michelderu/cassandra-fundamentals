# 01 — The architect’s blueprint: relational vs Cassandra

Topics: **why query-first design**, **relational workflow vs Cassandra workflow**, **the golden rule**, **lab: cluster + cqlsh**.

**Terms:**

| Term | Meaning |
|------|---------|
| **Partition key** | First part of the `PRIMARY KEY`; decides how rows are grouped into **partitions** and hashed onto the ring. |
| **Clustering key(s)** | Columns after the partition key; define **sort order** and row uniqueness **inside** one partition. |
| **Denormalization** | Storing the same logical information in more than one table so each **access pattern** can read without server-side joins. |

**Prerequisites:** Completing the **architecture** track through [07-self-healing-lwt-and-summary.md](../architecture/07-self-healing-lwt-and-summary.md) is recommended. Hands-on work uses the **Docker Compose** lab cluster ([`docker-compose.yml`](../docker-compose.yml), [data-modeling README](README.md)). Create `lab_ks` / `events` per [architecture/02-lab-environment.md](../architecture/02-lab-environment.md) before module **02** onward (module **01** only needs a running cluster).

**Previous:** [07-self-healing-lwt-and-summary.md](../architecture/07-self-healing-lwt-and-summary.md). **Next:** [02-process-and-primary-key.md](02-process-and-primary-key.md).

---

## Blueprint: designing for scale

Cassandra’s **masterless**, **log-structured** architecture can deliver **high throughput** and **linear scale-out**—but only if the **data model** matches how the cluster physically stores and retrieves data (partitions on the ring, LSM writes, tunable consistency). This track is the **architect’s blueprint**: query-driven schemas, partitioning, and deliberate duplication.

---

## Database paradigm contrast: relational vs Cassandra

**Typical relational workflow:** identify **entities** → apply **normal forms** to reduce redundancy → create **tables** → add **indexes** → run **ad hoc SQL** with **JOINs**. The usual focus is **storage efficiency** and flexible querying; at very large scale, complex joins and central bottlenecks can become **scaling constraints**.

**Cassandra workflow:** **list access patterns** first → **choose partition keys** so each query hits a known partition (or a small bounded set) → **define clustering** for order inside the partition → often **one table per query pattern** at production scale. The focus is **partition-local access** and **read latency**; duplication is acceptable when it buys predictable performance.

![Database paradigm contrast: relational vs Cassandra](../assets/modeling-relational-vs-cassandra.png)

**Golden rule:** Design **one table** (or materialized path) **per query pattern** you need at **production scale**. If a pattern cannot be expressed as **known partition key + optional range on clustering**, you are still thinking in rows-and-joins—you likely need another table, a different key, or a different store.

---

## Lab — Cluster and cqlsh (Docker Compose)

**Goal:** Confirm the **same** Compose stack used in the architecture labs is up and you can run CQL.

1. From the **repository root**, start the cluster ([../README.md](../README.md#start-the-lab-cluster)): `docker compose up -d`.
2. Wait for **UN** on all nodes: `docker exec cassandra-1 nodetool status`.
3. Open **cqlsh**: `docker exec -it cassandra-1 cqlsh cassandra-1 9042`.
4. Run:

   ```sql
   SELECT cluster_name, release_version FROM system.local;
   ```

**Deliverable:** Note `cluster_name` (expect `training-lab` from Compose) and that you have a prompt. Before module **02**, complete **Lab B** in [architecture/02-lab-environment.md](../architecture/02-lab-environment.md) to create `lab_ks` and `events`.

---

## Next

[02-process-and-primary-key.md](02-process-and-primary-key.md) — the modeling process and primary key structure.
