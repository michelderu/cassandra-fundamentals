# 01 — Architecture and deployment options

This module frames **why** Cassandra-class databases exist and **how** common deployment choices differ.

**Terms used here:**

| Term | Meaning |
|------|---------|
| **CQL** | Cassandra Query Language (SQL-like interface to Cassandra). |
| **RF** | Replication factor (how many copies of each row’s partition exist in the cluster). |
| **CL** | Consistency level (how many of those replicas must acknowledge a read or write). |
| **DC** | Datacenter. |
| **OSS** | Open source. |
| **DBaaS** | Database-as-a-service (vendor runs the database for you). |

---

## When to use Cassandra (and what it is good at)

Cassandra is often used as an **operational data store (ODS)** for **live applications**: serving reads and writes with predictable latency at large scale, not as a primary **batch analytics** or **warehouse** layer (though data can be exported or integrated with analytics stacks).

**Strengths that match many production systems:**

| Need | How Cassandra-style systems address it |
|------|------------------------------------------|
| **Scale-out** | Add nodes to grow capacity and throughput horizontally; masterless design avoids a single write bottleneck. |
| **Low latency** | Tunable consistency (e.g. `LOCAL_QUORUM`, `ONE`) lets you trade strictness for response time where appropriate. |
| **High availability** | Replication across nodes/racks/DCs; no single master; survives node failures when **RF** and **CL** are chosen sensibly. |
| **Global distribution** | Multi-datacenter replication and **local** CLs (e.g. `LOCAL_QUORUM` = quorum **within the same DC** as the coordinator) keep traffic near the data that serves it. |

**When it may be a poor fit:**

- You need rich **ad-hoc joins** across arbitrary tables (Cassandra favors **query-first, denormalized** models).
- You require **default** single-system **strong serializable** transactions across many keys (Cassandra is **not** a traditional RDBMS; **LWT** = lightweight transactions, for narrow compare-and-set style cases only).
- Tiny datasets with no scale or HA requirements may be simpler on a single-node SQL store.

---

## Core architecture

The rest of this course dives into **Apache Cassandra** internals: partitions, replication, gossip, LSM storage, compaction, and repairs. That knowledge applies whether you run OSS Cassandra or a vendor distribution.

---

## Deployment options: Apache Cassandra, DataStax HCD, and Astra DB

All three are rooted in **Apache Cassandra compatibility** (CQL, drivers, partition-oriented modeling), but **who runs the infrastructure** and **where** it runs differ.

### Apache Cassandra (open source)

- **What it is:** Community **Apache Cassandra** releases that you install and operate yourself (bare metal, VMs, or your own Kubernetes).
- **Fit:** Teams that want **maximum control**, custom images, direct access to configs and upgrades, and no vendor lock-in for the binary.
- **Tradeoffs:** **You** own monitoring, backups, upgrades, security patching, and capacity planning.

### DataStax Hyper-Converged Database (HCD)

- **What it is:** DataStax’s **self-managed**, **Kubernetes-native** Cassandra-compatible platform for **on-premises** or **your** cloud accounts—aimed at enterprises that need data **in their** environment with vendor packaging and operational tooling (e.g. Mission Control in the DataStax ecosystem).
- **Fit:** Regulated industries, hybrid cloud, or policies that avoid fully vendor-hosted database planes while still wanting an enterprise distribution and support.
- **Tradeoffs:** **You** still operate the stack (unlike DBaaS); you gain supported packaging and features vs. raw OSS, with corresponding licensing/support considerations.

### DataStax Astra DB

- **What it is:** **Managed** Cassandra-compatible **database-as-a-service** on major public clouds: provisioning, patching, scaling, and SLAs are largely **DataStax-operated**.
- **Fit:** Teams optimizing for **time-to-value**, reduced DB operations headcount, and elastic scale without running Cassandra nodes themselves.
- **Tradeoffs:** Less control over low-level infrastructure and deployment topology than self-managed; pricing and cloud region choices follow the provider’s model.

### Summary comparison

| Dimension | OSS Cassandra | DataStax HCD (typical) | Astra DB (typical) |
|-----------|----------------|-------------------------|---------------------|
| **Operations** | Your team | Your team (supported stack) | Vendor-managed service |
| **Where it runs** | Your choice | Often on-prem / your cloud | DataStax-managed cloud |
| **Best when** | Full DIY control | Self-managed + enterprise support | Fastest path to managed CQL |

Check [DataStax documentation](https://docs.datastax.com/) for current HCD and Astra DB capabilities.

---

## Next

1. [02-lab-environment.md](02-lab-environment.md) — start the cluster; create `lab_ks` and `events`
2. [03-masterless-peers-and-placement.md](03-masterless-peers-and-placement.md) — token placement
3. [04-cap-and-tunable-consistency.md](04-cap-and-tunable-consistency.md) — CAP and consistency levels

Then continue with [05-gossip-and-topology.md](05-gossip-and-topology.md).
