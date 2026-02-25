"""Repository for Playground Traces."""

from prism.server.models.playground import PlaygroundTrace
from sqlalchemy.orm import Session


class PlaygroundRepository:
  """Repository for Playground Traces."""

  def __init__(self, session: Session):
    self._session = session

  def save_trace(self, trace: PlaygroundTrace) -> PlaygroundTrace:
    """Saves a PlaygroundTrace."""
    self._session.add(trace)
    self._session.commit()
    self._session.refresh(trace)
    return trace

  def get_trace(self, trace_id: int) -> PlaygroundTrace | None:
    """Gets a PlaygroundTrace by ID."""
    return self._session.get(PlaygroundTrace, trace_id)
