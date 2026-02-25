"""Pydantic schemas for the Example entity."""

import datetime

from prism.common.schemas.assertion import Assertion
from prism.common.schemas.assertion import AssertionRequest
import pydantic


class ExampleCreate(pydantic.BaseModel):
  """Schema for creating a new Example."""

  test_suite_id: int
  logical_id: str | None = None  # Optional, can be auto-generated
  question: str = pydantic.Field(..., description="The input question")
  asserts: list[AssertionRequest] = pydantic.Field(
      default_factory=list, description="List of assert definitions"
  )


class ExampleUpdate(pydantic.BaseModel):
  """Schema for updating an existing Example."""

  question: str | None = None
  asserts: list[AssertionRequest] | None = None


class Example(ExampleCreate):
  """Schema for a persisted Example."""

  id: int
  logical_id: str
  asserts: list[Assertion] = pydantic.Field(default_factory=list)
  created_at: datetime.datetime
  modified_at: datetime.datetime | None = None
  is_archived: bool = False

  model_config = pydantic.ConfigDict(from_attributes=True)


class TestCaseInput(pydantic.BaseModel):
  """Schema for bulk import of test cases with assertions."""

  __test__ = False

  question: str
  assertions: list[AssertionRequest] = pydantic.Field(default_factory=list)
