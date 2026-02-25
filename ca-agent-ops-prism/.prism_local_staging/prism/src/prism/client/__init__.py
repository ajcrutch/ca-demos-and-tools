"""Prism API Client."""

from prism.client.agent_client import AgentsClient
from prism.client.prism_client import PrismClient
from prism.client.run_client import RunsClient
from prism.client.suite_client import SuitesClient


__all__ = [
    "PrismClient",
    "AgentsClient",
    "SuitesClient",
    "RunsClient",
    "get_client",
]


_CLIENT: PrismClient | None = None


def get_client() -> PrismClient:
  """Factory to get the configured Prism Client."""
  global _CLIENT
  if _CLIENT is None:
    _CLIENT = PrismClient()
  return _CLIENT
