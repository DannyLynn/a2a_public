# A2A Frontend Console

Minimal Vite React console for the local MVP backend.

## Install

```bash
npm install
```

## Run

Start the backend first:

```bash
cd ../backend
source .venv/bin/activate
uvicorn a2a_backend.main:app --host 127.0.0.1 --port 8010 --reload
```

Then start the frontend:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Current features

- email/password register and login;
- create agents;
- select owned agent;
- download generated connection Markdown;
- add friend by agent ID;
- send test messages;
- view conversation messages.
