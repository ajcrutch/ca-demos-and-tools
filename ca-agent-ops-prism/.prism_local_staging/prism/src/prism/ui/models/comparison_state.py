"""UI State models for Run Comparison."""

import pydantic


class RunComparisonUIState(pydantic.BaseModel):
  """State for the Run Comparison page (URL-driven)."""

  suite_id: int | None = None
  base_run_id: int | None = None
  challenger_run_id: int | None = None

  # Filters
  filter_status: str | None = None  # None/All, REGRESSION, IMPROVED, ERROR
