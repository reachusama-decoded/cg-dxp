---
name: dplc-publish
description: >-
  Phase 6 Publish sub-orchestrator under /dplc-build-stage. Records the
  deployment, produces the consumer onboarding guide and release notes
  when the product requires them, and verifies the marketplace listing;
  reports the Phase 6 gate. Use once Phase 5 UAT is signed off and
  deployment is staged.
  Trigger phrases: "publish the product", "Phase 6", "deploy and
  onboard", "ship to production", "go live", "write release notes".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: phase-6-publish
  dependencies:
    - deployment-record
    - consumer-onboarding-guide
    - release-notes
    - marketplace-search
  consumes:
    - uat-sign-off
    - build-checklist
    - data-contract
    - consumer-use-case-map
  shared-components:
    core: []
    platforms: []
  standards: []                 # orchestrator delegates rule coverage to invoked leaves
---

# Phase 6: Publish Orchestrator

This orchestrator guides you through **Phase 6 -- Publish** of the Data
Product Lifecycle (see `rfd/0002/README.md` for the full definition).

**Phase 6 purpose:** Deploy to production, onboard consumers, and announce
availability. This is the go-live phase.

**Who this is for:** A Data Product Creator working with DataOps and the
Data Product Manager for the final review of the release.

**Phase 6 gate:** *Production validated?* RFD 0002 § Phase 6 assigns the
Phase 6 artifacts *conditional* necessity, so the gate separates criteria
that always apply from those that apply only when a product attribute
holds. (Step 1 establishes the attributes; Step 5 verifies the marketplace
listing programmatically; the remaining criteria are checked at the end of
Step 4.)

*Always required:*
- **Marketplace listing live** (RFD 0002 Required artifact)
- At least one consumer confirmed access and validated the product
- Deployment record completed with environment + rollback plan (RFD:
  Recommended -- produced by default; if the user declines it, note that in
  the gate report)

*Conditionally required* -- each is satisfied **either** by the artifact
**or** by a recorded skip reason when its condition does not hold:
- Consumer onboarding guide available -- required only if the product has
  **external consumers**
- Release notes published -- required only if the product is **versioned**
  or serves **multiple consumer teams**

- Yes -> Ship stage (Phase 7 Operate)
- No -> Address deployment issues and retry

> **Scope note — physical App→Domain copy.** "Publish" here means
> *marketplace listing + governance docs*. The separate **deep-clone
> publish step** (`CREATE TABLE <domain_catalog>... DEEP CLONE
> <app_catalog>...` per `DBX-DELTA-009`) is currently
> **un-orchestrated** — no skill or runbook executes it, and the
> production exemplar (`edo-ig-data-products`) plumbs the
> `domain_catalog` variable but leaves it empty. The recommended
> shape lives in
> `skills/dbt-best-practices/references/catalog-architecture.md`
> under "Deep-clone publish pattern (suggested; pending live
> reference)". Operationalize that pattern in a follow-on PR once the
> platform team converges on it.

---

## Progress Reporting

As you work through each step, report progress clearly so the user can
follow along. For each sub-skill or action:

1. **Announce** what you're about to do before doing it
2. **Report** what you produced after each step
3. **Show specifics** -- not "wrote deployment record" but "Deployment
   record drafted: env=prod, version=1.0.0, rollback plan included"
4. **Use a checklist** format so the user can see what's done and what's
   left:

Example:
```
- [x] Read pre-Phase-6 artifacts (uat-sign-off approved, build-checklist present)
- [x] Product attributes: external consumers=yes, versioned=yes, teams=3
- [x] deployment-record: env=prod, version=1.0.0, rollback documented
- [x] consumer-onboarding-guide: 6 consumers, prereqs + queries included
- [ ] release-notes: drafting...
- [ ] Phase 6 gate determination
```

Never run silently. The user should always know where you are.

---

## Sub-Skills Invoked

