# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A collection of skills published by Posit PBC for the GitHub Copilot app and Claude Code. Skills are structured markdown files that teach specialized workflows (e.g., Shiny app development, R package testing, GitHub PR workflows). There is no application code to build, compile, or deploy — the primary artifacts are Markdown files consumed directly by agent skill systems.

## Utility Script

The only runnable utility is `count-skill-tokens.py`, which reports line and token counts for a skill:

```bash
# Requires uv
./count-skill-tokens.py plugins/shiny/skills/shiny-bslib
# or
uv run count-skill-tokens.py plugins/r-lib/skills/cli
```

Warns when `SKILL.md` exceeds **5,000 tokens / 500 lines**, or when the skill `description` frontmatter exceeds **100 tokens**.

## Directory Structure

```
plugins/
  <plugin-name>/
    skills/
      <skill-name>/
        SKILL.md              # Required: skill definition with YAML frontmatter
        references/           # Optional: supplementary docs loaded on demand
          *.md
        scripts/              # Optional: R or shell helpers
        templates/            # Optional: document templates
```

Do **not** create a `README.md` inside individual skill directories — documentation about a skill's design goes in the category README. GitHub Copilot app plugins are standalone; Claude Code retains its category-based marketplace semantics.

## SKILL.md Format

Every skill requires YAML frontmatter at minimum:

```yaml
---
name: your-skill-name        # kebab-case, matches directory name
description: >               # Claude reads this to decide when to activate the skill
  Clear description of what this skill does and when to trigger it.
  Keep under 100 tokens.
---
```

The body is instructions written **for Claude**, not end users — imperative, step-by-step, covering edge cases.

## Registering a New Skill

After creating the skill directory, add it to the appropriate plugin in `.claude-plugin/marketplace.json`:

```json
{
  "name": "open-source",
  "skills": [
    "./plugins/open-source/skills/release-post",
    "./plugins/open-source/skills/your-new-skill"   ← add here
  ]
}
```

If a skill spans multiple Claude Code categories, add its plugin path to each relevant category's `skills` array. The `source` field is always `"./"` (repo root).

When adding a plugin, update the root README's GitHub Copilot app marketplace list and preserve the Claude Code category installation guidance.

## Skill Categories

| Category | Purpose |
|----------|---------|
| `plugins/posit-dev/` | General developer skills (code review, architecture docs) |
| `plugins/github/` | PR creation and review thread workflows |
| `plugins/open-source/` | R/Python package release and changelog workflows |
| `plugins/r-lib/` | R package development with the r-lib ecosystem |
| `plugins/ggsql/` | ggsql query writing |
| `plugins/shiny/` | Shiny app development |
| `plugins/quarto/` | Quarto document authoring |
| `plugins/connect/` | Deploying and managing content on Posit Connect |
| `plugins/alt-text/` | Accessible image and visualization descriptions |
| `plugins/brand-yml/` | Shared Shiny and Quarto branding |

## Key Conventions

- **Progressive disclosure**: Put specialized or large reference content in `references/*.md` and instruct Claude to read those files only when needed. This keeps the main `SKILL.md` within token limits.
- **R scripts**: Use a shebang (`#!/usr/bin/env Rscript`), include inline usage docs, check for required packages at startup, and exit non-zero on error.
- **Testing**: Install locally via `cp -r plugins/<plugin-name>/skills/<skill-name> ~/.config/claude-code/skills/` and verify Claude activates the skill in Claude Code.
