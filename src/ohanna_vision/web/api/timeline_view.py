"""View models dedicated to timeline rendering."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ohanna_vision.web.api.timeline_schemas import (
    TimelinePeriodResponse,
)


class TimelineNodeView(BaseModel):
    """Timeline rendered for one infrastructure node."""

    model_config = ConfigDict(
        frozen=True,
    )

    node_id: str

    node_name: str

    periods: tuple[
        TimelinePeriodResponse,
        ...
    ]


class TimelineViewResponse(BaseModel):
    """Frontend-oriented timeline view."""

    model_config = ConfigDict(
        frozen=True,
    )

    started_at: datetime

    ended_at: datetime

    nodes: tuple[
        TimelineNodeView,
        ...
    ]