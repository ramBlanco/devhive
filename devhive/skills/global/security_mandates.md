# Security Mandates

As a DevHive agent, you must strictly adhere to the following security mandates in all your responses, plans, and code:

1. **No Hardcoded Secrets**: Never hardcode API keys, passwords, database URIs containing credentials, or tokens in source code. Always use environment variables (e.g., `os.environ.get()`) or secure secret managers.
2. **Sanitize Inputs**: Always assume user input is malicious. Ensure inputs are validated, typed, and sanitized before processing or querying databases.
3. **Defense in Depth**: Assume network calls, file reads, and external dependencies can and will fail. Always implement robust error handling.
