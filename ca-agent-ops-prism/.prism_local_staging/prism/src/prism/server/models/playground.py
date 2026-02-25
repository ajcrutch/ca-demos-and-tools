"""SQLAlchemy model for Playground Traces."""

import datetime
from typing import Any

from prism.server.db import Base
from prism.server.models.base_mixin import BaseMixin
import sqlalchemy
from sqlalchemy import orm


class PlaygroundTrace(Base, BaseMixin):
  """Represents an ephemeral execution trace from the Question Playground."""

  __tablename__ = "playground_traces"

  id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
  created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
      sqlalchemy.DateTime,
      default=lambda: datetime.datetime.now(datetime.timezone.utc),
      nullable=False,
  )

  # Context
  question: orm.Mapped[str] = orm.mapped_column(sqlalchemy.Text, nullable=False)
  agent_id: orm.Mapped[int] = orm.mapped_column(
      sqlalchemy.ForeignKey("agents.id"), nullable=False
  )

  # Results
  trace_results: orm.Mapped[list[dict[str, Any]]] = orm.mapped_column(
      sqlalchemy.JSON, nullable=False
  )
  assertion_results: orm.Mapped[list[dict[str, Any]]] = orm.mapped_column(
      sqlalchemy.JSON, default=list, nullable=False
  )
  output_text: orm.Mapped[str | None] = orm.mapped_column(
      sqlalchemy.Text, nullable=True
  )
  error_message: orm.Mapped[str | None] = orm.mapped_column(
      sqlalchemy.Text, nullable=True
  )
  score: orm.Mapped[float | None] = orm.mapped_column(
      sqlalchemy.Float, nullable=True
  )
  duration_ms: orm.Mapped[int | None] = orm.mapped_column(
      sqlalchemy.Integer, nullable=True
  )
  passed: orm.Mapped[bool] = orm.mapped_column(
      sqlalchemy.Boolean, default=False, nullable=False
  )

  # Relationship
  agent = orm.relationship("Agent")
