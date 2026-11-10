# Claude Code skill and subagent format (checked 2026-11-10)

Sources: https://code.claude.com/docs/en/skills and https://code.claude.com/docs/en/sub-agents

## Skills
- Project skill path: `.claude/skills/<skill-name>/SKILL.md`. Loaded in sessions in that repo.
- Frontmatter between `---` markers. All fields optional; `description` recommended. Unknown fields ignored silently.
- Fields used here: `name` (defaults to directory name; slash command name), `description` (what and when; key use case first; description + `when_to_use` truncated at 1,536 characters in the listing), `when_to_use` (extra trigger phrases), `argument-hint`.
- Other fields exist (`allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `paths`, `hooks`...). Not needed for this skill.
- Supporting files live in the skill directory and are referenced from SKILL.md with a note on what each contains and when to load it. Loaded only when needed.
- Keep SKILL.md under 500 lines. Once loaded it stays in context across turns. After auto-compaction, the first 5,000 tokens of each invoked skill are re-attached: so the most important rules go at the top of SKILL.md.
- Invocation: automatic when the description matches, or `/writers-room`.

## Subagents
- Project path: `.claude/agents/<name>.md`. Markdown with YAML frontmatter; body = system prompt.
- Required: `name`, `description`. Optional used here: `tools` (allowlist), `model` (`inherit` allowed).
- Fresh isolated context: does not see the conversation, prior skills, or files already read. Receives its own system prompt, the delegation message Claude writes, CLAUDE.md files, git status.
- Read-only: `tools: Read, Grep, Glob`.
- `skills` field preloads full skill content; not used, because the reviewer should load only review.md, anti-slop.md and the relevant lenses, not the whole workflow.
- Delegation is driven by `description`; can also be invoked by name or @-mention.

Design consequences
- SKILL.md: workflow and hard rules first (they survive compaction), pointers to reference files with "load when" notes.
- The main agent must pass the braintrust reviewer the file paths of the draft and the story bible, because the reviewer sees nothing else.
