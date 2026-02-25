import argparse
import csv
import json
import os
import sys
from urllib.parse import parse_qs, unquote, urlparse
from dotenv import load_dotenv

try:
  import psycopg2
  from psycopg2.extras import Json
except ImportError:
  print(
      "Error: psycopg2 is not installed. Please install it with 'pip install"
      " psycopg2-binary'"
  )
  sys.exit(1)


def parse_looker_url(url: str) -> dict:
  """Parses a Looker explore URL and extracts model, explore, fields, filters, sorts, and limit."""
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
  query_params = parse_qs(parsed_url.query, keep_blank_values=True)

  # Extract fields
  fields = []
  if "fields" in query_params:
    fields = query_params["fields"][0].split(",")

  # Extract filters
  filters = []
  for key, values in query_params.items():
    if key.startswith("f[") and key.endswith("]"):
      field_name = key[2:-1]  # Extract field name from f[field_name]
      # Looker encodes spaces as +, parse_qs handles some of this,
      # but we'll take the first value and optionally decode further if needed
      value = values[0]
      # Looker values might need further unquoting if they contain quotes etc.
      # but the examples show keeping them as is, e.g. "after 2025/10/20"
      # Note: parse_qs decodes %2F to / and + to space.
      # The examples from the user for filters kept the '+' as spaces or literal '+' ?
      # Example 2 url has after+2025%2F10%2F20, unencoded is after 2025/10/20.
      # Actually, parse_qs decodes `+` to ` ` by default.
      # Looker often uses ` ` or `+` in the actual filter text.
      # To match the user's example: {"field": "fiscal_pop_parameters.day_fy_date", "value": "after+2025/10/20"}
      # The user explicitly wants `+` in the value if it was `+` in the url, but parse_qs converts `+` to ` `.
      # Let's use string replacement to keep it exactly as the raw query string decoded ?
      # Actually, parse_qs does standard parsing. Let's see how parse_qs handles it.
      # parse_qs(..., keep_blank_values=True) returns strings.
      pass

  # Better approach for exact matching to user's example: manual parse of query string
  filters = []
  # Re-parse manually to match the exact string formatting the user asked for
  # (e.g., keeping + instead of spaces if they want, but unquoting %2F to /)
  raw_query = parsed_url.query
  for pair in raw_query.split("&"):
    if not pair:
      continue
    if "=" not in pair:
      continue
    k, v = pair.split("=", 1)
    k_dec = unquote(k)
    v_dec = unquote(v)  # unquote decodes %2F, %22 etc, but leaves + alone!

    if k_dec.startswith("f[") and k_dec.endswith("]"):
      field_name = k_dec[2:-1]
      filters.append({"field": field_name, "value": v_dec})

  # Extract sorts
  sorts = None
  if "sorts" in query_params:
    # User example: ["cv_merch_fiscal_metrics_holiday.op_gmv_retail_amt+desc"]
    # parse_qs converts + to space. Manual unquote leaves + alone.
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

  assertion_params = {
      "model": model,
      "explore": explore,
      "fields": fields,
      "filters": filters if filters else None,
      "sorts": sorts if sorts else None,
      "limit": limit,
  }

  return assertion_params


def get_db_connection():
  """Establishes connection to the PostgreSQL database."""
  load_dotenv()
  db_url = os.environ.get("DATABASE_URL")
  if not db_url:
    print(
        "Error: DATABASE_URL environment variable is not set. Check your"
        " .env file."
    )
    sys.exit(1)

  try:
    conn = psycopg2.connect(db_url)
    return conn
  except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)


