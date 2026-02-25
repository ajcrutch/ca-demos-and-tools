"""SQLAlchemy model for the Test Suite entity."""

from prism.server.db import Base
from prism.server.models.base_mixin import BaseMixin
import sqlalchemy
from sqlalchemy import orm


class BaseSuite:
  """Mixin for Suite fields shared between Live and Snapshot models."""

  name: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String, nullable=False)
  description: orm.Mapped[str | None] = orm.mapped_column(
      sqlalchemy.Text, nullable=True
  )
  tags: orm.Mapped[dict[str, str]] = orm.mapped_column(
      sqlalchemy.JSON, default=dict, nullable=False
  )


class TestSuite(Base, BaseMixin, BaseSuite):
  """A reusable collection of tests."""

  __tablename__ = "test_suites"

  id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
