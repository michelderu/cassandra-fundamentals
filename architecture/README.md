# Architecture (cluster labs)

The timed class for this material is **Phase 1** in [`sessions/`](../sessions/README.md): session 1 (architecture, DSE explained, placement) and session 2 (consistency, gossip, storage, a failure lab). Modules **01–07** are the longer reference on the same Docker Compose cluster: topology, replication and consistency, gossip, the storage engine, and repairs / lightweight transactions. DSE is explained in [01](01-architecture-and-deployment.md). There is no DSE lab.

| # | File | Focus |
|---|------|--------|
| 01 | [01-architecture-and-deployment.md](01-architecture-and-deployment.md) | When to use Cassandra; OSS vs HCD vs Astra DB |
| 02 | [02-lab-environment.md](02-lab-environment.md) | Cluster, `lab_ks`, `events` table |
| 03 | [03-masterless-peers-and-placement.md](03-masterless-peers-and-placement.md) | Masterless topology, token ring, `getendpoints` |
| 04 | [04-cap-and-tunable-consistency.md](04-cap-and-tunable-consistency.md) | CAP, consistency levels, tracing |
| 05 | [05-gossip-and-topology.md](05-gossip-and-topology.md) | Gossip, snitches, DC/rack |
| 06 | [06-storage-engine-write-through-read.md](06-storage-engine-write-through-read.md) | LSM, SSTables, reads, compaction, tombstones |
| 07 | [07-self-healing-lwt-and-summary.md](07-self-healing-lwt-and-summary.md) | Hints, repair, LWT |

**Next:** [Data modeling](../data-modeling/README.md) — query-first schema design (01–07).

Parent index: [../README.md](../README.md).
