# Open Questions

These are intentionally unresolved and should be decided when implementation starts.

## Backend stack

Options:

1. FastAPI + SQLAlchemy;
2. Node.js + Express/NestJS;
3. Next.js full-stack.

Recommendation: FastAPI for MVP because SDK/examples are Python-first.

## Session strategy

Options:

1. HTTP-only cookie sessions for browser;
2. JWT access tokens;
3. simple bearer token for local MVP.

Recommendation: HTTP-only cookies for web console, bearer API keys for SDK.

## Database

Options:

1. SQLite for local MVP;
2. PostgreSQL immediately.

Recommendation: SQLite for fastest local development, PostgreSQL before external testing.

## Public repo vs private app repo

This repository can hold public SDK/docs/templates. The actual backend/frontend can either be added here while early, or moved to a private repo later if the product should not be public.

## GitHub push access

The repository was cloned successfully over HTTPS. Push access has not been confirmed. GitHub CLI is not installed in the current environment. If HTTPS push prompts fail, use SSH key auth or a GitHub personal access token.
