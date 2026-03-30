# 05 — Gossip and topology awareness

Topics: **gossip protocol**, **snitches**, **multi-DC ideas** (this lab stays **single DC**).

**Previous:** [04-cap-and-tunable-consistency.md](04-cap-and-tunable-consistency.md). **Next:** [06-storage-engine-write-through-read.md](06-storage-engine-write-through-read.md).

---

## 6. Gossip

**What it means:** **Gossip** is the epidemic protocol nodes use to share **membership**, **health**, **load**, and **schema/token map** metadata. Each round, a node exchanges state with a **few** peers; updates spread quickly across large clusters.

**Failure detection:** **Accrual** (e.g. phi-accrual) failure detection is **probabilistic**, reducing false “dead” decisions under **network jitter**.

![Gossip and failure detection](../assets/image-c1a5cd48-098a-43e4-9700-3eb682083291.png)

**Takeaways:** Gossip is **control-plane** metadata, not the application data path; it supports routing and repair decisions.

---

## 7. Topology aware

**What it means:** Production clusters span **racks** and **data centers**. A **snitch** maps nodes to **rack/DC** so replication can avoid placing all copies on one failure domain.

**Multi-DC:** Replication across WAN is often **asynchronous**; **NetworkTopologyStrategy** sets **per-DC replication factors**. Clients often use **LOCAL_** consistency in their home DC.

This Compose lab uses **one DC** and `SimpleStrategy` for simplicity; production multi-DC would switch strategy + snitch.

![Topology and multi-DC](../assets/image-8f5cb0e9-7bbe-4042-96d3-89ea5b9b5167.png)

**Takeaways:** Match **snitch + replication strategy** to real layout; this module’s labs only **peek** at endpoint metadata.

---

## Lab A — Describe cluster and gossip peers

On the **host**:

```bash
docker exec cassandra-1 nodetool describecluster
docker exec cassandra-1 nodetool gossipinfo | head -40
```

**Deliverable:** From `describecluster`, note **name** and **partitioner**; from `gossipinfo`, confirm you see entries for peer IPs/hostnames.

---

## Lab B — Failure detector (read-only)

```bash
docker exec cassandra-1 nodetool failuredetector
```

**Deliverable:** One sentence linking **phi** / thresholds to **transient network** behavior (from the theory section).

---

## Lab C — Snitch and endpoint types (conceptual)

```bash
docker exec cassandra-1 nodetool describecluster
docker exec cassandra-1 cat /etc/cassandra/cassandra.yaml | grep -E '^endpoint_snitch|^# endpoint'
```

**Deliverable:** Which snitch is configured? Why is **SimpleSnitch** enough for this single-site lab but not for multi-DC production?

---

## Next

[06-storage-engine-write-through-read.md](06-storage-engine-write-through-read.md)
