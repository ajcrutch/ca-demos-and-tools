"""Reusable empty state components."""

from dash_iconify import DashIconify
import dash_mantine_components as dmc


def render_empty_state(
    title: str,
    description: str,
    button_label: str | None = None,
    href: str | None = None,
    icon: str = "bi:inbox",
):
  """Renders a centered empty state card."""
  children = [
      dmc.ThemeIcon(
          variant="light",
          color="gray",
          size=60,
          radius="md",
          children=DashIconify(icon=icon, width=30),
          mb="md",
      ),
      dmc.Title(title, order=3, fw=600, mb="sm"),
      dmc.Text(description, c="dimmed", size="md", mb="xl", maw=500),
  ]

  if button_label and href:
    children.append(
        dmc.Anchor(
            dmc.Button(
                button_label,
                leftSection=DashIconify(icon="bi:plus-lg"),
                size="md",
            ),
            href=href,
            underline=False,
        )
    )

  return dmc.Center(
      style={"height": "60vh", "gridColumn": "1 / -1"},
      children=[
          dmc.Paper(
              withBorder=True,
              radius="md",
              shadow="none",
              p="xl",
              children=dmc.Stack(
                  align="center",
                  justify="center",
                  children=children,
              ),
          )
      ],
  )
