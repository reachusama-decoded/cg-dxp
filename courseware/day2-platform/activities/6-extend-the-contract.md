# Activity 6 — Extend the contract

*Day 2 · Individual, then pairs or tables · 30 minutes*

On your own, ask Catalyst what source-to-target transformation types and what service-level indicators and objectives it knows. Then, in pairs or at your table, take one of yesterday's data contracts: name the incoming tables and the outgoing table, write the rules that get you from one to the other (lookups, derivations, filters, what nulls mean), and the commitments a consumer would hold you to. Transcribe the discussion, give it to Catalyst, extend the contract, then inspect and revise.

**Produce**

- At least one unambiguous mapping rule someone else could implement without asking you
- At least one measurable commitment with its indicator, target, tolerance and time zone
- The revised contract, shared for review

**Finished early?** Add the breach response: who is told, by when, what they are told.

**Debrief questions**

- Could someone else implement this rule without asking you what it means?
- For 'available by 07:30': which time zone, which days, measured where, and what happens on failure?
- For a lookup: what is the join key, and what happens with zero or several matches?

**Prompts.** "What types of source-to-target transformation do you distinguish?" · "What service-level indicators and objectives should a data contract state?" · then `/ai-catalyst data-contract` with the transcript of your discussion and the existing contract attached: "Extend the STTM and SLA sections; keep everything else."
