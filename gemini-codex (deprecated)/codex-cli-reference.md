# Codex CLI reference

This document preserves Codex-specific command guidance as reference material only.

It is not an installable Gemini skill entrypoint.

Use `skills/gemini-codex/SKILL.md` for cross-harness routing between Codex, Claude, Antigravity, and GitHub Copilot.

## Before running Codex
1. Verify Codex CLI is installed with `codex --version`.
2. If Codex is missing, stop and ask the user to install it.
3. Check authentication with `codex login status` if there is any doubt.
4. If Codex is not authenticated, ask the user to either:
   - run `codex` and choose **Sign in with ChatGPT**, or
   - pipe an API key into `codex login --with-api-key`
5. Do not assume Gemini authentication also authenticates Codex.

## Choosing the right command
- Use `codex exec` for non-interactive delegation.
- Use `codex review` when the user specifically wants a review of repo changes.
- Use `codex resume` to continue an interactive Codex session.
- Use `codex exec resume` to continue a non-interactive exec session.

## Recommended command patterns

### One-shot task in a repository
```bash
codex exec -C /absolute/path/to/repo "<task prompt>"
```

### Structured event output for automation
```bash
codex exec -C /absolute/path/to/repo --json "<task prompt>"
```

`--json` emits JSONL events, not a single JSON object.

### Continue the latest exec session
```bash
codex exec resume --last "<follow-up prompt>"
```

### Continue a specific exec session
```bash
codex exec resume <session-id> "<follow-up prompt>"
```

### Continue the latest interactive session
```bash
codex resume --last
```

### Continue a specific interactive session with a new prompt
```bash
codex resume <session-id> "<follow-up prompt>"
```

### Review changes
```bash
codex review --uncommitted "<review instructions>"
```

or

```bash
codex review --base main "<review instructions>"
```

## Models
- Codex exposes `-m` / `--model <MODEL>`.
- Only pass `--model` when the user explicitly wants a specific model or already uses one.
- If the user does not care, let Codex use its configured default.
- Do not invent Gemini-style model aliases for Codex.

## Reasoning and thinking controls
- Do not use `model_reasoning_effort`.
- I did not verify a dedicated Codex CLI flag for reasoning effort or thinking budget.
- If the user asks for reasoning tuning, explain that only generic config overrides were verified (`-c key=value`), so you should not guess at undocumented Codex config keys.

## Working directory and repo boundaries
- Prefer `-C /absolute/path/to/repo` instead of shelling into the repo first.
- Use `--skip-git-repo-check` only when the user explicitly wants Codex to run outside a Git repo.
- Use `--add-dir <DIR>` only when Codex needs extra writable directories beyond the main workspace.

## Sandboxing and approvals
- Codex supports `--sandbox` / `-s` with these verified modes:
  - `read-only`
  - `workspace-write`
  - `danger-full-access`
- Codex supports `--ask-for-approval` / `-a` with these verified modes:
  - `untrusted`
  - `on-request`
  - `never`
- `on-failure` exists but is deprecated; prefer `on-request` or `never`.
- Never use `--dangerously-bypass-approvals-and-sandbox` unless the user explicitly asks for it and the environment is already externally sandboxed.

## Non-interactive output handling
- For automation, prefer `codex exec`.
- Use `--json` when you need structured machine-readable event output.
- Use `-o <FILE>` only when you need Codex to write the final assistant message to a file.
- If the task prompt is long or generated from another tool, `codex exec -` can read it from stdin.

## Error handling
- If `codex --version` fails, stop and tell the user Codex CLI is unavailable.
- If authentication is missing, stop and ask the user to sign in or configure API-key login.
- If sandbox or approval settings block the run, explain which verified flags could change the behavior and ask before retrying.
- If the user asks for an unverified Codex feature, state that the feature was not verified and fall back to a documented command.

## Critical evaluation of Codex output
- Treat Codex as a collaborator, not an authority.
- If Codex conflicts with Gemini or local evidence, compare the claims against docs, code, or command output before trusting it.
- Summarize the result for the user in plain language, including any relevant caveats about auth, sandboxing, approvals, or session reuse.
