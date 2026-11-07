# Activity 10 — Release decision

*Day 4 · Pairs · 20 minutes*

The nightly build produced a candidate output with 500 rows but only 497 distinct IDs, so the uniqueness check failed and the candidate was not published. Yesterday's accepted output is still available to consumers. In ten minutes, decide what should happen next and draft a two-sentence update to the consumer. Then ten minutes of discussion.

**Produce**

- A decision: what is released, what stays blocked, and who decides
- A two-sentence update to the consumer
- The information you are missing and who can supply it

**Debrief questions**

- Does the consumer's freshness commitment allow yesterday's output to stand today?
- What would make the three duplicate IDs a data problem rather than a pipeline problem?
- Who gets to override a failed quality gate, and how is that recorded?
