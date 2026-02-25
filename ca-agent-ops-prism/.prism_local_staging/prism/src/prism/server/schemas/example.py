"""Pydantic schemas for the Example entity."""

import datetime

from prism.server.schemas.assertion import Assertion
import pydantic


class ExampleCreate(pydantic.BaseModel):
  """Schema for creating a new Example."""

  test_suite_id: int
  logical_id: str | None = None  # Optional, can be auto-generated
  question: str = pydantic.Field(..., description="The input question")
  asserts: list[Assertion] = pydantic.Field(
      default_factory=list, description="List of assert definitions"
  )


class ExampleUpdate(pydantic.BaseModel):
  """Schema for updating an existing Example."""

  question: str | None = None
  asserts: list[Assertion] | None = None


class Example(ExampleCreate):
  """Schema for a persisted Example."""

  id: int
  logical_id: str
  created_at: datetime.datetime
  modified_at: datetime.datetime | None = None
  is_archived: bool = False

  model_config = pydantic.ConfigDict(from_attributes=True)
