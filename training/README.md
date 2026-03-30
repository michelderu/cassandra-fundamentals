# Training modules

Work through these in order. Each file includes **labs** you run against the Docker Compose cluster.

| # | Module | Topics |
|---|--------|--------|
| [01](01-lab-environment.md) | Lab environment | Setup, verification, cqlsh, keyspace |
| [02](02-masterless-peers-and-placement.md) | Masterless, peers, data placing | Cluster topology, hashing, placement |
| [03](03-cap-and-tunable-consistency.md) | CAP, tunable consistency | Availability vs consistency, CL |
| [04](04-gossip-and-topology.md) | Gossip, topology awareness | Gossip, snitches, DC/rack concepts |
| [05](05-storage-engine-write-through-read.md) | Write path, flush, read path, compaction, tombstones | LSM, SSTables, reads, compaction, deletes |
| [06](06-self-healing-lwt-and-summary.md) | Hints/repair, LWT, summary | Hints, repair, Paxos, recap |
