"""UI callbacks package."""

from prism.ui.callbacks import agent_add_callbacks
from prism.ui.callbacks import agent_callbacks
from prism.ui.callbacks import agent_context_test_callbacks
from prism.ui.callbacks import agent_detail_callbacks
from prism.ui.callbacks import agent_monitor_callbacks
from prism.ui.callbacks import agent_trace_callbacks
from prism.ui.callbacks import evaluation_callbacks
from prism.ui.callbacks import home_callbacks
from prism.ui.callbacks import run_comparison_callbacks
from prism.ui.callbacks import shell_callbacks
from prism.ui.callbacks import test_suite_callbacks
from prism.ui.callbacks import test_suite_questions_callbacks


def register_all_callbacks():
  """No-op to register all callbacks.

  Callbacks are already registered by above imports.
  """
