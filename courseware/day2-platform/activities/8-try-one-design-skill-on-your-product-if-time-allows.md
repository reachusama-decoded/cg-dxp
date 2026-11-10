# Activity 8 — Try one design skill on your product (if time allows)

*Day 2 · Pairs · 20 minutes*

Pick one design-phase skill and run it on your own PRD and contract: `consumer-use-case-map` (who consumes it and how), `data-model` (the entities and their keys), `architecture-diagram` (the flow from sources to consumers), `data-quality-controls-plan` (the few checks that matter) or `nfr-specification` (performance, reliability, cost). Attach the PRD and the contract. Read the result for the invented detail before you keep anything. No build skills today: dbt comes tomorrow, with the design agreed.

**Produce**

- One generated design document, reviewed
- One line for the room: what it added that the PRD and contract did not say, and one thing it invented

**Finished early?** Run a second skill and check whether the two documents agree with each other.

**Debrief questions**

- Which phase was the skill for, and did your product have what that phase needs?
- What did it invent, and which input would have prevented it?

**Prompts.** `/ai-catalyst consumer-use-case-map` "Map the consumers, their use cases and access patterns for the product in #file:02-prd.md and #file:03-data-contract.md" · `/ai-catalyst data-model` "Design the conceptual and logical model for this product" · `/ai-catalyst architecture-diagram` "Draw the data flow from sources to consumers" · `/ai-catalyst data-quality-controls-plan` "Propose the controls for the target table in the contract".
