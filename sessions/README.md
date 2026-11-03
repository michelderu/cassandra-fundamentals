# Four sessions, two hours each

Labs run on the open-source Compose cluster. **DSE is explained in session 1 and referred to later. There is no DSE lab.**

| | Session | Phase | Audience | Outcome |
|---|---------|-------|----------|---------|
| 1 | [Common foundation](01-common-foundation.md) | 1 | Developers, platform engineers, SRE, support | Say what Cassandra is for, how DSE differs, and where a partition lives |
| 2 | [Consistency, topology, storage](02-consistency-topology-storage.md) | 1 | Same | Pick a consistency level, read a snitch, and explain a write, a read, and a node loss |
| 3 | [Query-driven design](03-query-driven-design.md) | 2 | Developers, architects, technical leads | Turn an access pattern into a primary key that stays bounded |
| 4 | [CQL, drivers, performance](04-cql-drivers-performance.md) | 2 | Same | Write CQL and driver calls that respect tombstones, TTL, and the anti-patterns |

## How to run the room

- Teach from the session file in front of you. The agenda is the clock.
- Labs sit **inside** the block they illustrate. Do not save them for a lab hour at the end.
- Each session names one cut if you are behind. Take that cut before you drop a lab that the next session needs.
- Reference modules ([`architecture/`](../architecture/README.md), [`data-modeling/`](../data-modeling/README.md)) hold extra labs (full repair, compaction stats, capstone repeats). They are not a fifth and sixth session.

## Cluster

Start and reset: [repository README](../README.md#start-the-lab-cluster). Session 1 creates `lab_ks`. Sessions 2–4 reuse it.

## What each phase deliberately leaves out

**Phase 1** does not design schemas, write a driver, or open OpsCenter. Support and SRE leave with the operational vocabulary; developers leave ready for Phase 2.

**Phase 2** does not operate gossip, repair, or multi-DC failover. It assumes session 1 and 2, and spends the time on schema, CQL, drivers, tombstones, and TTL.
