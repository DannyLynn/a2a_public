# Next Session Checklist

Use this checklist when resuming development.

## Repo setup

```bash
cd /Users/mac/Desktop/claude_work/a2a_network
git status
```

## Validate current public files

```bash
python3 -m py_compile sdk/python/a2a/client.py sdk/python/a2a/types.py examples/python-echo-agent/main.py
```

## Before pushing to GitHub

1. Check for real secrets:

```bash
grep -R "sk_live\|sk_test\|password\|token" . --exclude-dir=.git
```

2. Review changed files:

```bash
git status --short
git diff
```

3. Commit only public files.

## Next product task

Build the local backend MVP first.

Minimum success test:

```text
1. Create two agents
2. Add them as friends
3. Run two SDK echo agents
4. Send a message from A to B
5. B receives and replies
6. A receives reply
7. Web console shows messages and statuses
```
