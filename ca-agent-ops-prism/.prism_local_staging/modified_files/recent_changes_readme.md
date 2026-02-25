# Prism Core Backend: Custom Agent Integration Patch

This patch contains recent additions and modifications to the Prism Backend. The recent work focused on integrating custom, user-defined agent endpoints (Custom Agent APIs) with the Prism Evaluation platform.

## Key Changes and Files Included:

### Configuration:
- `.env`: Contains the DB connection strings and updated env vars.
- `README_upload_looker_assertions.md`: Updated documentation for local DB extraction tools.

### Backend/Services:
- `src/prism.egg-info/*` files (automatically generated after rebuilds)
- `src/prism/common/schemas/agent.py`: Extended agent schema definition to handle custom APIs.
- `src/prism/server/services/agent_service.py`: Updated logic for testing/calling external agents.
- `src/prism/server/services/custom_api_client.py`: Implementation of the actual custom API connector.
- `src/prism/server/services/execution_service.py`: Updates to testing logic, running golden queries through the custom APIs.

### UI Modifications:
- `src/prism/ui/callbacks/*`: Logic updates for creating/updating agent profiles.
- `src/prism/ui/pages/*`: Updated pages for choosing custom API models vs GCP models, displaying updated agent IDs, and parsing test suite suites.
- `src/prism/ui/constants.py`: New endpoints and identifiers for Custom Agents.

### Testing/Utilities:
- `tests/clients/test_gemini_data_analytics_client.py`: Updates for integration tests.
- `tests/services/test_golden_queries.py`: Tests for assertion evaluations.
- `fix_tests.sh`, `fix_test_golden.sh`: New scripts to handle updates/golden tests locally.

## Design Changes:
The app has been extended to allow Prism to define a "Custom" engine instead of strictly requiring Google Cloud Platform (GCP) or Gemini direct integrations. This enables flexibility for connecting any third-party model (e.g., custom deployed vector data models, different on-prem models) with the same Prism standard schema and frontend. 

## To Use / Setup:
1. Ensure your `.env` is properly configured with your database URL.
2. Ensure Custom Agent endpoints have an established API and test connection via the 'Test Connection' button in the updated UI.
3. Use `./scripts/setup_postgres.sh` (or `docker-compose up`) to ensure your database is running properly before testing.

