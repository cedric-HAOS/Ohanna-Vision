"""REST response returned after observation ingestion."""

from pydantic import BaseModel, ConfigDict


class ObservationIngestionResponse(BaseModel):
    """Response confirming that an observation was accepted."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    message: str