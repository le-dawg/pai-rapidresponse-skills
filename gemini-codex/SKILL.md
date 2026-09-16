---
name: gemini-codex
description: Use when the user wants to hand work from the current harness to Codex, Claude, Antigravity, or GitHub Copilot using canonical `:<target>` syntax or compatibility `handoff <target>` syntax.
user-invocable: true
canonical: ":<target> [args...] [prompt...]"
compatibility: "handoff <target> [args...] [prompt...]"
source_policy: source-agnostic
source_inference_behavior: ask-once-and-stop
continuation_mode: true
copilot_model_required: true
copilot_model_missing_behavior: ask-and-stop
copilot_confirmed_working_models:
  - auto
  - gpt-5.4
antigravity_model: gemini-3.1-pro
copilot_known_models:
  - auto
  - claude-sonnet-4.6
  - claude-sonnet-4.5
  - claude-haiku-4.5
  - gpt-5.4
  - gpt-5.3-codex
  - gpt-5.4-mini
  - gpt-5-mini
  - gpt-4.1
  - claude-sonnet-5
  - gemini-3.1-pro-preview
  - gemini-3.5-flash
  - gemini-3.6-flash
  - gemini-3.7-flash
  - gpt-5.6-luna
  - gpt-5.6-terra
  - grok-4.5
  - grok-4.6
  - kimi-k2.7-code
  - kimi-k3
  - mai-code-1.1-flash
  - mai-code-1-flash-picker
internal_routing_object:
  source: inferred current harness by default
  target: destination harness key
  prompt: explicit trailing prompt or generated continuation prompt
  model: destination model if supplied or defaulted
  cwd: working directory or repo context
  resume_mode: continuation or fresh
  extra_flags: destination-specific passthrough options
handoff_capsule:
  goal: top-level objective being handed off
  mode: research|implement|review
  constraints: binding limits, invariants, and policy constraints
  files: relevant paths, repos, or artifacts
  done_so_far: progress summary for continuation handoffs
  open_questions: unresolved items the destination harness should answer
  verification_status: current evidence and what has already been checked
  preferred_model: destination-model preference when relevant
  preferred_effort: reasoning or effort preference when relevant
  resume_hint: explicit continuation/resume guidance for the destination
  tool_classes_needed: neutral task/tool categories needed to continue
action_vocabulary:
  - read
  - edit
  - search_web
  - dispatch_subagent
  - track_tasks
  - resume_session
  - run_verification
---

# General handoff router

This skill is installed under the exact name `gemini-codex` so slash invocation resolves consistently in Claude, Codex, and other harnesses that expose the frontmatter `name` as the user-facing command.

## Supported destinations
- `codex`
- `claude`
- `antigravity`
- `copilot`

## Explicit Codex credential and model instructions

Codex credential and model policy:

- If Codex is called with no specific model, use Codex's default model and do not pass a model option.
- If a specific model is mentioned and it is exactly `gpt-5.4`, use that model without applying `TEMPKEY`.
- If a specific model is mentioned and it is anything other than exactly `gpt-5.4`, use the `TEMPKEY` environment variable as the Codex credential and preserve the requested model exactly.
- `TEMPKEY` means the name of the environment variable whose value must be supplied to the Codex process as `OPENAI_API_KEY`; never ask for, print, log, or embed its secret value.
- If `TEMPKEY` is unset or empty when required, fail clearly and do not silently use local login or another credential.
- Scope the credential override to the delegated Codex process only; do not modify global shell configuration or persist the secret.
- Treat model placeholders in prose such as `<MODEL>` or `ABC` as placeholders, never as literal model names. Only a concrete model explicitly mentioned by the user counts as a specific model.

### Normalized example

```yaml
source: inferred current harness
 target: codex
 model: <user-supplied model identifier, or omitted when no model was specified>
 auth_env: TEMPKEY only when a specific model was named and it was not gpt-5.4
 prompt: <remaining user request>
```

## Router rules

- Accept canonical `:<target>` syntax.
- Accept compatibility `handoff <target>` syntax.
- Normalize both forms into the same internal routing object.
- Infer the source harness automatically by default.
- If source cannot be inferred confidently, ask once and stop.
- If the user provides no trailing prompt, the default behavior should be continuation handoff.
- If the user provides trailing text, treat it as an explicit handoff prompt.
- If destination is unavailable on the system, fail clearly and name what is missing.
- If the target is unknown, fail clearly and list the supported destinations.
- If the source harness is unsupported, fail clearly and ask for a supported environment.
- If destination configuration or authentication is missing, fail clearly and name what is missing.
- If the requested feature combination is unsupported for the destination, fail clearly instead of guessing.

