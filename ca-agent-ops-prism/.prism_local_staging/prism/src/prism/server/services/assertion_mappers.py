"""Utilities for mapping between Assertion Schemas and Models.

This module provides reusable functions to convert between Pydantic schemas
(used in API/Engine) and SQLAlchemy models (used in DB).
"""

from prism.common.schemas.assertion import Assertion as AssertionSchema
from prism.server.models.assertion import Assertion as AssertionModel
from prism.server.models.assertion import AssertionSnapshot as AssertionSnapshotModel
from prism.server.models.assertion import SuggestedAssertion as SuggestedAssertionModel
from pydantic import TypeAdapter


def schema_to_model(schema: AssertionSchema) -> AssertionModel:
  """Converts a Pydantic Assertion schema to a SQLAlchemy Assertion model.

  Args:
      schema: The Pydantic Assertion schema.

  Returns:
      A SQLAlchemy Assertion model.
  """
  data = schema.model_dump()
  # Extract explicit fields for the model
  assertion_type = data.pop("type")
  weight = data.pop("weight", 1.0)
  # The rest are params
  params = data

  return AssertionModel(type=assertion_type, weight=weight, params=params)


def model_to_schema(model: AssertionModel) -> AssertionSchema:
  """Converts a SQLAlchemy Assertion model to a Pydantic Assertion schema.

  Args:
      model: The SQLAlchemy Assertion model.

  Returns:
      A Pydantic Assertion schema.
  """
  data = model.params.copy()
  data["type"] = model.type
  data["weight"] = model.weight
  data["id"] = model.id
  # Include original_assertion_id if it exists (e.g. for Snapshots using this mapper)
  if hasattr(model, "original_assertion_id"):
    data["original_assertion_id"] = model.original_assertion_id
  return TypeAdapter(AssertionSchema).validate_python(data)


def snapshot_model_to_schema(
    model: AssertionSnapshotModel,
) -> AssertionSchema:
  """Converts a SQLAlchemy AssertionSnapshot model to a Pydantic schema."""
  data = model.params.copy()
  data["type"] = model.type
  data["weight"] = model.weight
  data["id"] = model.id
  data["original_assertion_id"] = model.original_assertion_id
  return TypeAdapter(AssertionSchema).validate_python(data)


def schema_to_suggested_model(
    schema: AssertionSchema, trial_id: int
) -> SuggestedAssertionModel:
  """Converts a Pydantic Assertion schema to a SuggestedAssertion model.

  Args:
      schema: The Pydantic Assertion schema.
      trial_id: The ID of the trial this suggestion belongs to.

  Returns:
      A SQLAlchemy SuggestedAssertion model.
  """
  data = schema.model_dump()
  # Extract explicit fields for the model
  assertion_type = data.pop("type")
  weight = data.pop("weight", 1.0)
  reasoning = data.pop("reasoning", None)
  # Exclude 'id' from params if present
  data.pop("id", None)
  # The rest are params
  params = data

  return SuggestedAssertionModel(
      trial_id=trial_id,
      type=assertion_type,
      weight=weight,
      params=params,
      reasoning=reasoning,
  )
