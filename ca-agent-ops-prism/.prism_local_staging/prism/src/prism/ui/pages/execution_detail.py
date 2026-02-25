"""Execution Detail page."""

import dash
from dash import html
import dash_mantine_components as dmc
from prism.ui.components.assertion_components import render_assertion_form_content
from prism.ui.components.page_layout import render_page
from prism.ui.ids import EvaluationIds as Ids


def layout(execution_id: str = None, **_kwargs):
  """Renders the Execution Detail layout."""
  title = (
      f"Execution Detail #{execution_id}"
      if execution_id
      else "Execution Detail"
  )
  return render_page(
      title=title,
      breadcrumbs_id=Ids.EXECUTION_BREADCRUMBS_CONTAINER,
      children=[
          html.Div(
              id=Ids.EXECUTION_DETAIL_CONTAINER,
              children=[dmc.Center(children=[dmc.Loader(variant="dots")])],
          ),
          # Suggestion Edit Modal
          dmc.Modal(
              id=Ids.EXECUTION_SUG_EDIT_MODAL,
              size="80%",
              title="Edit Suggestion",
              children=[
                  render_assertion_form_content(
                      ids_class=type(
                          "ExecutionSuggestionEditIds",
                          (),
                          {
                              "ASSERT_TYPE": Ids.EXECUTION_SUG_EDIT_TYPE,
                              "ASSERT_WEIGHT": Ids.EXECUTION_SUG_EDIT_WEIGHT,
                              "ASSERT_VALUE": Ids.EXECUTION_SUG_EDIT_VALUE,
                              "ASSERT_YAML": Ids.EXECUTION_SUG_EDIT_YAML,
                              "ASSERT_CHART_TYPE": (
                                  Ids.EXECUTION_SUG_EDIT_CHART_TYPE
                              ),
                              "ASSERT_GUIDE_CONTAINER": (
                                  Ids.EXECUTION_SUG_EDIT_GUIDE_CONTAINER
                              ),
                              "ASSERT_GUIDE_TITLE": (
                                  Ids.EXECUTION_SUG_EDIT_GUIDE_TITLE
                              ),
                              "ASSERT_GUIDE_DESC": (
                                  Ids.EXECUTION_SUG_EDIT_GUIDE_DESC
                              ),
                              "ASSERT_EXAMPLE_CONTAINER": (
                                  Ids.EXECUTION_SUG_EDIT_EXAMPLE_CONTAINER
                              ),
                              "ASSERT_EXAMPLE_VALUE": (
                                  Ids.EXECUTION_SUG_EDIT_EXAMPLE_VALUE
                              ),
                              "ASSERT_EXAMPLE_YAML": (
                                  Ids.EXECUTION_SUG_EDIT_EXAMPLE_YAML
                              ),
                              "VAL_MSG": Ids.EXECUTION_SUG_VAL_MSG,
                          },
                      ),
                      is_edit=True,
                      is_suggestion=True,
                  ),
                  # Context Store for Edit (Execution ID, Index)
                  dash.dcc.Store(id=Ids.EXECUTION_SUG_EDIT_CONTEXT),
                  # Signal Store for Refresh
                  dash.dcc.Store(id=Ids.EXECUTION_SUG_UPDATE_SIGNAL),
                  # Loading Store for Skeletons
                  dash.dcc.Store(
                      id=Ids.EXECUTION_SUG_LOADING_STORE, data=False
                  ),
                  dmc.Group(
                      justify="flex-end",
                      mt="xl",
                      children=[
                          dmc.Button(
                              "Save & Update Execution",
                              id=Ids.EXECUTION_SUG_EDIT_SAVE_BTN,
                          ),
                      ],
                  ),
              ],
          ),
      ],
  )


def register_page():
  dash.register_page(
      __name__,
      path_template="/executions/<execution_id>",
      title="Prism | Execution Detail",
      layout=layout,
  )
