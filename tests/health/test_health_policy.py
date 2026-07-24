from datetime import timedelta

import pytest

from ohana_vision.domain import Criticality
from ohana_vision.health import CapabilityHealthPolicy


def test_policy_is_created() -> None:
    policy = CapabilityHealthPolicy(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
        criticality=Criticality.CRITICAL,
        stale_after=timedelta(minutes=5),
    )

    assert policy.key == (
        "infra-01",
        "dns-primary",
        "dns.resolve",
    )
    assert policy.criticality is Criticality.CRITICAL


def test_policy_rejects_non_positive_stale_duration() -> None:
    with pytest.raises(
        ValueError,
        match="stale_after must be greater than zero",
    ):
        CapabilityHealthPolicy(
            node_id="infra-01",
            service_id="dns-primary",
            capability_id="dns.resolve",
            stale_after=timedelta(),
        )
