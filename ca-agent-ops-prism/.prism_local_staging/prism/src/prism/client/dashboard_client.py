"""Dashboard Client implementation."""

from fast_depends import Depends
from fast_depends import inject
from prism.client import dependencies
from prism.common.schemas import dashboard as dashboard_schemas
from prism.server.services.dashboard_service import DashboardService


class DashboardClient:
  """Dashboard Client implementation."""

  @inject
  def get_dashboard_stats(
      self,
      service: DashboardService = Depends(dependencies.get_dashboard_service),
  ) -> dashboard_schemas.DashboardStats:
    """Calculates and returns dashboard statistics."""
    return service.get_dashboard_stats()
