# Plan: Recreate Test Suite from Looker Regression `.txtpbs`

This plan outlines how to map the criteria in `regression.txtpbs` to Prism's `AssertionType` and how to programmatically generate the Test Suite.

## Mapping Logic

| `.txtpbs` Criteria Pattern | Prism Assertion Type | Parameters / Notes |
| :--- | :--- | :--- |
| "Date filter represents..." | `LOOKER_QUERY_MATCH` | Add to `filters` list. |
| "Selects fields..." | `LOOKER_QUERY_MATCH` | Add to `fields` list. |
| "Uses filter..." | `LOOKER_QUERY_MATCH` | Add to `filters` list. |
| "Has a limit X, by sort..." | `LOOKER_QUERY_MATCH` | Set `limit` and `sorts`. |
| "produces a line chart" | `CHART_CHECK_TYPE` | `value: "line"` |
| "uses dimension..." | `LOOKER_QUERY_MATCH` | Add to `fields` or `filters`. |
| "sorts by..." | `LOOKER_QUERY_MATCH` | Add to `sorts`. |
| "indicates in response..." | `AI_JUDGE` | Semantic check for response content. |
| "uses measure to represent..." | `AI_JUDGE` | Or `LOOKER_QUERY_MATCH` if field name is obvious. |

## Implementation Strategy

1.  **Parsing**: Use a regex or simple line-by-line parser to extract `text` (the question) and `criteria` from the `.txtpbs` file.
2.  **Mapping**: For each example:
    *   Create a `TestSuite` (if it doesn't exist).
    *   For each criterion, determine the best Prism `Assertion`.
    *   Group `LOOKER_QUERY_MATCH` criteria for the same example into a single assertion where possible, or keep them separate for granularity.
3.  **Generation Script**: A Python script in `sandbox/generate_suite.py` that:
    *   Reads the `.txtpbs`.
    *   Uses Prism's model schemas (via `pydantic`) to validate the objects.
    *   Uses a database session to insert the `TestSuite`, `Example`s, and `Assertion`s.

## Verification

*   Manually inspect a few generated Examples in the Prism UI.
*   Ensure Looker-specific fields are correctly populated in the `params` of `LookerQueryMatch`.
