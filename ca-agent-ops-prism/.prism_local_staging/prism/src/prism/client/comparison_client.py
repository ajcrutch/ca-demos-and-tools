"""Client for comparing evaluation runs."""

from fast_depends import Depends
from fast_depends import inject
from prism.client import dependencies
from prism.common.schemas import comparison as comparison_schemas
from prism.server.services.comparison_service import ComparisonService


class ComparisonClient:
  """Comparison Client implementation."""

  @inject
  def compare_runs(
      self,
      base_run_id: int,
      challenger_run_id: int,
      service: ComparisonService = Depends(dependencies.get_comparison_service),
  ) -> comparison_schemas.RunComparison:
    """Compares two runs and generates a comparison report."""
    return service.compare_runs(base_run_id, challenger_run_id)
