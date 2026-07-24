"""REST response returned after infrastructure ingestion."""

from pydantic import BaseModel, ConfigDict


class InfrastructureIngestionResponse(BaseModel):
    """Confirm that an infrastructure snapshot was accepted."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    infrastructure_id: str
    node_count: int
    service_count: int
