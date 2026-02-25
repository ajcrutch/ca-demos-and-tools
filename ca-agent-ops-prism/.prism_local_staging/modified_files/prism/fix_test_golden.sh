sed -i '' 's/view="view1"/explore="view1"/g' tests/services/test_golden_queries.py
sed -i '' 's/view="view2"/explore="view2"/g' tests/services/test_golden_queries.py
sed -i '' 's/\["view"\]/\["explore"\]/g' tests/services/test_golden_queries.py
