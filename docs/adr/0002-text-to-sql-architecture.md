# 0002. Text-to-SQL Architecture for Boss Dashboard

Date: 2026-07-08

## Status

Accepted

## Context

We are building a "War Room" dashboard for executives (boss) to query logistics data using natural language (Text-to-SQL). The feature needs to be robust, secure, and demonstrate Forward Deployed Engineer (FDE) principles like transparency and error resilience.

## Decision

We have made four core architectural decisions during the design grilling session:

1. **Security & Scope (Whitelist approach)**: To prevent hallucinations or dangerous access, we will use SQLAlchemy to whitelist *only* the `bills_of_lading` table (and exclude internal tables like `bad_cases`). The LLM will only have access to a Read-Only schema slice.
2. **AI Execution (SQL Agent with ReAct)**: Instead of a fragile single-pass SQL chain, we will implement a LangChain SQL Agent. If the agent generates a SQL error, it will read the error log and self-correct, drastically improving the success rate.
3. **Data Visualization (Text + Markdown Table)**: The final output will be a smart natural language summary followed by a Markdown table. (Relying on the frontend `marked` + Tailwind Typography from ADR-0001 for rendering).
4. **Communication Protocol (SSE Streaming)**: We will use Server-Sent Events (SSE) via FastAPI's `StreamingResponse` and LangChain's `astream_events()`. We will stream both the agent's intermediate "Thought Process" (e.g., executing a query, handling an error) and the final summary to the frontend to build a highly transparent, FDE-style UI.

## Consequences

- **Pros**: High security, extreme fault tolerance, and a stunning "transparent UI" that builds executive trust.
- **Cons**: The backend implementation is more complex (requires asynchronous streaming of agent steps), and response times may be slightly longer (5-8 seconds) due to the ReAct loop.
