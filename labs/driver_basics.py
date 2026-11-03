#!/usr/bin/env python3
"""Session 4 — token-aware driver, prepared statements, LOCAL_QUORUM.

Against the Compose cluster (cassandra-1 on localhost:9042).
The same policies apply when contact points are DSE nodes; this file
does not connect to DSE.

  pip install cassandra-driver
  python labs/driver_basics.py
"""

import uuid
from datetime import datetime, timezone

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.protocol import InvalidRequest
from cassandra.query import SimpleStatement

CONTACT_POINTS = ["127.0.0.1"]
PORT = 9042
LOCAL_DC = "datacenter1"
KEYSPACE = "lab_ks"


def main() -> None:
    cluster = Cluster(
        CONTACT_POINTS,
        port=PORT,
        load_balancing_policy=TokenAwarePolicy(
            DCAwareRoundRobinPolicy(local_dc=LOCAL_DC)
        ),
    )
    try:
        session = cluster.connect(KEYSPACE)
    except NoHostAvailable as exc:
        cluster.shutdown()
        raise SystemExit(
            f"Could not reach {CONTACT_POINTS[0]}:{PORT}. "
            "Start the stack with: docker compose up -d\n"
            f"{exc}"
        ) from exc
    except InvalidRequest as exc:
        cluster.shutdown()
        raise SystemExit(
            f"Reached the cluster, but keyspace {KEYSPACE} is missing or not usable. "
            "Create it in session 1.\n"
            f"{exc}"
        ) from exc

    # Drivers page large results. A wide partition should not arrive in one response.
    session.default_fetch_size = 100

    insert = session.prepare(
        "INSERT INTO events (user_id, event_time, payload) VALUES (?, ?, ?)"
    )
    insert.consistency_level = ConsistencyLevel.LOCAL_QUORUM

    select = session.prepare(
        "SELECT payload FROM events WHERE user_id = ? LIMIT 5"
    )
    select.consistency_level = ConsistencyLevel.LOCAL_QUORUM

    user_id = uuid.uuid4()
    session.execute(
        insert,
        (user_id, datetime.now(timezone.utc), "driver-lab"),
    )
    row = session.execute(select, (user_id,)).one()
    if row is None:
        raise SystemExit("Insert succeeded but the following read saw no row.")

    print(f"payload={row.payload}")
    print(f"consistency={select.consistency_level}")
    print(f"user_id={user_id}")

    # Show that a non-prepared statement is still explicit about consistency.
    ping = SimpleStatement(
        "SELECT release_version FROM system.local",
        consistency_level=ConsistencyLevel.LOCAL_ONE,
    )
    version = session.execute(ping).one()
    print(f"release_version={version.release_version}")

    cluster.shutdown()


if __name__ == "__main__":
    main()