| Skill | Type | Purpose | Required? |
|:------|:-----|:--------|:----------|
| `deployment-record` | document | Record what was deployed, when, by whom, and verification steps | Recommended |
| `consumer-onboarding-guide` | document | Document prereqs, datasets, queries, and support contacts for consumers | Optional -- required if external consumers |
| `release-notes` | document | Summarize what shipped: what's new, breaking changes, known issues | Optional -- required if versioned or multi-team |
| `marketplace-search` | workflow | Verify the marketplace listing exists and is validated (read-only check, no write) | Required |

The necessity column follows **RFD 0002 § Phase 6 Artifacts**: catalog /
marketplace listing = Required, deployment record = Recommended, onboarding
guide and release notes = Optional with conditions. Step 1 establishes the
product attributes that decide the conditional artifacts; when a condition
does not hold, the orchestrator **skips that artifact and records the reason
in the deployment record** (Steps 3-4) rather than forcing it. The three
document skills produce the Phase 6 artifacts; `marketplace-search` is
invoked at Step 5 to verify the listing exists and is validated. The deploy
itself happens outside the skill (CI/CD pipeline, manual deployment, or
DataOps handoff); these skills document, announce, and verify it.

---

## Sequencing

### Step 1 -- Read pre-Phase-6 artifacts

Before asking the user anything, check the conversation/workspace for
prior phase artifacts:

- `build-checklist` (Phase 4 -- Build) -- confirms build readiness
- `uat-sign-off` (Phase 5 -- Validate) -- **must be present and approved**
- `data-contract` (Phase 3 -- Design) -- feeds onboarding guide schema/SLA
- `consumer-use-case-map` (Phase 1 -- Triage) -- tailors onboarding examples

If `uat-sign-off` is missing or not marked approved, **stop and tell the
user Phase 5 must complete first**. Do not proceed to deployment without
UAT acceptance. **Do not generate a deployment record on the assumption
UAT will pass** -- the gate exists to prevent exactly that, and a
draft "pending UAT" artifact defeats it.

If the other artifacts are missing, ask the user where they live (or
whether earlier phases were skipped). Carry whatever is available forward;
note gaps in the release notes.

Also collect from the user (if not already known):
- Target environment (e.g., `prod`, `prod-eu`)
- Version / release identifier
- Rollback plan summary

**Establish the product's necessity attributes.** RFD 0002 § Phase 6 makes
two of the Phase 6 artifacts conditional, so before sequencing, determine
the three attributes that decide whether they are required. Infer from the
prior-phase artifacts first; ask the user only for what you cannot infer:
- **External consumers?** -- does the product serve consumers outside the
  producing team? The Phase 1 `consumer-use-case-map` usually answers this.
  Drives `consumer-onboarding-guide` (Step 3).
- **Versioned?** -- does the product follow a versioning scheme that
  consumers track (not merely the release identifier of this one deploy)?
  Drives `release-notes` (Step 4).
- **Multiple consumer teams?** -- is more than one team consuming the
  product? Also drives `release-notes` (Step 4).

Carry these three answers forward: Steps 3 and 4 branch on them, and Step 2
records any resulting skips in the deployment record.

### Step 2 -- Invoke `deployment-record` (Recommended)

RFD 0002 marks the deployment record **Recommended**. In practice, produce
it by default: it is both the authoritative record of this release event
*and* the place where any optional artifacts skipped in Steps 3-4 are
recorded with their reason. Only skip the deployment record if the user
explicitly declines -- in that case capture the deployment metadata and any
optional-artifact skips directly in the Step 6 gate report instead.

Call `deployment-record` with the deployment metadata gathered in Step 1:
environment, version, rollback plan, and verification steps.

The output captures *what was deployed and how to roll back*. Carry it
forward as input to Steps 3 and 4, and as those steps resolve, record in the
deployment record which optional artifacts were produced versus skipped, and
why (e.g. "release-notes skipped -- unversioned, single-team product (RFD
0002 § Phase 6: Optional)").

### Step 3 -- Invoke `consumer-onboarding-guide` (Optional -- required if external consumers)

**Condition (from Step 1).** The onboarding guide is required only if the
product has **external consumers** (consumers outside the producing team).

