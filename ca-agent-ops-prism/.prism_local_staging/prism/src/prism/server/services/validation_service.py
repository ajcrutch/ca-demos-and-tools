"""Service for validating assertion data using Pydantic schemas."""

import logging
from typing import Any

from prism.common.schemas.assertion import AssertionRequest
import pydantic
import yaml


def validate_assertion(assertion_data: dict[str, Any]) -> str | None:
  """Validates assertion data against Pydantic schemas.

  Args:
      assertion_data: The raw assertion data to validate.

  Returns:
      A user-friendly error message if validation fails, else None.
  """
  try:
    # Use TypeAdapter for the discriminated union
    pydantic.TypeAdapter(AssertionRequest).validate_python(assertion_data)
    return None
  except pydantic.ValidationError as e:
    # Format a user-friendly error message
    error_msgs = []
    for error in e.errors():
      loc = " -> ".join(str(l) for l in error["loc"])
      msg = error["msg"]
      error_msgs.append(f"{loc}: {msg}")

    error_str = "; ".join(error_msgs)
    logging.warning("Assertion validation failed: %s", error_str)
    return error_str
  except Exception as e:  # pylint: disable=broad-exception-caught
    logging.exception("Unexpected error during assertion validation")
    return str(e)


def parse_yaml_safely(
    yaml_str: str,
) -> tuple[dict[str, Any] | None, str | None]:
  """Parses YAML string safely and returns (data, error_message)."""
  if not yaml_str:
    return {}, None
  try:
    data = yaml.safe_load(yaml_str)
    if not isinstance(data, dict):
      return None, "YAML must resolve to a dictionary/object."
    return data, None
  except yaml.YAMLError as e:
    return None, f"Invalid YAML format: {str(e)}"
  except Exception as e:  # pylint: disable=broad-exception-caught
    return None, f"Unexpected error parsing YAML: {str(e)}"
