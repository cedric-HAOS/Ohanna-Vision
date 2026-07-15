"""Tests for ConnectorResult."""

import pytest

from ohanna_vision.connector import ConnectorResult


def test_connector_result_stores_values() -> None:
    result = ConnectorResult(
        success=True,
        message="Observation accepted.",
    )

    assert result.success is True
    assert result.message == "Observation accepted."


def test_connector_result_can_represent_failure() -> None:
    result = ConnectorResult(
        success=False,
        message="Observation rejected.",
    )

    assert result.success is False
    assert result.message == "Observation rejected."


def test_connector_result_creates_success_result() -> None:
    result = ConnectorResult.succeeded()

    assert result.success is True
    assert result.message == "Observation received successfully."


def test_connector_result_creates_success_result_with_custom_message() -> None:
    result = ConnectorResult.succeeded("Observation processed.")

    assert result.success is True
    assert result.message == "Observation processed."


def test_connector_result_creates_failure_result() -> None:
    result = ConnectorResult.failed("Processor unavailable.")

    assert result.success is False
    assert result.message == "Processor unavailable."


def test_connector_result_is_immutable() -> None:
    result = ConnectorResult.succeeded()

    with pytest.raises(AttributeError):
        result.success = False
