"""Shared mixins for SQLAlchemy models."""

import datetime

import sqlalchemy
from sqlalchemy import orm


class BaseMixin:
  """Mixin class that adds standard timestamp and archive fields."""

  created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
      sqlalchemy.DateTime(timezone=True),
      server_default=sqlalchemy.func.now(),
      nullable=False,
  )
  modified_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
      sqlalchemy.DateTime(timezone=True),
      server_default=sqlalchemy.func.now(),
      onupdate=sqlalchemy.func.now(),
      nullable=False,
  )
  is_archived: orm.Mapped[bool] = orm.mapped_column(
      sqlalchemy.Boolean, default=False, nullable=False
  )
