# CLAUDE.md

Notes for Claude Code working inside this repository. For the general skill
spec (frontmatter, directory layout, conventions), read [AGENTS.md](./AGENTS.md) —
this file only covers repo-local behaviors that agents need on top of the spec.

## Repo shape

- `skills/<kebab-case-name>/SKILL.md` — one skill per directory.
- `skills/<name>/references/` — long-form docs the skill pulls in on demand.
- `skills/<name>/scripts/` — automation the skill can invoke.
- `AGENTS.md` — canonical spec. Treat it as the source of truth over any
  loose conventions inferred from existing skills.

## Useful one-liners

```bash
# list skills
ls skills/

# show every SKILL.md's frontmatter
for f in skills/*/SKILL.md; do echo "### $f"; awk '/^---$/{c++; next} c==1' "$f"; done

# find all section headings across skills (spot structural drift)
grep -nE '^## ' skills/*/SKILL.md
```

## When creating a skill

Follow [AGENTS.md](./AGENTS.md) exactly — including the template headings
(`When to Apply`, `How It Works`, `Usage`, `References`). Don't invent
alternative heading names; structural consistency across skills is a
feature of this repo.

## When editing an existing skill

- Don't shorten the `description` frontmatter field — it's the only text an
  agent sees at startup when deciding whether to load the skill, so richer
  trigger phrases help discovery.
- Keep `SKILL.md` under ~500 lines; move detail into `references/`.
- If you rename a section heading, grep for anchor links first:
  `grep -rn '#section-name' .`
