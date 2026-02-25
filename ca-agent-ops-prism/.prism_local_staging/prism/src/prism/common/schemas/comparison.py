"""Pydantic schemas for Run Comparison."""

import enum
from prism.common.schemas.execution import RunSchema
from prism.common.schemas.execution import Trial
import pydantic


class ComparisonStatus(str, enum.Enum):
  """Status of a comparison case."""

  REGRESSION = "REGRESSION"
  IMPROVED = "IMPROVED"
  STABLE = "STABLE"
  NEW = "NEW"  # Only in challenger
  REMOVED = "REMOVED"  # Only in base
  ERROR = "ERROR"  # Error in challenger (maybe base was success)


class ComparisonCase(pydantic.BaseModel):
  """A single case comparison (Row in the UI)."""

  logical_id: str
  question: str

  # Trials (Optional because might be NEW or REMOVED)
  base_trial: Trial | None = None
  challenger_trial: Trial | None = None

  # Deltas
  score_delta: float | None = None
  duration_delta: int | None = None

  status: ComparisonStatus

  model_config = pydantic.ConfigDict(from_attributes=True)


class ComparisonDelta(pydantic.BaseModel):
  """Overall delta summary."""

  accuracy_delta: float = 0.0
  duration_delta_avg: float = 0.0
  regressions_count: int = 0
  improvements_count: int = 0
  same_count: int = 0
  errors_count: int = 0


class RunComparisonMetadata(pydantic.BaseModel):
  """Metadata for the comparison report."""

  base_run_id: int
  challenger_run_id: int
  total_cases: int


class RunComparison(pydantic.BaseModel):
  """Full comparison report object."""

  base_run: RunSchema
  challenger_run: RunSchema
  metadata: RunComparisonMetadata
  delta: ComparisonDelta
  cases: list[ComparisonCase]
