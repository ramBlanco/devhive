# Non-Functional Requirements (NFR) Checklist

When exploring and analyzing a new feature request, you MUST actively consider and document Non-Functional Requirements (NFRs). Do not just focus on the happy path. 

Always evaluate and include considerations for:
1. **Latency/Performance**: Are there strict response time expectations? Will this feature slow down the app?
2. **Concurrency/Scale**: How will this behave if 1,000 users do it at the exact same time?
3. **Data Retention & Privacy**: Does this feature generate PII (Personally Identifiable Information)? How long do we need to store it?
4. **Accessibility (a11y)**: If there is a UI component, does it need to support screen readers or keyboard navigation?
5. **Observability**: How will we know if this feature is broken in production? What metrics/logs must be captured?
