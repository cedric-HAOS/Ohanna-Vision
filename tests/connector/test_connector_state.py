"""Tests for ConnectorState."""

from ohanna_vision.connector import ConnectorState


def test_connector_state_contains_expected_values() -> None:
    assert ConnectorState.CREATED == "created"
    assert ConnectorState.READY == "ready"
    assert ConnectorState.RUNNING == "running"
    assert ConnectorState.ERROR == "error"


def test_connector_state_is_a_string_enum() -> None:
    assert isinstance(ConnectorState.CREATED, str)


def test_connector_state_can_be_created_from_string() -> None:
    assert ConnectorState("created") is ConnectorState.CREATED
    assert ConnectorState("ready") is ConnectorState.READY
    assert ConnectorState("running") is ConnectorState.RUNNING
    assert ConnectorState("error") is ConnectorState.ERROR


def test_connector_state_serializes_as_string() -> None:
    assert str(ConnectorState.CREATED) == "created"