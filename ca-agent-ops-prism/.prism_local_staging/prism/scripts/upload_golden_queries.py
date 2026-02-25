import argparse
import csv
import logging
import os
import sys
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow imports from prism
# Assuming this script is in .../prism/scripts/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

try:
  from prism.server.clients.gemini_data_analytics_client import (
      GeminiDataAnalyticsClient,
  )
  from prism.common.schemas.agent import (
      LookerGoldenQuery,
      LookerQuery,
      LookerFilter,
      AgentConfig,
  )
  from prism.server.db import SessionLocal
  from prism.server.repositories.agent_repository import AgentRepository
except ImportError as e:
  logger.error(
      "Error importing Prism modules: %s. Make sure you are running this script"
      " from the correct environment.",
      e,
  )
  sys.exit(1)


def parse_looker_url(url: str) -> dict:
  """Parses a Looker explore URL and extracts model, explore, fields, filters, sorts, and limit.

  Reused from upload_looker_assertions.py.
  """
  parsed_url = urlparse(url)

  # Extract model and explore from path
  # e.g. /explore/merch-ieh/merch_holiday_inv_trans_store
  path_parts = parsed_url.path.strip("/").split("/")
  if len(path_parts) >= 3 and path_parts[0] == "explore":
    model = path_parts[1]
    explore = path_parts[2]
  else:
    raise ValueError(f"Invalid Looker explore URL path: {parsed_url.path}")

  # Parse query parameters
  # parse_qs returns a dict where values are lists of strings
  query_params = parse_qs(parsed_url.query, keep_blank_values=True)

  # Extract fields
  fields = []
  if "fields" in query_params:
    fields = query_params["fields"][0].split(",")

  # Extract filters
  filters = []
  # Manual parsing to handle Looker's encoding quirks if necessary,
  # but reusing the logic that seemed to work in upload_looker_assertions.py
  # functionality primarily:
  raw_query = parsed_url.query
  for pair in raw_query.split("&"):
    if not pair or "=" not in pair:
      continue
    k, v = pair.split("=", 1)
    k_dec = unquote(k)
    v_dec = unquote(v)

    if k_dec.startswith("f[") and k_dec.endswith("]"):
      field_name = k_dec[2:-1]
      filters.append({"field": field_name, "value": v_dec})

  # Extract sorts
  sorts = None
  sorts_raw = []
  for pair in raw_query.split("&"):
    if pair.startswith("sorts="):
      sorts_raw.append(unquote(pair[6:]))
  if sorts_raw:
    sorts = sorts_raw[0].split(",")

  # Extract limit
  limit = None
  if "limit" in query_params:
    limit = query_params["limit"][0]

  return {
      "model": model,
      "explore": explore,
      "fields": fields,
      "filters": filters,
      "sorts": sorts,
      "limit": limit,
  }


def get_agent_client(project: str) -> GeminiDataAnalyticsClient:
  """Initializes the GeminiDataAnalyticsClient."""
  return GeminiDataAnalyticsClient(project=project)