def process_csv_and_upload(
    csv_path: str, test_suite_id: int, new_test_suite_name: str = None
):
  conn = get_db_connection()
  cursor = conn.cursor()

  try:
    # Create new test suite if requested
    if new_test_suite_name:
      print(f"Creating new test suite: '{new_test_suite_name}'")
      cursor.execute(
          "INSERT INTO test_suites (name, is_archived, tags, description)"
          " VALUES (%s, FALSE, '{}', '') RETURNING id;",
          (new_test_suite_name,),
      )
      test_suite_id = cursor.fetchone()[0]
      print(f"Created test suite with ID: {test_suite_id}")
    elif not test_suite_id:
      print("Error: Must provide either --test-suite-id or --new-test-suite")
      sys.exit(1)
    else:
      print(f"Using existing test suite ID: {test_suite_id}")

    with open(csv_path, "r", encoding="utf-8") as f:
      reader = csv.DictReader(f, delimiter="\t")
      # Find the exact header names
      headers = reader.fieldnames
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
        print(
            "Error: Could not identify question or url columns. Headers found:"
            f" {headers}"
        )
        sys.exit(1)

      success_count = 0
      for row in reader:
        question = row[q_col]
        url = row[url_col]

        if not question or not url:
          continue

        try:
          params = parse_looker_url(url)
        except Exception as e:
          print(f"Error parsing URL for question '{question}': {e}")
          continue

        # Insert example
        # "logical_id" defaults to gen_random_uuid(), but we might need to supply it if there's no default.
        # Assuming gen_random_uuid() is default or we can supply it via SQL.
        cursor.execute(
            """
                    INSERT INTO examples (test_suite_id, logical_id, question, is_archived) 
                    VALUES (%s, gen_random_uuid(), %s, FALSE) 
                    RETURNING id;
                    """,
            (test_suite_id, question),
        )
        example_id = cursor.fetchone()[0]

        # Generate assertions
        assertions_to_insert = []

        base_params = {"model": params["model"], "explore": params["explore"]}

        # 1. Full assertion (already parsed)
        assertions_to_insert.append(
            {"original_assertion_id": None, "reasoning": None, "params": params}
        )

        # 2. Assertions for each field
        if params.get("fields"):
          for field in params["fields"]:
            field_params = base_params.copy()
            field_params["fields"] = [field]
            field_params["filters"] = None
            field_params["sorts"] = None
            field_params["limit"] = None
            assertions_to_insert.append({
                "original_assertion_id": None,
                "reasoning": None,
                "params": field_params,
            })

        # 3. Assertions for each filter field/value pair
        if params.get("filters"):
          for filter_obj in params["filters"]:
            filter_params = base_params.copy()
            filter_params["fields"] = []
            filter_params["filters"] = [filter_obj]
            filter_params["sorts"] = None
            filter_params["limit"] = None
            assertions_to_insert.append({
                "original_assertion_id": None,
                "reasoning": None,
                "params": filter_params,
            })

        # 4. Assertions for each sort
        if params.get("sorts"):
          for sort in params["sorts"]:
            sort_params = base_params.copy()
            sort_params["fields"] = []
            sort_params["filters"] = None
            sort_params["sorts"] = [sort]
            sort_params["limit"] = None
            assertions_to_insert.append({
                "original_assertion_id": None,
                "reasoning": None,
                "params": sort_params,
            })

        # 5. Assertion for limit
        if params.get("limit"):
          limit_params = base_params.copy()
          limit_params["fields"] = []
          limit_params["filters"] = None
          limit_params["sorts"] = None
          limit_params["limit"] = params["limit"]
          assertions_to_insert.append({
              "original_assertion_id": None,
              "reasoning": None,
              "params": limit_params,
          })

        # Insert all assertions for this example
        for assertion_json in assertions_to_insert:
          cursor.execute(
              """
                INSERT INTO assertions (example_id, type, weight, is_archived, params) 
                VALUES (%s, 'LOOKER_QUERY_MATCH', 1.0, FALSE, %s);
                """,
              (example_id, Json(assertion_json)),
          )

        print(
            f"Successfully uploaded: Question '{question}' with"
            f" {len(assertions_to_insert)} assertions."
        )
        success_count += 1

    conn.commit()
    print(
        f"\nUpload complete. Successfully processed {success_count} questions."
    )

  except Exception as e:
    conn.rollback()
    print(f"An error occurred during database operations: {e}")
  finally:
    cursor.close()
    conn.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Upload Looker questions and URLs as examples and assertions."
  )
  parser.add_argument("csv_file", help="Path to the input CSV file")

  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument(
      "--test-suite-id",
      type=int,
      help="Existing test suite ID to add examples to",
  )
  group.add_argument(
      "--new-test-suite", type=str, help="Name for a new test suite to create"
  )

  args = parser.parse_args()

  process_csv_and_upload(args.csv_file, args.test_suite_id, args.new_test_suite)
