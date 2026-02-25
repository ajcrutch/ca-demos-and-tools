# Test Suite Management Tool

This tool allows you to **export** existing test suites (including their examples and assertions) to a JSON file and **import** them into the same or a different Prism database instance.

This is useful for:
*   Backing up test suites.
*   Moving test suites between environments (e.g., from Development to Production).
*   Duplicating test suites for testing purposes.

## Prerequisites

1.  **Environment Setup**: Ensure you are in the project root and your virtual environment is activated.
    ```bash
    source .venv/bin/activate
    ```
2.  **Database Connection**: The script uses the `DATABASE_URL` from your `.env` file. Ensure this is set correctly to point to the desired database.
    ```bash
    # Example .env
    DATABASE_URL=postgresql://user:pass@localhost:5432/prism
    ```

## Usage

 The script is located at `scripts/manage_test_suites.py`.

### 1. Exporting a Test Suite

To export a test suite, you need its ID. You can find the ID by checking the `test_suites` table in your database.

**Command:**
```bash
python scripts/manage_test_suites.py export --id <TEST_SUITE_ID> --output <OUTPUT_FILE.json>
```

**Example:**
```bash
python scripts/manage_test_suites.py export --id 11 --output ilhc_suite_backup.json
```
*   **--id**: The integer ID of the test suite you want to export.
*   **--output**: The path where the JSON file will be saved.

### 2. Importing a Test Suite

To import a test suite from a JSON file.

**Command:**
```bash
python scripts/manage_test_suites.py import --input <INPUT_FILE.json> [--new-name "New Suite Name"]
```

**Example (Keep original name):**
```bash
python scripts/manage_test_suites.py import --input ilhc_suite_backup.json
```

**Example (Rename during import):**
```bash
python scripts/manage_test_suites.py import --input ilhc_suite_backup.json --new-name "ILHC Suite (Staging)"
```
*   **--input**: The path to the JSON file you want to import.
*   **--new-name** (Optional): A new name for the suite. If not provided, the script uses the name found in the JSON file.

## Data Handling

*   **Structure**: The tool preserves the full hierarchy: `Test Suite` -> `Examples` -> `Assertions`.
*   **IDs**:
    *   New database IDs are *always* generated for the imported Suite, Examples, and Assertions.
    *   The `logical_id` for Examples is currently preserved from the export file. If you are importing into the same database and strict uniqueness is required for `logical_id`, this might need adjustment, but currently, it is a non-unique field in the schema.
*   **Tags & Metadata**: All tags, descriptions, and archive statuses are preserved.

## Troubleshooting

*   **"psycopg2 is not installed"**: Run `pip install psycopg2-binary`.
*   **"DATABASE_URL not set"**: Check your `.env` file exists and has the variable set.
*   **"Test suite with ID X not found"**: Verify the ID exists in the database you are connected to.
