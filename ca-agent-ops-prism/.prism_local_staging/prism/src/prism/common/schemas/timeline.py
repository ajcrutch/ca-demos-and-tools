"""Pydantic schemas for Timeline visualization."""

import datetime
from typing import Literal

import pydantic


class TimelineEvent(pydantic.BaseModel):
  """A single event in the timeline."""

  title: str
  content: str
  content_type: Literal["text", "json", "code", "sql", "python", "vegalite"] = (
      "text"
  )
  icon: str = "bi:circle"
  duration_ms: int = 0
  cumulative_duration_ms: int = 0
  timestamp: datetime.datetime | None = None
  group_title: str | None = None

  # For internal storage of original data if needed, but not sent to UI usually
  # metadata: dict[str, Any] = pydantic.Field(default_factory=dict)


class TimelineGroup(pydantic.BaseModel):
  """A group of adjacent events sharing a common theme or tool."""

  title: str
  duration_ms: int = 0
  icon: str = "bi:circle"
  events: list[TimelineEvent] = pydantic.Field(default_factory=list)


class Timeline(pydantic.BaseModel):
  """Timeline DTO containing all events and metadata."""

  total_duration_ms: int
  events: list[TimelineEvent] = pydantic.Field(default_factory=list)
  groups: list[TimelineGroup] = pydantic.Field(default_factory=list)
