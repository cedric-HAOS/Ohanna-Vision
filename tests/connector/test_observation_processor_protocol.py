"""Tests for ObservationProcessorProtocol."""

from ohanna_vision.connector import ObservationProcessorProtocol


def test_observation_processor_protocol_is_defined() -> None:
    assert ObservationProcessorProtocol.__name__ == (
        "ObservationProcessorProtocol"
    )


def test_observation_processor_protocol_declares_process() -> None:
    assert hasattr(ObservationProcessorProtocol, "process")