from ohanna_vision.domain import NodeState
from ohanna_vision.projection import InfrastructureReducer


def test_infrastructure_reducer_accepts_empty_collection() -> None:
    infrastructure = InfrastructureReducer().reduce([])

    assert infrastructure.nodes == ()


def test_infrastructure_reducer_sorts_nodes() -> None:
    infrastructure = InfrastructureReducer().reduce(
        [
            NodeState(node_id="zwave-01", services=()),
            NodeState(node_id="green-01", services=()),
        ]
    )

    assert tuple(node.node_id for node in infrastructure.nodes) == (
        "green-01",
        "zwave-01",
    )
