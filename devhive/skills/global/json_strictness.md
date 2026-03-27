# JSON Strictness

When your output format is specified as JSON:

1. **Raw JSON Only**: Output ONLY valid, parseable JSON. 
2. **String Escaping**: Be extremely careful with string escaping inside JSON values. Use standard JSON escapes for quotes (`\"`), newlines (`\n`), etc.
3. **No Markdown Wrapping**: Unless explicitly asked to wrap JSON in ````json ... ```` blocks, provide the raw JSON string directly.
