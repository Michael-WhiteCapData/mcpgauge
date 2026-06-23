# mcpgauge scoring methodology (v0)

The score is **deterministic and open** — no LLM, no network beyond talking to the
server you point it at. Anyone can reproduce or argue with it. This document is the
source of truth; the code in `score.py` implements exactly what's written here.

## Per-tool dimensions (each scored 0–5)

A tool is `{name, description, inputSchema}` as returned by `tools/list`.

1. **Purpose Clarity** (weight 0.25) — is there a description, and does it read as a
   real explanation rather than a restatement of the name?
   - 0 if no/empty description.
   - Scaled by description length bands and whether the first sentence adds
     information beyond the tool name's words.

2. **Parameter Semantics** (weight 0.20) — are the parameters documented?
   - Fraction of input-schema properties that have a non-trivial `description`,
     scaled to 0–5. Tools with no parameters score full marks (nothing to document).

3. **Behavioral Transparency** (weight 0.20) — does the description say what the
   tool returns or does (side effects, output shape)?
   - Heuristic: presence of return/effect signal words ("return", "returns",
     "outputs", "writes", "deletes", "creates", "list of", "JSON", etc.).

4. **Schema Validity** (weight 0.15) — is `inputSchema` well-formed?
   - `type: object`; every declared property has a `type`; no obviously broken
     constructs (e.g. empty `properties` while `required` is non-empty).

5. **Naming** (weight 0.10) — is the tool name clean and specific?
   - Matches `^[a-z][a-z0-9_]*$`, is not a vague generic ("run", "do", "execute",
     "tool", "call", "handler"), and is not duplicated within the server.

6. **Conciseness** (weight 0.10) — is the description in a healthy length band?
   - Penalize empty/one-word descriptions and bloated walls of text; reward
     focused descriptions (roughly 1–4 sentences).

**Tool score (TDQS)** = weighted sum of the six dimensions (0–5).

## Server score

```
server_score = 0.6 * mean(TDQS over tools) + 0.4 * min(TDQS over tools)
```

The 40% weight on the *minimum* means a single poorly-described tool drags the
whole server down — which matches how agents actually fail (they pick the worst
tool at the worst moment). A small **coherence** penalty is applied for duplicate
tool names and for an excessive tool count with many low scorers.

## Grades

| Grade | Server score |
|-------|--------------|
| A     | ≥ 4.0        |
| B     | ≥ 3.3        |
| C     | ≥ 2.6        |
| D     | ≥ 1.8        |
| F     | < 1.8        |

## Versioning
This methodology is versioned (`METHODOLOGY_VERSION` in `score.py`). Any change to
weights, bands, or heuristics bumps the version so historical scores remain
interpretable. Scores from different methodology versions are not comparable.
