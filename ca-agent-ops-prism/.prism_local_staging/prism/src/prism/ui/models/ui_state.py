"""UI State Models."""

from typing import Any
import uuid

from prism.common.schemas import agent
from prism.common.schemas import execution
import pydantic


class AgentCreateForm(pydantic.BaseModel):
  """Form data for creating a new agent."""

  project_id: str
  location: str
  agent_resource_id: str
  name: str


class AssertItem(pydantic.BaseModel):
  """Represents a single assert in the UI builder."""

  id: int | None = None
  type: str
  params: dict[str, Any] | int | str | float | None = None

  model_config = pydantic.ConfigDict(extra="allow")


class TestCaseState(pydantic.BaseModel):
  """Represents a test case in the UI builder."""

  id: int | None = None
  logical_id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
  question: str
  asserts: list[AssertItem] = []


class TestCaseModalState(pydantic.BaseModel):
  """State for the test case editor modal."""

  mode: str = "add"  # "add" or "edit"
  index: int | None = None
  question_id: int | None = None
  asserts: list[AssertItem] = []


class AssertionMetric(pydantic.BaseModel):
  """Metrics for a group of assertions."""

  total: int
  passed: int
  failed: int
  pass_rate: float | None


class AssertionSummary(pydantic.BaseModel):
  """Summary metrics for all assertions in a trial."""

  overall: AssertionMetric
  accuracy: AssertionMetric
  diagnostic: AssertionMetric


class RunDetailPageState(pydantic.BaseModel):
  """State for the Run Detail page, containing run and trials data."""

  run: execution.RunSchema
  trials: list[execution.Trial]
