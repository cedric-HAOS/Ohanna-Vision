"""Inject demonstration observations into Ohanna-Vision."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "http://127.0.0.1:8000"

STATUSES = (
    "healthy",
    "healthy",
    "degraded",
    "healthy",
    "unhealthy",
    "healthy",
)

CAPABILITIES = (
    "network.reachable",
    "dns.resolve",
    "service.available",
    "network.latency",
)

SERVICES = (
    "network-primary",
    "dns-primary",
    "supervision-primary",
)


def fetch_json(url: str) -> Any:
    """Fetch a JSON resource."""
    request = Request(
        url=url,
        headers={
            "Accept": "application/json",
        },
        method="GET",
    )

    with urlopen(request, timeout=10) as response:
        return json.load(response)


def post_json(url: str, payload: dict[str, Any]) -> int:
    """Post a JSON resource and return its HTTP status."""
    body = json.dumps(payload).encode("utf-8")

    request = Request(
        url=url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        response.read()
        return response.status


def topology_node_ids(topology: dict[str, Any]) -> list[str]:
    """Return unique node identifiers declared in the topology."""
    node_ids: list[str] = []

    for device in topology.get("devices", []):
        node_id = device.get("node_id")

        if node_id and node_id not in node_ids:
            node_ids.append(node_id)

    return node_ids


def build_observation(
    *,
    node_id: str,
    index: int,
    observed_at: datetime,
) -> dict[str, Any]:
    """Build one demonstration observation."""
    status = STATUSES[index % len(STATUSES)]
    capability_id = CAPABILITIES[index % len(CAPABILITIES)]
    service_id = SERVICES[index % len(SERVICES)]

    latency_ms = 5.0 + index * 7.5

    if status == "degraded":
        latency_ms += 100.0

    if status == "unhealthy":
        latency_ms += 500.0

    return {
        "capability_id": capability_id,
        "service_id": service_id,
        "node_id": node_id,
        "status": status,
        "observed_at": observed_at.isoformat(),
        "latency_ms": latency_ms,
        "metadata": {
            "source": "demo-observation-injector",
            "sequence": index,
        },
    }


def inject_observations(
    *,
    base_url: str,
    observations_per_node: int,
) -> None:
    """Inject demonstration observations."""
    topology_url = f"{base_url}/api/topology"
    observations_url = f"{base_url}/api/observations"

    topology = fetch_json(topology_url)
    node_ids = topology_node_ids(topology)

    if not node_ids:
        raise RuntimeError(
            "La topologie ne contient aucun équipement avec un node_id.",
        )

    now = datetime.now(UTC)
    injected = 0

    print("Injection d’observations de démonstration")
    print("----------------------------------------")
    print(f"Serveur : {base_url}")
    print(f"Nœuds   : {len(node_ids)}")
    print()

    sequence = 0

    for node_index, node_id in enumerate(node_ids):
        for observation_index in range(observations_per_node):
            age_minutes = observation_index * 45 + node_index * 4

            observed_at = now - timedelta(
                minutes=age_minutes,
            )

            observation = build_observation(
                node_id=node_id,
                index=sequence,
                observed_at=observed_at,
            )

            status = post_json(
                observations_url,
                observation,
            )

            print(
                f"[{status}] "
                f"{node_id:<20} "
                f"{observation['status']:<10} "
                f"{observation['capability_id']}",
            )

            sequence += 1
            injected += 1

    print()
    print(f"{injected} observations injectées.")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=("Injecter des observations de démonstration dans Ohanna-Vision."),
    )

    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=(f"Adresse d’Ohanna-Vision (défaut : {DEFAULT_BASE_URL})."),
    )

    parser.add_argument(
        "--observations-per-node",
        type=int,
        default=5,
        help="Nombre d’observations injectées par nœud.",
    )

    return parser.parse_args()


def main() -> None:
    """Run the demonstration injector."""
    arguments = parse_arguments()

    if arguments.observations_per_node <= 0:
        raise ValueError(
            "--observations-per-node doit être supérieur à zéro.",
        )

    try:
        inject_observations(
            base_url=arguments.base_url.rstrip("/"),
            observations_per_node=(arguments.observations_per_node),
        )
    except HTTPError as error:
        detail = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise SystemExit(
            f"Erreur HTTP {error.code} : {detail}",
        ) from error
    except URLError as error:
        raise SystemExit(
            f"Impossible de joindre Ohanna-Vision : {error.reason}",
        ) from error


if __name__ == "__main__":
    main()
