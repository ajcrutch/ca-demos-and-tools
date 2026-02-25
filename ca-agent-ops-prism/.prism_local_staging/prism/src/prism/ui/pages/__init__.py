"""UI pages package."""

from prism.ui.pages import agent_add
from prism.ui.pages import agent_detail
from prism.ui.pages import agent_home
from prism.ui.pages import agent_monitor
from prism.ui.pages import agent_trace
from prism.ui.pages import context_prototype
from prism.ui.pages import evaluation_detail
from prism.ui.pages import evaluations
from prism.ui.pages import execution_detail
from prism.ui.pages import getting_started
from prism.ui.pages import home
from prism.ui.pages import run_comparison
from prism.ui.pages import test_suite_home
from prism.ui.pages import test_suite_new
from prism.ui.pages import test_suite_questions
from prism.ui.pages import test_suite_view
from prism.ui.pages import trial_detail


def register_all_pages():
  """Explicitly register all Dash pages."""
  agent_add.register_page()
  agent_detail.register_page()
  agent_home.register_page()
  agent_monitor.register_page()
  agent_trace.register_page()
  context_prototype.register_page()
  test_suite_home.register_page()
  test_suite_new.register_page()
  test_suite_questions.register_page()
  test_suite_view.register_page()
  evaluation_detail.register_page()
  evaluations.register_page()
  execution_detail.register_page()
  getting_started.register_page()
  home.register_page()
  run_comparison.register_page()
  trial_detail.register_page()