def process_csv_and_upload(
    csv_path: str,
    agent_name_or_id: str,
    project: str,
    location: str,
    dry_run: bool = False,
):
  """Reads CSV, parses URLs, and uploads Golden Queries to the Agent."""

  # Initialize Client
  # Project format for client init: projects/{project}/locations/{location}
  # But the client class takes 'project' as the first arg in __init__?
  # Let's check GeminiDataAnalyticsClient.__init__ docstring/code.
  # It takes `project` which it passes to `parent=self.project` in list_agents.
  # So it expects `projects/p/locations/l`.
  parent_resource = f"projects/{project}/locations/{location}"
  client = get_agent_client(parent_resource)

  # Fetch existing agent
  full_agent_name = None

  # Check if agent_name_or_id is potentially a Prism Integer ID
  if agent_name_or_id.isdigit():
    try:
      prism_id = int(agent_name_or_id)
      logger.info("Detected Prism Agent ID. Looking up in database...")
      db = SessionLocal()
      try:
        repo = AgentRepository(db)
        prism_agent = repo.get_by_id(prism_id)
        if prism_agent and prism_agent.agent_resource_id:
          full_agent_name = (
              f"{parent_resource}/dataAgents/{prism_agent.agent_resource_id}"
          )
          logger.info(
              "Found GCP Agent Resource ID: %s", prism_agent.agent_resource_id
          )
        elif prism_agent:
          logger.error(
              "Prism Agent found but has no GCP Agent Resource ID linked."
          )
          sys.exit(1)
        else:
          logger.error("Prism Agent ID %d not found in database.", prism_id)
          sys.exit(1)
      finally:
        db.close()
    except Exception as e:
      logger.warning(
          "Failed to lookup Prism ID in database: %s. Proceeding as if string.",
          e,
      )

  if not full_agent_name:
    if "/dataAgents/" in agent_name_or_id:
      full_agent_name = agent_name_or_id
    else:
      full_agent_name = f"{parent_resource}/dataAgents/{agent_name_or_id}"

  logger.info("Fetching agent: %s", full_agent_name)
  try:
    agent = client.get_agent(full_agent_name)
  except Exception as e:
    logger.error("Failed to fetch agent: %s", e)
    sys.exit(1)

  if not agent:
    logger.error("Agent not found: %s", full_agent_name)
    sys.exit(1)

  logger.info("Successfully fetched agent: %s", agent.name)

  # Parse CSV
  new_golden_queries = []
  with open(csv_path, "r", encoding="utf-8") as f:
    # Handle potentially different delimiters or just try DictReader
    # verify delimiter. expected tab or comma.
    # We can try csv.Sniffer() or just assume tab if file extension is .tsv?
    # User said "csv or tsv file".
    # Let's peek at the first line.
    first_line = f.readline()
    f.seek(0)
    delimiter = "\t" if "\t" in first_line else ","
    print(f"Detected delimiter: '{delimiter}'")

    reader = csv.DictReader(f, delimiter=delimiter)
    headers = reader.fieldnames

    # Identify columns
    q_col = next(
        (
            h
            for h in headers
            if "question" in h.lower() and "number" not in h.lower()
        ),
        None,
    )
    url_col = next(
        (
            h
            for h in headers
            if "share" in h.lower() and "unencoded" not in h.lower()
        ),
        None,
    )

    if not q_col or not url_col:
      logger.error(
          "Could not identify 'question' or 'share' URL columns. Headers: %s",
          headers,
      )
      sys.exit(1)

    for row in reader:
      question = row[q_col]
      url = row[url_col]

      if not question or not url:
        continue

      try:
        params = parse_looker_url(url)
      except Exception as e:
        logger.warning(
            "Skipping row: Error parsing URL for question '%s': %s", question, e
        )
        continue

      # Convert to LookerGoldenQuery
      # Map params to LookerQuery
      filters = []
      if params["filters"]:
        for f in params["filters"]:
          filters.append(LookerFilter(field=f["field"], value=f["value"]))

      looker_query = LookerQuery(
          model=params["model"],
          explore=params["explore"],
          fields=params["fields"],
          filters=filters,
          sorts=params["sorts"],
          limit=params["limit"],
      )

      gq = LookerGoldenQuery(
          natural_language_questions=[question], looker_query=looker_query
      )
      new_golden_queries.append(gq)

  logger.info("Parsed %d new Golden Queries from CSV.", len(new_golden_queries))

  if not new_golden_queries:
    logger.info("No queries to upload. Exiting.")
    return

  # Append to existing
  existing_golden_queries = []
  if agent.config and agent.config.golden_queries:
    existing_golden_queries = agent.config.golden_queries

  # Check for duplicates?
  # For now, simplistic append.
  # But maybe we should avoid exact duplicates (same question same query)?
  # Let's just append as requested, user can manage duplicates.
  final_golden_queries = existing_golden_queries + new_golden_queries

  logger.info(
      "Total Golden Queries after merge: %d (Old: %d, New: %d)",
      len(final_golden_queries),
      len(existing_golden_queries),
      len(new_golden_queries),
  )

  if dry_run:
    logger.info(
        "[DRY RUN] Would update agent with %d golden queries.",
        len(final_golden_queries),
    )
    # Print sample
    logger.info(
        "Sample new query: %s",
        new_golden_queries[0] if new_golden_queries else "None",
    )
    return

  # Update Agent
  # We need to construct a new AgentConfig with the updated golden_queries
  # and pass it to update_agent.
  # client.update_agent takes (agent_name, config=...)

  # Create a config object with ONLY golden_queries set?
  # update_agent implementation in client:
  # if config is not None: ... merges ...
  # It looks like it handles partial updates by fetching existing first.
  # But we already fetched existing agent to get existing queries.
  # The client's update_agent ALSO fetches existing to merge.
  # We can just pass the NEW list in a config object.

  update_config = AgentConfig(golden_queries=final_golden_queries)

  try:
    logger.info("Updating agent...")
    client.update_agent(full_agent_name, config=update_config)
    logger.info("Successfully updated agent.")
  except Exception as e:
    logger.error("Failed to update agent: %s", e)
    sys.exit(1)


if __name__ == "__main__":
  load_dotenv()

  parser = argparse.ArgumentParser(
      description="Upload Golden Queries to a Prism Data Agent."
  )
  parser.add_argument("csv_file", help="Path to input CSV file")
  parser.add_argument(
      "--agent-id",
      help=(
          "ID or Resource Name of the Agent. If just ID, requires --project and"
          " --location (or env vars)."
      ),
      required=True,
  )
  parser.add_argument(
      "--project",
      help="GCP Project ID. Defaults to PRISM_GENAI_CLIENT_PROJECT env var.",
      default=os.environ.get("PRISM_GENAI_CLIENT_PROJECT"),
  )
  parser.add_argument(
      "--location",
      help="GCP Location. Defaults to PRISM_GENAI_CLIENT_LOCATION env var.",
      default=os.environ.get("PRISM_GENAI_CLIENT_LOCATION"),
  )
  parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Parse CSV and prepare update but do not actually call API.",
  )

  args = parser.parse_args()

  if not args.project or not args.location:
    logger.error(
        "Project and Location must be set via arguments or environment"
        " variables."
    )
    sys.exit(1)

  process_csv_and_upload(
      args.csv_file, args.agent_id, args.project, args.location, args.dry_run
  )
