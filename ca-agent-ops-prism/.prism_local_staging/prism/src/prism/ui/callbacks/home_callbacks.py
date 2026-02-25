"""Callbacks for the Home Dashboard."""

from dash import Input
from dash import Output
from prism.client.dashboard_client import DashboardClient
from prism.ui.components.dashboard_components import render_evaluation_chart
from prism.ui.components.dashboard_components import render_run_volume_chart
from prism.ui.components.tables import render_run_table
from prism.ui.pages.home_ids import HomeIds
from prism.ui.utils import typed_callback


@typed_callback(
    [
        Output(HomeIds.CHART_CONTAINER, "children"),
        Output(HomeIds.VOLUME_CHART_CONTAINER, "children"),
        Output(HomeIds.RECENT_RUNS_CONTAINER, "children"),
    ],
    [Input(HomeIds.INTERVAL, "n_intervals")],
)
def update_dashboard(n_intervals: int):
  """Updates dashboard statistics and components."""
  del n_intervals  # Unused argument

  client = DashboardClient()
  stats = client.get_dashboard_stats()

  # 2. Performance Chart
  chart_data = [item.model_dump() for item in stats.accuracy_history]
  chart = render_evaluation_chart(chart_data)

  # 3. Volume Chart
  volume_data = [item.model_dump() for item in stats.run_volume_history]
  volume_chart = render_run_volume_chart(volume_data)

  # 4. Recent Runs
  # Names are now included in the RunSchema via the Client/Service
  recent_runs = render_run_table(
      stats.recent_runs,
      table_id=HomeIds.RECENT_RUNS_CONTAINER,
  )

  return (
      chart,
      volume_chart,
      recent_runs,
  )
