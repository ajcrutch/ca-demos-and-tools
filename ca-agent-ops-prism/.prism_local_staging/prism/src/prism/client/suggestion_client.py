"""Suggestion Client implementation."""

from typing import Any

from fast_depends import Depends
from fast_depends import inject
from prism.client import dependencies
from prism.common.schemas import assertion as assertion_schemas
from prism.server.services.suggestion_service import SuggestionService


class SuggestionClient:
  """Suggestion Client implementation."""

  @inject
  def suggest_assertions(
      self,
      trial_id: int,
      existing_assertions: list[assertion_schemas.Assertion] | None = None,
      service: SuggestionService = Depends(dependencies.get_suggestion_service),
  ) -> list[assertion_schemas.Assertion]:
    """Suggests assertions for a trial."""
    return service.suggest_assertions(
        trial_id=trial_id, existing_assertions=existing_assertions
    )

  @inject
  def curate_suggestion(
      self,
      suggestion_id: int,
      action: str,
      service: SuggestionService = Depends(dependencies.get_suggestion_service),
  ) -> None:
    """Accepts or rejects a suggested assertion."""
    service.curate_suggestion(suggestion_id=suggestion_id, action=action)

  @inject
  def suggest_assertions_from_trace(
      self,
      trace: list[dict[str, Any]],
      existing_assertions: list[assertion_schemas.Assertion] | None = None,
      location: str | None = None,
      service: SuggestionService = Depends(dependencies.get_suggestion_service),
  ) -> list[assertion_schemas.Assertion]:
    """Suggests assertions for a given trace."""
    return service.suggest_assertions_from_trace(
        trace=trace,
        existing_assertions=existing_assertions,
        location=location,
    )
