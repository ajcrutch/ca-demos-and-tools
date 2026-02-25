"""Reusable component for rendering the Asserts Guide."""

from dash import dcc
from dash import html
import dash_mantine_components as dmc
from prism.ui.constants import ASSERTS_GUIDE


def render_asserts_guide(guide_data=None):
  """Renders the list of assert descriptions."""
  if guide_data is None:
    guide_data = ASSERTS_GUIDE

  return html.Div([
      html.Div(
          [
              dmc.Text(
                  item["label"],
                  fw=700,
                  size="sm",
              ),
              dmc.Text(item["description"], size="sm", mb="xs"),
          ],
          className="mb-4",
      )
      for item in guide_data
  ])


def render_asserts_guide_accordion():
  """Renders the Asserts Guide inside a collapsible Accordion."""
  return dmc.Accordion(
      children=[
          dmc.AccordionItem(
              [
                  dmc.AccordionControl("Assertion Help Guide"),
                  dmc.AccordionPanel(
                      html.Div(
                          render_asserts_guide(),
                          style={"maxHeight": "70vh", "overflowY": "auto"},
                      )
                  ),
              ],
              value="asserts-guide",
          )
      ],
      className="mt-3",
  )
