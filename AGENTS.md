# AGENTS.md instructions for d:/project/cursor

## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file.

### Available skills
- data-analysis-agent: Data analysis and insight delivery for CSV/Excel/JSON/SQL. Use for data cleaning, EDA, statistical testing, metric design, experiment evaluation, and chart/report generation. (file: d:/project/cursor/data-analysis-agent/SKILL.md)

### How to use skills
- Discovery: The list above is the skills available in this session (name + description + file path).
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description, use that skill for that turn.
- Missing/blocked: If a named skill path can't be read, say so briefly and continue with the best fallback.
