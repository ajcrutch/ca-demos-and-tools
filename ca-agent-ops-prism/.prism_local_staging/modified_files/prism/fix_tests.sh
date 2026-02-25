sed -i '' 's/mock_proto_gq.looker_query.model = None/mock_proto_gq.looker_query.model = None\n  mock_proto_gq.looker_query.explore = None/g' tests/clients/test_gemini_data_analytics_client.py
sed -i '' 's/mock_proto_gq.looker_query.model = None/mock_proto_gq.looker_query.model = None\n  mock_proto_gq.looker_query.explore = None/g' tests/services/test_golden_queries.py
