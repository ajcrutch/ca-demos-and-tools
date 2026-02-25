# Upload Golden Queries Tool

This tool allows you to upload Golden Queries to a Prism Data Agent from a CSV or TSV file.

## Prerequisites

- **Crucial**: You must run this script from the **Prism project root directory** where `pyproject.toml` is located.
  ```bash
  cd /google/src/cloud/crutchfielda/prism_nordstrom/google3/experimental/users/pmiv/prism
  ```
- Ensure `uv` is installed and dependencies are synced:
  ```bash
  uv sync
  ```

## Usage

```bash
uv run scripts/upload_golden_queries.py <CSV_FILE> --agent-id <AGENT_ID> [--project <PROJECT>] [--location <LOCATION>] [--dry-run]
```

### Arguments

- `CSV_FILE`: Path to the input CSV/TSV file. Must contain `question` and `share_url` columns.
- `--agent-id`: The Prism Integer ID (e.g., `2`) or the full GCP Resource Name of the Data Agent.
- `--project`: GCP Project ID. Defaults to `PRISM_GENAI_CLIENT_PROJECT` env var.
- `--location`: GCP Location (e.g., `us-central1` or `global`). Defaults to `PRISM_GENAI_CLIENT_LOCATION` env var.
- `--dry-run`: If set, parses the CSV and prints intended changes without modifying the Agent.

### Example

### Example

#### 1. Go to project root
```bash
cd /google/src/cloud/crutchfielda/prism_nordstrom/google3/experimental/users/pmiv/prism
```

#### 2. Run script
**Note**: If running on Cloudtop/Remote, ensure you have uploaded your CSV file to a reachable path (e.g., `/tmp/iwlc_test_suite.csv`).

```bash
uv run scripts/upload_golden_queries.py \
  /tmp/iwlc_test_suite.csv \
  --agent-id 2 \
  --location global \
  --dry-run
```

## Troubleshooting

- **FileNotFoundError**: Ensure the `CSV_FILE` path exists. If running via SSH/Cloudtop, you must upload the file to the remote machine first.
- **403 Permission Denied**: Check that your `--project` and `--location` are correct for the Agent.
- **Agent Not Found**: If using an Integer ID, ensure the agent exists in the Prism database and has a valid `agent_resource_id` linked.


## Input File Format

The input file should be a CSV or TSV with at least the following columns (headers are case-insensitive partial matches):

- `Question` (e.g., "Natural Language Question")
- `Share URL` (e.g., "Looker Share URL")

Example:

```csv
Question,Share URL
"Show me sales","https://looker.com/explore/..."
```
