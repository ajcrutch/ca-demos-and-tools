"""Script to recreate a Prism Test Suite with hard-coded Looker Regression data."""

import logging
import sys
from typing import Any

from prism.common.schemas.assertion import Assertion
from prism.common.schemas.assertion import AssertionType
from prism.server.db import SessionLocal
from prism.server.repositories.example_repository import ExampleRepository
from prism.server.repositories.suite_repository import SuiteRepository
from prism.server.services.suite_service import SuiteService
import pydantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Hard-coded Test Suite Data
TEST_CASES: list[dict[str, Any]] = [
    {
        "question": "Total ad events by ad type in November 2023",
        "asserts": [
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    "Date filter represents the period of November 2023. Note"
                    " that date-filter ranges are beginning-inclusive and"
                    ' end-exclusive, e.g. "date1 to date2" refers to a range of'
                    " date1 inclusive through date2 but excluding date2"
                ),
            },
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {
                    "fields": ["adgroups.ad_type", "adevents.total_ad_events"]
                },
            },
        ],
    },
    {
        "question": "Top 3 purchased SKUs in the Swim product category",
        "asserts": [
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {
                    "filters": [{
                        "field": (
                            "omni_channel_transactions__transaction_details.product_category"
                        ),
                        "value": "Swim",
                    }],
                    "limit": 3,
                    "sorts": ["measure desc"],
                },
            },
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    'Uses some measure that fits the intent of "top purchased"'
                    " (e.g. item_count, transaction_count)"
                ),
            },
        ],
    },
    {
        "question": "Top 5 conversation categories this month",
        "asserts": [
            {
                "type": AssertionType.AI_JUDGE,
                "value": 'uses date filter to represent "this month"',
            },
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    'Use some measure that fits the intent of "top"'
                    " conversation categories (e.g. number of conversations,"
                    " number of messages)"
                ),
            },
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {"limit": 5, "sorts": ["measure desc"]},
            },
        ],
    },
    {
        "question": (
            "Show me a line chart of weekly messages broken down by category"
            " from February 1st 2024 to today"
        ),
        "asserts": [
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    'uses date filter to represent "February 1st 2024 to'
                    ' today". Note that date-filter ranges are'
                    ' beginning-inclusive and end-exclusive, e.g. "date1 to'
                    ' date2" refers to a range of date1 inclusive through date2'
                    " but excluding date2"
                ),
            },
            {"type": AssertionType.CHART_CHECK_TYPE, "value": "line"},
            {
                "type": AssertionType.AI_JUDGE,
                "value": "uses a date-dimension representing week",
            },
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {
                    "fields": ["transcript__messages.issue_topic"],
                    "sorts": ["week asc"],
                },
            },
        ],
    },
    {
        "question": "Number of users by first visit quarter last year",
        "asserts": [
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {
                    "fields": ["user_session_fact.first_visit_quarter"],
                    "sorts": ["user_session_fact.first_visit_quarter asc"],
                },
            },
            {
                "type": AssertionType.AI_JUDGE,
                "value": 'uses a date filter representing "last year"',
            },
        ],
    },
    {
        "question": (
            "Which 3 product brands have the highest total sales, and what are"
            " each of their most popular product names?"
        ),
        "asserts": [
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    'creates initial query to determine top 3 "products.brand"'
                    " by total sales"
                ),
            },
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    "runs 3 follow-up queries for each of the top 3 brand,"
                    ' selecting top "product.item_name" by some measure that'
                    " represents popularity"
                ),
            },
        ],
    },
    {
        "question": (
            "What are the total conversations that are first time vs repeat?"
        ),
        "asserts": [
            {
                "type": AssertionType.AI_JUDGE,
                "value": 'uses measure to represent "total conversations"',
            },
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {"fields": ["transcript.is_first_call"]},
            },
        ],
    },
    {
        "question": (
            "Give me details on all of the incomplete procedures in Knoxville"
        ),
        "asserts": [
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    'must select a handful of fields that capture "procedure'
                    ' details"'
                ),
            },
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {
                    "filters": [
                        {"field": "ortho_procedures.complete", "value": "No"}
                    ]
                },
            },
            {
                "type": AssertionType.AI_JUDGE,
                "value": 'must have some filter corresponding to "Knoxville"',
            },
        ],
    },
    {
        "question": (
            "Among agents with at least 1000 ratings, who has the highest"
            " average rating?"
        ),
        "asserts": [
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {
                    "filters": [{
                        "field": "satisfaction_ratings.count",
                        "value": ">=1000",
                    }],
                    "fields": [
                        "agents.name",
                        "satisfaction_ratings.average_csat",
                    ],
                    "sorts": ["satisfaction_ratings.average_csat desc"],
                },
            },
            {
                "type": AssertionType.AI_JUDGE,
                "value": (
                    "indicates in response which single agent has the highest"
                    " average rating"
                ),
            },
        ],
    },
    {
        "question": (
            "Total supply cost for knee implants when supplier was Stryker and"
            " payer was commercial"
        ),
        "asserts": [
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {"fields": ["ortho_procedures.total_supply_costs"]},
            },
            {
                "type": AssertionType.LOOKER_QUERY_MATCH,
                "params": {
                    "filters": [
                        {
                            "field": "ortho_payer.payer_type",
                            "value": "Commercial",
                        },
                        {
                            "field": "ortho_supplier_preferences.supplier_name",
                            "value": "Stryker",
                        },
                        {
                            "field": "ortho_procedures.supply_category",
                            "value": "Knee Implant",
                        },
                    ]
                },
            },
        ],
    },
]


def generate_suite(dry_run: bool = True):
  """Main function to generate the test suite."""
  print(f"INFO: Starting test suite generation (dry_run={dry_run})")

  session = SessionLocal()
  suite_repo = SuiteRepository(session)
  example_repo = ExampleRepository(session)
  suite_service = SuiteService(session, suite_repo, example_repo)

  suite_name = "Looker Regression (v2)"
  suite_description = "Imported from ca_on_looker/regression.txtpbs"

  if dry_run:
    print(f"DRY RUN: Would create/use Suite: {suite_name}")
  else:
    # Check if suite already exists
    existing_suites = suite_service.list_suites()
    suite = next((s for s in existing_suites if s.name == suite_name), None)
    if not suite:
      suite = suite_service.create_suite(
          name=suite_name, description=suite_description
      )
      print(f"SUCCESS: Created Suite ID: {suite.id}")
    else:
      print(f"INFO: Using existing Suite ID: {suite.id}")

  for i, case in enumerate(TEST_CASES):
    question = case["question"]
    assertions = case["asserts"]

    # Add default weights if missing
    for a in assertions:
      if "weight" not in a:
        a["weight"] = 1.0

    if dry_run:
      print(f"INFO: Example {i + 1}: {question}")
      for a in assertions:
        print(f"  - Assert: {a}")
    else:
      try:
        # Convert to Pydantic models as expected by SuiteService/Repository
        parsed_asserts = [
            pydantic.TypeAdapter(Assertion).validate_python(a)
            for a in assertions
        ]
        suite_service.add_example(
            suite_id=suite.id, question=question, asserts=parsed_asserts
        )
      except pydantic.ValidationError as e:
        print(f"ERROR: Validation error for example '{question}': {e}")
      except Exception as e:
        print(f"ERROR: Failed to add example '{question}': {e}")

  if not dry_run:
    session.commit()
    print(f"SUCCESS: Imported {len(TEST_CASES)} examples.")

  session.close()


if __name__ == "__main__":
  is_dry_run = "--run" not in sys.argv
  generate_suite(dry_run=is_dry_run)
