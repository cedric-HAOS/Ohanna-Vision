"""Tests for topology layouts."""

import math

import pytest

from ohana_vision.topology import (
    TopologyLayout,
    TopologyLayoutKind,
    TopologyPosition,
)


def test_topology_position_stores_coordinates() -> None:
    """A topology position must expose its canvas coordinates."""
    position = TopologyPosition(
        x=250,
        y=400,
    )

    assert position.x == 250
    assert position.y == 400
    assert position.layer == 0
    assert position.pinned is False


def test_topology_position_can_be_pinned() -> None:
    """A topology position may be protected from automatic moves."""
    position = TopologyPosition(
        x=500,
        y=100,
        layer=2,
        pinned=True,
    )

    assert position.layer == 2
    assert position.pinned is True


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("x", math.inf, "x must be finite"),
        ("x", -math.inf, "x must be finite"),
        ("x", math.nan, "x must be finite"),
        ("y", math.inf, "y must be finite"),
        ("y", -math.inf, "y must be finite"),
        ("y", math.nan, "y must be finite"),
    ],
)
def test_topology_position_rejects_non_finite_coordinates(
    field_name: str,
    value: float,
    message: str,
) -> None:
    """Topology coordinates must contain finite numeric values."""
    arguments = {
        "x": 100.0,
        "y": 200.0,
    }
    arguments[field_name] = value

    with pytest.raises(ValueError, match=message):
        TopologyPosition(**arguments)


def test_topology_position_is_immutable() -> None:
    """A topology position must remain immutable."""
    position = TopologyPosition(
        x=250,
        y=400,
    )

    with pytest.raises(AttributeError):
        position.x = 300  # type: ignore[misc]


def test_topology_layout_stores_identity() -> None:
    """A topology layout must expose its identity and purpose."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
    )

    assert layout.layout_id == "physical-main"
    assert layout.label == "Carte physique principale"
    assert layout.kind is TopologyLayoutKind.PHYSICAL


def test_topology_layout_uses_default_canvas_dimensions() -> None:
    """A topology layout must provide useful default dimensions."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
    )

    assert layout.canvas_width == 1600
    assert layout.canvas_height == 900


def test_topology_layout_stores_device_positions() -> None:
    """A topology layout must associate positions with devices."""
    internet_position = TopologyPosition(
        x=800,
        y=80,
        pinned=True,
    )
    freebox_position = TopologyPosition(
        x=800,
        y=220,
    )

    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        positions={
            "internet": internet_position,
            "freebox": freebox_position,
        },
    )

    assert layout.position_for("internet") == internet_position
    assert layout.position_for("freebox") == freebox_position


def test_topology_layout_normalizes_device_identifiers() -> None:
    """Layout device identifiers must be normalized."""
    position = TopologyPosition(
        x=800,
        y=80,
    )

    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        positions={
            "  internet  ": position,
        },
    )

    assert layout.position_for("internet") == position
    assert layout.position_for("  internet  ") == position


def test_topology_layout_reports_contained_devices() -> None:
    """A topology layout must report positioned devices."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        positions={
            "internet": TopologyPosition(
                x=800,
                y=80,
            ),
        },
    )

    assert layout.contains_device("internet") is True
    assert layout.contains_device("freebox") is False
    assert layout.contains_device("   ") is False


def test_topology_layout_returns_none_for_unknown_device() -> None:
    """An unknown device must not have a layout position."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
    )

    assert layout.position_for("unknown") is None


def test_topology_layout_normalizes_identity() -> None:
    """Topology layout identity values must be normalized."""
    layout = TopologyLayout(
        layout_id="  physical-main  ",
        label="  Carte physique principale  ",
        kind=TopologyLayoutKind.PHYSICAL,
    )

    assert layout.layout_id == "physical-main"
    assert layout.label == "Carte physique principale"


def test_topology_layout_rejects_empty_layout_id() -> None:
    """A topology layout must have a non-empty identifier."""
    with pytest.raises(
        ValueError,
        match="layout_id must not be empty",
    ):
        TopologyLayout(
            layout_id="   ",
            label="Carte physique principale",
            kind=TopologyLayoutKind.PHYSICAL,
        )


