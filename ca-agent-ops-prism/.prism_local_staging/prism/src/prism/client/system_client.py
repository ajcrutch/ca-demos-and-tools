"""System Client implementation."""

from fast_depends import Depends
from fast_depends import inject
from prism.client import dependencies
from prism.server.services.worker import WorkerProcessManager


class SystemClient:
  """System Client for background operations."""

  @inject
  def start_worker_pool(
      self,
      num_workers: int = 2,
      service: WorkerProcessManager = Depends(
          dependencies.get_worker_pool_service
      ),
  ) -> None:
    """Starts the background worker manager."""
    service.max_concurrent_trials = num_workers
    service.start()
