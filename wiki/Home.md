# A2A Network Wiki

This local wiki records the current product and engineering context so future development can resume quickly.

## Current decision summary

- MVP uses email/password login.
- Agents connect through SDK-first polling, not webhook-first.
- Webhook is a future advanced integration mode.
- Users create agents in the web console.
- Platform generates `agent_id` and `api_key`.
- Platform generates user-specific Markdown instructions from public templates.
- Public GitHub stores generic SDK/docs/templates only.
- Real secrets must stay out of GitHub.

## Important docs

- [Product Overview](Product-Overview.md)
- [Development Notes](Development-Notes.md)
- [Next Session Checklist](Next-Session-Checklist.md)
- [Open Questions](Open-Questions.md)

## Main implementation docs

- [Architecture](../docs/architecture.md)
- [Backend API Design](../docs/backend-api-design.md)
- [Database Schema](../docs/database-schema.md)
- [Frontend Product Design](../docs/frontend-product-design.md)
- [SDK Design](../docs/sdk-design.md)
- [Roadmap](../docs/roadmap.md)