- **If external consumers:** call `consumer-onboarding-guide` with:
  - `data-contract` (Step 1) -- schema and SLA info
  - `consumer-use-case-map` (Step 1) -- tailor examples to known consumers
  - `deployment-record` (Step 2) -- endpoints, access methods, environment

  The onboarding guide tells consumers how to use the product: prereqs,
  queries, access process, support contacts. For a feature-level release on
  an existing product, *update* the existing onboarding guide rather than
  creating a new one.

- **If internal-only (no external consumers):** skip this step -- do not
  produce the guide. Record the skip in the deployment record:
  "consumer-onboarding-guide skipped -- internal-only product, no external
  consumers (RFD 0002 § Phase 6: Optional)."

### Step 4 -- Invoke `release-notes` (Optional -- required if versioned or multi-team)

**Condition (from Step 1).** Release notes are required only if the product
is **versioned** (follows a versioning scheme consumers track) **or** serves
**multiple consumer teams**.

- **If versioned or multi-team:** call `release-notes` with:
  - `deployment-record` (Step 2) -- version and components deployed
  - `data-contract` (Step 1) -- detect breaking changes vs. prior version
  - `uat-sign-off` (Step 1) -- carry forward known issues from validation

  Summarize: what's new, what changed, breaking changes, known issues. For a
  feature-level release, *append* to the existing release-notes document
  rather than creating a new one. For a first GA release of a versioned or
  multi-team product, still set the baseline document so later releases have
  something to append to.

- **If unversioned and single-team:** skip this step -- do not produce
  release notes. Record the skip in the deployment record: "release-notes
  skipped -- unversioned, single-team product (RFD 0002 § Phase 6:
  Optional)."

### Step 5 -- Confirm marketplace listing (ask + verify)

RFD 0002 lists **catalog / marketplace listing as the Required artifact**
for Phase 6. The Marketplace at `marketplace.capgroup.com` is the
canonical data product catalog at Capital Group; products are not
considered Published until they are registered and validated there.

**Today (centralized model).** Only EDO-designated **Data Producers**
can register new datasets / data products, via the **"Register Data"**
feature inside the Marketplace UI
(<https://marketplace.capgroup.com>). There is no write-side API
integration in this skill yet -- this step asks the user to confirm
the listing happened, then verifies it programmatically using the
read-only marketplace API via `marketplace-search`. *(See the
Marketplace FAQ on the DxP SharePoint for the current registration
process and authorization rules.)*

**Future (federated model).** Per the DxP Operating Model, additional
teams will gain the Data Producer role. When the marketplace exposes a
write API, a `marketplace-register` capability skill should be built
and this step rewired to invoke it instead of relying on manual
registration. Tracked in AICAT-83.

**Action -- ask and verify.**

1. **Ask the user:**

   > "Is the product registered in Marketplace (marketplace.capgroup.com ->
   > Register Data)? If yes, what's the product name as it appears in
   > marketplace?"

2. **If the user provides a marketplace name, invoke `marketplace-search`**
   to verify the listing programmatically:

   > `/marketplace-search <name>`

   Inspect the top matching entity and check:
   - `type.code == "data_product"` (not `dataset`, `data_domain`, or
     `external_data_product`)
   - `validated == true` -- marketplace's own "is it published" flag
   - `health` is healthy (not degraded / failing)
   - `ancestry[0]` matches the expected **target data domain** from the
     Phase 3 `data-contract.md`
   - Capture `detail_url` for the deployment record

3. **Report verification result** -- one of:

   - **Verified.** Entity found, validated, healthy, parented to
     `<ancestry[0]>`. Gate criterion satisfied. Record marketplace URL
     (`detail_url`) in the deployment record.
   - **Found but not validated.** The registration was filed but is not
     yet published in marketplace. Tell the user to follow up with the
     EDO Data Producer who submitted it. Gate criterion **not** satisfied
     until `validated == true`.
   - **Wrong entity type.** `marketplace-search` returned the entity as
     `<type.code>`, not `data_product`. Surface the discrepancy; the
     registering Data Producer may need to re-file or reclassify.
   - **Wrong target domain.** Found and validated, but `ancestry[0]`
     differs from the expected domain in `data-contract.md`. Surface the
     discrepancy; either the contract or the registration is wrong.
   - **Not found.** `marketplace-search` returned no matching entity.
     Either registration is incomplete, the marketplace search index
     hasn't picked it up yet (give it a few minutes), or the name in
     marketplace differs from what the user reported. Confirm the
     listing exists and re-verify.