### Examples
- `:codex`
- `:claude continue from current task context`
- `:antigravity investigate this issue`
- `:copilot --model gpt-5 review this implementation`
- `handoff codex review this repository`

## Destination adapter contracts

- Do not invent destination model aliases.

## Codex adapter
- Use destination-native Codex invocation patterns.
- Support fresh execution and resume-oriented continuation.
- Model is optional.
- Example: `codex exec "review this repository"`

## Claude adapter
- Use destination-native Claude invocation patterns.
- Preserve continuation context where possible.
- Model is optional for Claude itself.
- When the request delegates onward to Codex, apply the Codex credential and model policy exactly as described above.
- Example: `claude "continue from current task context"`
- With no model: `codex exec "<prompt>"`
- With `gpt-5.4`: `codex exec --model gpt-5.4 "<prompt>"`
- With any other explicitly named model: `OPENAI_API_KEY="$TEMPKEY" codex exec --model <user-supplied-model> "<prompt>"`

## Antigravity adapter
- Use destination-native Antigravity invocation patterns.
- Antigravity defaults to `gemini-3.1-pro` only when Antigravity itself is the target.
- If `--model` is omitted, default to `gemini-3.1-pro`.
- If a model is supplied, respect it.
- When the request delegates onward to Codex, do not substitute the Antigravity default; apply the Codex credential and model policy exactly as described above.
- Example: `antigravity "investigate this issue"`
- With no model: `codex exec "<prompt>"`
- With `gpt-5.4`: `codex exec --model gpt-5.4 "<prompt>"`
- With any other explicitly named model: `OPENAI_API_KEY="$TEMPKEY" codex exec --model <user-supplied-model> "<prompt>"`

## Copilot adapter
- Use destination-native Copilot invocation patterns.
- Copilot requires `--model` when Copilot itself is the target.
- If `--model` is missing, stop and ask the user.
- Do not guess the model.
- When the request delegates onward to Codex, preserve Codex `auth_env` and `model`; do not reinterpret the user-supplied model as a Copilot model.
- Example: `copilot --model gpt-5.4 "review this implementation"`
- With no model: `codex exec "<prompt>"`
- With `gpt-5.4`: `codex exec --model gpt-5.4 "<prompt>"`
- With any other explicitly named model: `OPENAI_API_KEY="$TEMPKEY" codex exec --model <user-supplied-model> "<prompt>"`

### Copilot model selection

The following model IDs were listed by the local GitHub Copilot CLI runtime on 2026-08-24:

- `auto`
- `claude-sonnet-4.6`
- `claude-sonnet-4.5`
- `claude-haiku-4.5`
- `gpt-5.4`
- `gpt-5.3-codex`
- `gpt-5.4-mini`
- `gpt-5-mini`
- `gpt-4.1`
- `claude-sonnet-5`
- `gemini-3.1-pro-preview`
- `gemini-3.5-flash`
- `gemini-3.6-flash`
- `gemini-3.7-flash`
- `gpt-5.6-luna`
- `gpt-5.6-terra`
- `grok-4.5`
- `grok-4.6`
- `kimi-k2.7-code`
- `kimi-k3`
- `mai-code-1.1-flash`
- `mai-code-1-flash-picker`

Confirmed live on this machine with a non-interactive ACK prompt:

- `auto`
- `gpt-5.4`

If the user does not know which Copilot model to choose, show this list and ask them to select one.

## Portable handoff capsule

Use a portable handoff capsule to carry continuation state between harnesses.

- `goal`
- `mode`
- `constraints`
- `files`
- `done_so_far`
- `open_questions`
- `verification_status`
- `preferred_model`
- `preferred_effort`
- `resume_hint`
- `tool_classes_needed`

The capsule lets the router stay source-agnostic while adapters render destination-native commands or prompts.

## Neutral action vocabulary

Use a neutral internal action vocabulary rather than encoding one CLI's worldview directly.

- `read`
- `edit`
- `search_web`
- `dispatch_subagent`
- `track_tasks`
- `resume_session`
- `run_verification`

Adapters translate this neutral vocabulary into destination-native actions.

## Failure behavior

Fail clearly, briefly, and actionably in these cases:

- unknown destination target
- unsupported source harness
- missing destination executable
- missing destination configuration or authentication
- missing required model for Copilot
- ambiguous source inference
- unsupported destination feature combination

Do not silently guess or degrade required behavior.
