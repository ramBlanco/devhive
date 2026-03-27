# Performance Bottleneck Detection

As the Auditor, verify the implementation for common architectural and code-level performance bottlenecks:

1. **N+1 Query Problem**: Does the code fetch a list of items and then query the database again for every single item in a loop? Require eager loading or batching.
2. **Missing Indexes**: If the code introduces new database queries with `WHERE`, `ORDER BY`, or `JOIN` clauses, verify that necessary database indexes have been proposed.
3. **Large In-Memory Processing**: Does the code attempt to load massive files or huge query results into memory all at once? Suggest generators, streams, or chunking.
4. **Blocking Calls**: In async environments, are there blocking synchronous I/O operations (like `time.sleep()` or sync `requests.get()`) that will stall the event loop?

If any of these are found, document them in your `missing_pieces` or `architecture_consistency` feedback.
