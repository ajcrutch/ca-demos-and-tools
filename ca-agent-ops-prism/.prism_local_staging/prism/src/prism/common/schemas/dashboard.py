"""Schemas for Dashboard."""

from prism.common.schemas.execution import RunSchema
import pydantic


class DailyAccuracySchema(pydantic.BaseModel):
  """Daily accuracy score."""

  date: str
  accuracy: float | None


class DailyRunCountSchema(pydantic.BaseModel):
  """Daily evaluation run count."""

  date: str
  count: int


class AgentStatusSchema(pydantic.BaseModel):
  """Agent status information."""

  id: int
  name: str
  status: str  # "Online" | "Offline" | "Training"
  version: str | None = None


class DashboardStats(pydantic.BaseModel):
  """Statistics for the dashboard."""

  total_agents: int
  active_agents_count: int  # Agents evaluated in last 7 days
  active_agents_24h: int  # Agents evaluated in last 24h
  total_runs_7d: int
  avg_accuracy_score: float | None  # Avg of all runs in last 7 days
  accuracy_history: list[DailyAccuracySchema]
  run_volume_history: list[DailyRunCountSchema]
  recent_runs: list[RunSchema]
  agent_statuses: list[AgentStatusSchema]
