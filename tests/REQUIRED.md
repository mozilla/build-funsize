We need a few tests in the following categories:

Unit-Tests:

- All of flask
- core.py
    - get_complete_mar
    - build_partial_mar
    - generate_partial_mar
- tools.py

Regression-Tests:

- Cache concurrency, where triggering multiple partial MARs to/from the same 
  dst/src dont cause cache collision errors
- 

Integration Tests:

- Test to make sure that the requests are always idempotent
- Test to make sure we are actually getting cache hits (both complete MARs and partials)