def test_topology_layout_rejects_empty_label() -> None:
    """A topology layout must have a non-empty label."""
    with pytest.raises(
        ValueError,
        match="label must not be empty",
    ):
        TopologyLayout(
            layout_id="physical-main",
            label="   ",
            kind=TopologyLayoutKind.PHYSICAL,
        )


def test_topology_layout_rejects_empty_position_device_id() -> None:
    """Every layout position must reference a device identifier."""
    with pytest.raises(
        ValueError,
        match="position device_id must not be empty",
    ):
        TopologyLayout(
            layout_id="physical-main",
            label="Carte physique principale",
            kind=TopologyLayoutKind.PHYSICAL,
            positions={
                "   ": TopologyPosition(
                    x=100,
                    y=200,
                ),
            },
        )


@pytest.mark.parametrize(
    "canvas_width",
    [
        0,
        -1,
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_topology_layout_rejects_invalid_canvas_width(
    canvas_width: float,
) -> None:
    """The layout canvas width must be finite and positive."""
    expected_message = (
        "canvas_width must be finite"
        if not math.isfinite(canvas_width)
        else "canvas_width must be greater than zero"
    )

    with pytest.raises(ValueError, match=expected_message):
        TopologyLayout(
            layout_id="physical-main",
            label="Carte physique principale",
            kind=TopologyLayoutKind.PHYSICAL,
            canvas_width=canvas_width,
        )


@pytest.mark.parametrize(
    "canvas_height",
    [
        0,
        -1,
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_topology_layout_rejects_invalid_canvas_height(
    canvas_height: float,
) -> None:
    """The layout canvas height must be finite and positive."""
    expected_message = (
        "canvas_height must be finite"
        if not math.isfinite(canvas_height)
        else "canvas_height must be greater than zero"
    )

    with pytest.raises(ValueError, match=expected_message):
        TopologyLayout(
            layout_id="physical-main",
            label="Carte physique principale",
            kind=TopologyLayoutKind.PHYSICAL,
            canvas_height=canvas_height,
        )


def test_topology_layout_copies_positions() -> None:
    """External position changes must not mutate the layout."""
    positions = {
        "internet": TopologyPosition(
            x=800,
            y=80,
        ),
    }

    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        positions=positions,
    )

    positions["freebox"] = TopologyPosition(
        x=800,
        y=220,
    )

    assert layout.contains_device("internet") is True
    assert layout.contains_device("freebox") is False


def test_topology_layout_positions_are_immutable() -> None:
    """Layout positions must not be mutable through the layout."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        positions={
            "internet": TopologyPosition(
                x=800,
                y=80,
            ),
        },
    )

    with pytest.raises(TypeError):
        layout.positions["freebox"] = TopologyPosition(  # type: ignore[index]
            x=800,
            y=220,
        )


def test_topology_layout_copies_metadata() -> None:
    """External metadata changes must not mutate the layout."""
    metadata: dict[str, object] = {
        "description": "Main infrastructure map",
    }

    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        metadata=metadata,
    )

    metadata["description"] = "Changed"

    assert layout.metadata["description"] == "Main infrastructure map"


def test_topology_layout_metadata_is_immutable() -> None:
    """Layout metadata must not be mutable."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        metadata={
            "description": "Main infrastructure map",
        },
    )

    with pytest.raises(TypeError):
        layout.metadata["description"] = "Changed"  # type: ignore[index]


def test_topology_layout_is_immutable() -> None:
    """A topology layout must remain immutable."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
    )

    with pytest.raises(AttributeError):
        layout.label = "Other layout"  # type: ignore[misc]


def test_topology_layout_metadata_is_deeply_immutable() -> None:
    """Nested topology layout metadata must remain immutable."""
    metadata = {
        "viewport": {
            "zoom_levels": [
                0.5,
                1.0,
                2.0,
            ],
        },
    }

    layout = TopologyLayout(
        layout_id="physical-main",
        label="Carte physique principale",
        kind=TopologyLayoutKind.PHYSICAL,
        metadata=metadata,
    )

    metadata["viewport"]["zoom_levels"].append(4.0)

    viewport = layout.metadata["viewport"]

    assert viewport["zoom_levels"] == (  # type: ignore[index]
        0.5,
        1.0,
        2.0,
    )
