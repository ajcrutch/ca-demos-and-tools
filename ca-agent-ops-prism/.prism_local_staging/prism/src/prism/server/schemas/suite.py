"""Pydantic schemas for the Test Suite entity."""

import datetime

import pydantic


class SuiteCreate(pydantic.BaseModel):
  """Schema for creating a new Test Suite."""

  name: str = pydantic.Field(..., description="Unique name of the suite")
  description: str | None = None
  tags: dict[str, str] = pydantic.Field(
      default_factory=dict, description="Metadata tags"
  )


class SuiteUpdate(pydantic.BaseModel):
  """Schema for updating an existing Test Suite."""

  name: str | None = None
  description: str | None = None
  tags: dict[str, str] | None = None


class Suite(SuiteCreate):
  """Schema for a persisted Test Suite."""

  id: int
  created_at: datetime.datetime
  modified_at: datetime.datetime | None = None
  is_archived: bool = False

  model_config = pydantic.ConfigDict(from_attributes=True)


class SuiteWithStats(pydantic.BaseModel):
  """Suite data with associated statistics."""

  suite: Suite
  question_count: int
  run_count: int
  assertion_coverage: float = 0.0
