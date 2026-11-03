# Architecture (long form)

These notes were folded into [session 1](../sessions/01-common-foundation.md) and [session 2](../sessions/02-consistency-topology-storage.md). Read the session. This folder is the earlier split of that same text. DSE is explained in session 1. There is no DSE lab.

| # | File | Focus |
|---|------|--------|
| 01 | [01-architecture-and-deployment.md](01-architecture-and-deployment.md) | When to use Cassandra; OSS vs HCD vs Astra DB |
| 02 | [02-lab-environment.md](02-lab-environment.md) | Cluster, `lab_ks`, `events` table |
| 03 | [03-masterless-peers-and-placement.md](03-masterless-peers-and-placement.md) | Masterless topology, token ring, `getendpoints` |
| 04 | [04-cap-and-tunable-consistency.md](04-cap-and-tunable-consistency.md) | CAP, consistency levels, tracing |
| 05 | [05-gossip-and-topology.md](05-gossip-and-topology.md) | Gossip, snitches, DC/rack |
| 06 | [06-storage-engine-write-through-read.md](06-storage-engine-write-through-read.md) | LSM, SSTables, reads, compaction, tombstones |
| 07 | [07-self-healing-lwt-and-summary.md](07-self-healing-lwt-and-summary.md) | Hints, repair, LWT |

The course continues at [session 2](../sessions/02-consistency-topology-storage.md), then [session 3](../sessions/03-query-driven-design.md). Do not start `data-modeling/` from here.
