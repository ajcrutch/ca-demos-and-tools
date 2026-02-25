"""Main Prism Client implementation."""

from prism.client.agent_client import AgentsClient
from prism.client.comparison_client import ComparisonClient
from prism.client.playground_client import PlaygroundClient
from prism.client.run_client import RunsClient
from prism.client.suggestion_client import SuggestionClient
from prism.client.suite_client import SuitesClient
from prism.client.system_client import SystemClient


class PrismClient:
  """Main Prism Client combining all sub-clients."""

  def __init__(self):
    self._agents = AgentsClient()
    self._suites = SuitesClient()
    self._runs = RunsClient()
    self._playground = PlaygroundClient()
    self._suggestion = SuggestionClient()
    self._comparison = ComparisonClient()
    self._system = SystemClient()
    self._trials = self._runs

  @property
  def agents(self) -> AgentsClient:
    return self._agents

  @property
  def suites(self) -> SuitesClient:
    return self._suites

  @property
  def runs(self) -> RunsClient:
    return self._runs

  @property
  def trials(self) -> RunsClient:
    return self._trials

  @property
  def playground(self) -> PlaygroundClient:
    return self._playground

  @property
  def suggestion(self) -> SuggestionClient:
    return self._suggestion

  @property
  def comparison(self) -> ComparisonClient:
    return self._comparison

  @property
  def system(self) -> SystemClient:
    return self._system
