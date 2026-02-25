"""Callbacks for the application shell."""

import dash
from dash import callback
from dash import Input
from dash import Output
from dash import State
from prism.client import get_client
from prism.ui.constants import CP
from prism.ui.constants import GLOBAL_PROJECT_ID_STORE
from prism.ui.utils import typed_callback


@typed_callback(
    Output(GLOBAL_PROJECT_ID_STORE, "data"),
    [Input("url", CP.PATHNAME)],
    state=[State(GLOBAL_PROJECT_ID_STORE, "data")],
)
def fetch_current_project_id(pathname, current_data):
  """Fetches the current GCP project ID on app load."""
  if current_data is not None:
    return dash.no_update

  try:
    client = get_client().agents
    return client.get_current_gcp_project()
  except Exception:  # pylint: disable=broad-except
    return None


@callback(
    output=[
        Output("nav-overview", "c"),
        Output("nav-agents", "c"),
        Output("nav-evaluations", "c"),
        Output("nav-test-suites", "c"),
        Output("nav-comparison", "c"),
    ],
    inputs=[Input("url", CP.PATHNAME)],
)
def update_active_nav_link(pathname: str):
  """Updates the active state of navigation links based on current pathname."""
  if not pathname:
    return [dash.no_update] * 5

  def _get_color(is_active: bool) -> str:
    return "blue" if is_active else "black"

  return [
      _get_color(pathname == "/overview" or pathname == "/"),
      _get_color(pathname.startswith("/agents")),
      _get_color(pathname.startswith("/evaluations")),
      _get_color(pathname.startswith("/test_suites")),
      _get_color(pathname.startswith("/compare")),
  ]
