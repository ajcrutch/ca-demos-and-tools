"""Pydantic schemas for Trace and Latency metrics."""

from typing import Any

from google.cloud import geminidataanalytics
from google.protobuf import json_format
import pydantic


class LatencyMetrics(pydantic.BaseModel):
  """Metrics for operation latency."""

  time_to_first_response: int | None = None
  total_duration: int


class AskQuestionResponse(pydantic.BaseModel):
  """Response from an ask_question call."""

  # The response is a list of JSON-dumped Protobuf messages
  # (geminidataanalytics.Message).
  # We store it as dicts for JSON serialization compatibility with DBs/API
  # responses, but providing the `protobuf_response` property to rehydrate them
  # into strong types.
  response: list[dict[str, Any]]
  latency: LatencyMetrics
  error_message: str | None = None

  @property
  def protobuf_response(self) -> list[geminidataanalytics.Message]:
    """Returns the response as a list of Protobuf Message objects."""
    # geminidataanalytics.Message is a proto-plus message.
    # self.response contains dicts, likely in JSON (camelCase) format from MessageToDict.
    # We must use ParseDict to reconstruct the proto correctly.
    messages = []
    for t in self.response:
      try:
        # Create a fresh internal protobuf message
        pb_instance = geminidataanalytics.Message()._pb
        # Parse the JSON dict into the protobuf
        json_format.ParseDict(t, pb_instance, ignore_unknown_fields=True)
        # Wrap it back into the high-level proto-plus object
        messages.append(geminidataanalytics.Message.wrap(pb_instance))
      except Exception:
        # Fallback: Maybe it's already snake_case?
        messages.append(geminidataanalytics.Message(t))
    return messages
