# Looker Assertions Upload Tool

## Overview
`upload_looker_assertions.py` is a specialized database extraction tool for the Prism backend. It takes a TSV (tab-separated values) file containing a sequence of questions and Looker "expanded share" URLs. It connects directly to the PostgreSQL database to automatically convert these URLs into categorized testing assertions.

## Prerequisites
1. **Python Environment**: Ensure you are in the Prism virtual environment.
   ```bash
   cd /Users/crutchfielda/prism_local/prism/ && source .venv/bin/activate
   ```
2. **Database Credentials**: A `.env` file at the root of the project containing `DATABASE_URL`.
   ```bash
   DATABASE_URL="postgresql://crutchfielda:@localhost:5432/prism?host=/tmp"
   ```
3. **Input Data**: A TSV file with a `question` and `expanded share` column.

## Usage
Run the script passing the path to the TSV file. You must also supply a Test Suite instruction.

**Create a new test suite:**
```bash
python scripts/upload_looker_assertions.py path/to/questions.tsv --new-test-suite "My New Test Suite"
```

**Use an existing test suite:**
```bash
python scripts/upload_looker_assertions.py path/to/questions.tsv --test-suite-id 15
```

## Generated Assertions (V2)
The script splits the expanded share URL into multiple, granular elements. For a single question, multiple `LOOKER_QUERY_MATCH` assertions are generated and tied to the corresponding `example_id`.

For every URL provided, the script automatically parses and generates:
1. **Full Assertion:** An assertion containing all fields, filters, sorts, and limits.
2. **Field Assertions:** For every `field` parsed, an individual assertion asserting just that `field`.
3. **Filter Assertions:** For every `filter`, an individual assertion asserting just that particular filter expression.
4. **Sort Assertions:** For every `sort` parameter, an individual assertion.
5. **Limit Assertion:** A dedicated assertion if a row `limit` is present.

### Example Database Record
```json
// One of the parsed sub-assertions generated from a URL
{
  "original_assertion_id": null, 
  "reasoning": null, 
  "params": {
    "model": "merch-ieh", 
    "explore": "merch_holiday_inv_trans_store", 
    "fields": [
      "cv_merch_fiscal_metrics_holiday.op_gmv_retail_amt"
    ], 
    "filters": null, 
    "sorts": null, 
    "limit": null
  }
}
```
