from datetime import UTC, datetime

from ohanna_vision.web.api import (
    TimelineNodeView,
    TimelinePeriodResponse,
    TimelineViewResponse,
)


def make_period():
    return TimelinePeriodResponse(
        status="healthy",
        started_at=datetime(
            2026,
            7,
            15,
            8,
            tzinfo=UTC,
        ),
        ended_at=None,
        duration_seconds=None,
        is_open=True,
    )

def test_timeline_node_view_is_immutable():
    period = make_period()

    node = TimelineNodeView(
        node_id="infra-01",
        node_name="Infrastructure",
        periods=(period,),
    )

    assert node.node_id == "infra-01"

    assert len(node.periods) == 1

def test_timeline_view_contains_nodes():
    period = make_period()

    node = TimelineNodeView(
        node_id="infra-01",
        node_name="Infrastructure",
        periods=(period,),
    )

    view = TimelineViewResponse(
        started_at=datetime(
            2026,
            7,
            15,
            8,
            tzinfo=UTC,
        ),
        ended_at=datetime(
            2026,
            7,
            15,
            9,
            tzinfo=UTC,
        ),
        nodes=(node,),
    )

    assert len(view.nodes) == 1

def test_timeline_view_json_contract():
    period = make_period()

    node = TimelineNodeView(
        node_id="infra-01",
        node_name="Infrastructure",
        periods=(period,),
    )

    view = TimelineViewResponse(
        started_at=datetime(
            2026,
            7,
            15,
            8,
            tzinfo=UTC,
        ),
        ended_at=datetime(
            2026,
            7,
            15,
            9,
            tzinfo=UTC,
        ),
        nodes=(node,),
    )

    payload = view.model_dump(
        mode="json",
    )

    assert payload["nodes"][0]["node_id"] == "infra-01"

    assert payload["nodes"][0]["node_name"] == "Infrastructure"