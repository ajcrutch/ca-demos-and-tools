import argparse
from datetime import datetime
import json
import os
import sys
from dotenv import load_dotenv

try:
  import psycopg2
  from psycopg2.extras import RealDictCursor, Json
except ImportError:
  print(
      "Error: psycopg2 is not installed. Please install it with 'pip install"
      " psycopg2-binary'"
  )
  sys.exit(1)


def get_db_connection():
  """Establishes connection to the PostgreSQL database."""
  load_dotenv()
  db_url = os.environ.get("DATABASE_URL")
  if not db_url:
    print(
        "Error: DATABASE_URL environment variable is not set. Check your .env"
        " file."
    )
    sys.exit(1)

  try:
    conn = psycopg2.connect(db_url)
    return conn
  except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)


def export_test_suite(suite_id: int, output_file: str):
  """Exports a test suite and all its examples and assertions to a JSON file."""
  conn = get_db_connection()
  try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
      # 1. Fetch Test Suite
      cur.execute(
          "SELECT name, description, tags, is_archived FROM test_suites WHERE"
          " id = %s",
          (suite_id,),
      )
      suite = cur.fetchone()
      if not suite:
        print(f"Error: Test suite with ID {suite_id} not found.")
        return

      # 2. Fetch Examples
      cur.execute(
          """
                SELECT id, logical_id, question, is_archived 
                FROM examples 
                WHERE test_suite_id = %s 
                ORDER BY id
            """,
          (suite_id,),
      )
      examples = cur.fetchall()

      # 3. Fetch Assertions for each example
      export_examples = []
      for ex in examples:
        cur.execute(
            """
                    SELECT type, weight, params, is_archived 
                    FROM assertions 
                    WHERE example_id = %s 
                    ORDER BY id
                """,
            (ex["id"],),
        )
        assertions = cur.fetchall()

        ex_data = {
            "logical_id": ex["logical_id"],
            "question": ex["question"],
            "is_archived": ex["is_archived"],
            "assertions": assertions,
        }
        export_examples.append(ex_data)

      # Construct final JSON structure
      export_data = {
          "version": "1.0",
          "exported_at": datetime.now().isoformat(),
          "suite": suite,
          "examples": export_examples,
      }

      with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)

      print(f"Successfully exported test suite {suite_id} to {output_file}")
      print(f"  - Suite Name: {suite['name']}")
      print(f"  - Examples: {len(export_examples)}")

  except Exception as e:
    print(f"Error during export: {e}")
  finally:
    conn.close()


def import_test_suite(input_file: str, new_name: str = None):
  """Imports a test suite from a JSON file."""
  if not os.path.exists(input_file):
    print(f"Error: Input file {input_file} not found.")
    return

  try:
    with open(input_file, "r", encoding="utf-8") as f:
      data = json.load(f)

    suite_data = data.get("suite")
    if not suite_data:
      print("Error: Invalid JSON format. Missing 'suite' key.")
      return

    conn = get_db_connection()
    conn.autocommit = False
    try:
      with conn.cursor() as cur:
        # 1. Create Test Suite
        name_to_use = new_name if new_name else suite_data["name"]
        print(f"Importing suite: '{name_to_use}'...")

        cur.execute(
            """
                    INSERT INTO test_suites (name, description, tags, is_archived)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """,
            (
                name_to_use,
                suite_data.get("description", ""),
                Json(suite_data.get("tags", {})),
                suite_data.get("is_archived", False),
            ),
        )
        new_suite_id = cur.fetchone()[0]
        print(f"  - Created Suite ID: {new_suite_id}")

        # 2. Create Examples and Assertions
        examples_data = data.get("examples", [])
        for ex in examples_data:
          # Insert Example
          cur.execute(
              """
                        INSERT INTO examples (test_suite_id, logical_id, question, is_archived)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """,
              (
                  new_suite_id,
                  ex.get(
                      "logical_id"
                  ),  # We can reuse strict logical_id or gen_random_uuid in db if we wanted new ones.
                  # For import/export, keeping logical_id allows mapping back?
                  # If unique constraint exists on logical_id globally, this might fail?
                  # examples table usually has unique logical_id.
                  # Let's assume we might need new logical_id if we match exactly?
                  # If import is into *another* instance, reuse is fine.
                  # If import is into *same* instance (duplication), logical_id must be unique.
                  # Let's generate NEW logical_id to be safe for same-db import.
                  ex["question"],
                  ex.get("is_archived", False),
              ),
          )
          # Actually, wait. logical_id is unique per example.
          # If we are importing into the same DB, we MUST generate a new logical_id.
          # If we export/import to a NEW db, we could keep it.
          # Safe bet: Let DB generate it if we pass UUID, or we generate it.
          # Let's assume we want a COPY, so new ID.

          # Update: The query above sends 'logical_id' value.
          # If we are duplicating within the same DB, this will fail if unique constraint exists.
          # Let's perform a check or just always generate new random uuid for safety?
          # "logical_id" helps track the 'same' semantic example across environments.
          # Ideally, we want to KEEP it if moving to a new environment (Prod -> Stage).
          # But if we are testing (Prod -> Prod duplicate), we need new.
          # For this tool, user didn't specify duplication strategy.
          # Use Case: "Import into ANOTHER instance".
          # So keeping logical_id is actually BETTER for tracking lineage.
          # Logic: Try insert with logical_id. If fails (collision), log warning or fail?
          # Let's try to keep it. NOTE: schema might not enforce unique logical_id?
          # Let's look at Example model? "logical_id: ... unique=True/index=True?"
          # Model code says: unique=False (just `nullable=False, index=True`).
          # Checking `example.py`: `logical_id: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String, nullable=False, index=True)`
          # No explicit unique constraint visible in the python code shown earlier (SQLAlchemy usually explicit).
          # So it might be fine.

          # Wait, let's just use the value from JSON.

          # Retrieve newly created ID
          new_example_id = cur.fetchone()[0]

          # 3. Create Assertions
          assertions_data = ex.get("assertions", [])
          for assertion in assertions_data:
            cur.execute(
                """
                            INSERT INTO assertions (example_id, type, weight, params, is_archived)
                            VALUES (%s, %s, %s, %s, %s)
                        """,
                (
                    new_example_id,
                    assertion["type"],
                    assertion["weight"],
                    Json(assertion["params"]),
                    assertion.get("is_archived", False),
                ),
            )

        conn.commit()
        print(f"Successfully imported {len(examples_data)} examples.")

    except Exception as e:
      conn.rollback()
      print(f"Error during import: {e}")
      print("Transaction rolled back.")
  finally:
    conn.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Manage Test Suites (Export/Import)"
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  # Export Command
  export_parser = subparsers.add_parser(
      "export", help="Export a test suite to JSON"
  )
  export_parser.add_argument(
      "--id", type=int, required=True, help="ID of the test suite to export"
  )
  export_parser.add_argument(
      "--output", type=str, required=True, help="Output JSON file path"
  )

  # Import Command
  import_parser = subparsers.add_parser(
      "import", help="Import a test suite from JSON"
  )
  import_parser.add_argument(
      "--input", type=str, required=True, help="Input JSON file path"
  )
  import_parser.add_argument(
      "--new-name", type=str, help="Optional new name for the imported suite"
  )

  args = parser.parse_args()

  if args.command == "export":
    export_test_suite(args.id, args.output)
  elif args.command == "import":
    import_test_suite(args.input, args.new_name)