4. **Capture the alignment pattern for traceability.** Marketplace
   stores the product as a `data_product` entity inside a data domain,
   but doesn't tag the *alignment pattern* (source-aligned,
   domain-aligned, or consumer-aligned -- decided in Phase 4 Build).
   Ask the user which pattern this product is, and record it in the
   deployment record's metadata so downstream consumers and ops can
   read the classification. This is a Catalyst-internal record, not a
   marketplace concept.

### Step 6 -- Phase 6 gate determination

Check the gate criteria from the Phase 6 gate section above: the
always-required criteria, plus each conditionally-required artifact **whose
condition holds** (external consumers -> onboarding guide; versioned or
multi-team -> release notes). A conditional artifact whose condition does
**not** hold is satisfied by its recorded skip reason -- do not treat a
correctly-skipped optional as a gate failure. Report the result:

**If the gate is satisfied:**
> "Phase 6 Publish complete.
> - Deployment record: [environment, version]
> - Consumer onboarding guide: [count] consumers covered *(or: skipped --
>   internal-only, no external consumers)*
> - Release notes: [link or summary] *(or: skipped -- unversioned,
>   single-team)*
> - Marketplace listing: [URL or marketplace entity ID]
> - Consumer validation: [name] confirmed access
>
> Gate result: **Production validated** -- proceeding to Phase 7 Operate.
> Run `/dplc-ship-stage` to begin Operate + Evolve setup."

For each optional artifact that was skipped, state the condition that made
it optional so the determination is auditable.

**If any required criterion fails:**
> State the specific blocker (e.g., "Marketplace listing not yet live --
> registration filed by [name] is pending EDO Data Producer publication",
> "No consumer has confirmed access yet", "Onboarding guide missing but the
> product has external consumers -- it is required for this product"). Tell
> the user exactly what to address; do not proceed to Phase 7.

**Do not announce the release externally until the gate passes.**
Premature announcement before the onboarding guide is published creates
support load.

### Step 7 -- Invite feedback

After the gate determination, append this one-line prompt as the final
line of your response:

> "Anything to flag about this run? Hit enter to skip, or tell me what
> worked / what didn't."

Then:
- **If the user replies with anything substantive** -- a sentence, a
  reaction, a problem description, even a short "worked great": invoke
  the `catalyst-feedback` skill with `$ARGUMENTS = "dplc-publish
  reply=<their reply verbatim>"`. The skill extracts session context,
  composes a draft issue, shows the user the full draft for review, and
  files after they confirm.
- **If the user hits enter / moves on / gives a non-substantive reply**
  (e.g. just "k", "ok", an emoji alone): do nothing. No file, no
  re-prompt. Silence means satisfied.

---

## Notes

- For **feature-level releases**, *update* the existing onboarding guide
  and *append* to the existing release notes rather than creating new
  artifacts (when those artifacts apply -- see Steps 3-4). The deployment
  record, when produced, is always new (every deployment is a discrete
  event).
- **Release-notes necessity is conditional** (Step 4): required for
  versioned products or multiple consumer teams, optional otherwise. When
  they apply, set a baseline document even for a first GA release so later
  releases have something to append to. For an internal, single-team,
  unversioned product, skipping them -- with the reason recorded in the
  deployment record -- is correct.
- **Do not announce the release externally** until the gate passes.
  Premature announcement before the onboarding guide is published
  creates support load.
- The deploy *itself* happens outside this skill (CI/CD pipeline, manual
  deployment, DataOps handoff). This orchestrator documents and announces
  the deploy; it does not perform it.
