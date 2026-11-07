---
authors: CPTS
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/416
labels: architecture, unity-catalog, access-model, consumption, governance
---

# RFD 0022 Catalog Topology, Access Model, and Read Routing

## Problem

Data on the Caspian platform flows across many producers and consumers,
but three foundational questions do not have shared answers:

1. **Placement.** Which Unity Catalog catalog does a new data product
   go in? Teams cannot answer this without a synchronous decision with
   the platform team.
2. **Access.** Who is allowed to read from and write to a given catalog,
   and at what grain? Access decisions today are per-product, not
   per-tier, so the same shape of privilege is granted differently
   across domains.
3. **Read routing.** Should a consumer read from the lakehouse or
   directly from the Book of Record (BOR)? Some consumers route every
   read through the lakehouse even when it adds no value over the BOR;
   others bypass the lakehouse even when it would give them integrated
   or historical data they need. There is no shared principle for the
   choice.

This RFD answers those three questions. Enumeration of concrete
integration and consumption patterns (batch, CDC, streaming, Delta
Sharing, API, extract, etc.) is out of scope.

## Background

Catalyst already defines:

- **RFD 0002** — Data Product Lifecycle (DPLC). Defines the phases,
  the Phase 3 Design artifact, and the source-aligned / consumer-aligned
  product concepts this RFD builds on.
- **RFD 0003** — Repository strategy and catalog placement via schema
  routing macros in `caspian-core`. Repository grain is scoped to
  independent delivery; catalog placement is a governance artifact.
- **RFD 0008** — Engineering standards, including `DBX-UC-*` rules for
  Unity Catalog (three-part names, external tables) and `DBX-SEC-002`
  for OAuth-only service-principal auth.
- **RFD 0010** — Lake versioning strategy: consumer-facing view
  versioning (`view` / `view_prev`, `_v1` / `_v2`) and multi-stage
  schema-change migration via IATs.
- **RFD 0011** — DAG standards for Airflow-orchestrated ingestion.
- **RFD 0012** — Databricks Asset Bundle standards for deployment.
- **RFD 0013** — dbt on Databricks SQL standards.

**RFD 0009 — ODCS data contracts** is *planned* (referenced from
RFD 0002 Phase 3 as a follow-on RFD; not yet on `main`). Several
parts of this RFD (§ 1.3.3 contract-named tables, the
Part 2 freshness gate) lean on it directly, so **RFD 0022 reaching
`published` is gated on RFD 0009 landing first**.

The three data product alignments used throughout this RFD are
defined here (RFD 0002 names only source-aligned and consumer-aligned;
domain-aligned appears in passing in RFD 0003 but is not defined as a
set). This RFD owns the three-alignment taxonomy until it is lifted
into a shared glossary or into an update of RFD 0002:

- **Source-aligned** — mirrors an upstream system with minimal
  transformation. Ownership sits with the ingestion team.
- **Domain-aligned** — canonical models owned by a single business
  domain that union and reconcile source-aligned tables. Inputs may
  span multiple domains via the RFD 0003 cross-domain sources
  mechanism (§ 1.3.3); ownership and placement remain single-domain.
  Cross-cutting reference data (e.g., Product, Results) may be owned
  either by its natural home domain or by a shared reference / MDM
  domain, following the same Curated-tier access model. Ownership
  sits with the domain team.
- **Consumer-aligned** — denormalized, pre-aggregated, or API-shaped
  outputs built on top of domain-aligned models for specific downstream
  use cases. Ownership sits with the consuming team (or a shared
  serving team).

What is missing is the mapping from these alignments to concrete
Unity Catalog placement, the corresponding access model per tier, and
the principle that tells a consumer whether to read from a
lakehouse-managed catalog at all.

## Proposal

The RFD has three goals:

1. **Catalog topology.** Define the tiers, name them, and place data
   products by alignment (Part 1).
2. **Access model.** Define who reads and writes at each tier and at
   what grain (Part 1 § 1.3).
3. **Read routing.** Define when a consumer reads from the lakehouse
   and when a consumer reads directly from the Book of Record (Part 2).

A short governance section (Part 3) records what counts as a standard,
what counts as an exception, and how exceptions are reviewed — so the
three goals above are actionable rather than aspirational.

### Part 1: Catalog topology and access model

#### 1.1 Catalog tiers

Every Unity Catalog catalog belongs to exactly one tier. The tier
determines who can write, who can read, and what governance controls
apply.

| Tier | Purpose | Alignment | Write access | Read access |
|---|---|---|---|---|
| **Source-aligned** | Untransformed ingested data, one schema per source system (catalog granularity per § 1.3.1) | Source-aligned | Ingestion service principal only | Domain SPs (curated → source traceability); Ops / L3 triage group; platform observability SP; **see § 1.3.1 for full model** |
| **Application / Incubation** | App-team-owned space for building and curating a data product; publishes to a domain's Curated catalog via Delta deep clone once sign-off is granted (§ 1.3.2) | Any (pre-publication and ongoing curation) | App team service principal | App team developer group; named review consumers; App team Ops / L3 triage group; no downstream production reads; **see § 1.3.2 for full model** |
| **Curated / Domain** | Canonical, contract-bound domain models | Domain-aligned | Domain team service principal | Cross-domain consumers via `_cross_domain__sources.yml`; consumer team SPs per ODCS contract; domain read-user groups; Ops / L3 triage; Delta Sharing recipients; **see § 1.3.3 for full model** |
| **Research / Sandbox** | Single team-scoped catalog for research and sandbox exploration; not contract-bound, no downstream production readers, and never a governed-data-product publication target. Consumer-aligned outputs live in Curated (§ 1.3.3), not here. Production candidates leave via DPC + Application (§ 1.3.4). | N/A (exploratory) | Team producer SP; individual users on their own schema | Individual user schemas owner-only by default; team-schema peer read configurable per team; Ops / L3 on invitation only; **see § 1.3.4 for full model** |
| **Regulated** *(within-tier pattern — see § 1.3.5)* | Regulated data (MNPI, restricted PII); by default co-located in the home schema with fine-grained controls, escalated to a **dedicated schema in the same home catalog** when in-schema controls are insufficient. Not a physical tier of its own; the parent tier (Source-aligned, Application, Curated, or Research / Sandbox) still applies. | Any (inherits home tier) | Restricted principals only, per § 1.3.5 | Restricted principals only, all reads audited |

> **Naming convention.** *(To be finalized during discussion.)* Candidate
> pattern: `<env>_<tier>_<domain-or-program>` — e.g.,
> `prd_curated_investments`, `prd_app_<team-or-product>`,
> `prd_src_bloomberg`, `prd_research_<team>`. Exact prefix/suffix
> and separator are open questions.

#### 1.2 Placement rules

A data product is placed in exactly one catalog. Placement follows the
alignment of the product:

- A **source-aligned** product goes in a Source-aligned catalog and
  lands in a **schema scoped to its source system** (§ 1.3.1);
  whether that catalog is one-per-source or shared across related
  sources is an open question.
- An **incubating product** owned by an app team — one that will
  eventually be published as domain-aligned but is still under design
  — goes in that team's Application / Incubation catalog (§ 1.3.2).
  Once the receiving domain signs off the ODCS contract, the product
  is **published to the owning domain's Curated catalog via a Delta
  deep clone**; ongoing curation stays with the app team in the
  Application catalog and the deep clone is republished on both
  cadences (each data-refresh run and each release cycle — see
  § 1.3.2 step 4). Consumer-aligned derivatives are built on top of
  the Curated deep-clone target, not directly from the Application
  catalog. The publication path is described in § 1.3.2.
- A **domain-aligned** product goes in the Curated / Domain catalog
  owned by the producing domain. Cross-domain *inputs* are pulled in
  via declared sources per § 1.3.3 (row: *Downstream domain SPs*); the
  product itself still has a single owning domain and lands in that
  domain's Curated catalog.
- A **consumer-aligned output** (a use-case-shaped table backing a
  BI dashboard, downstream API, or analytical application) lives
  in the producing domain's Curated catalog (§ 1.3.3) alongside
  domain-aligned canonical models. **Alignment describes the shape
  of the product, not the tier it lives in** — a Curated catalog
  can hold both. The ODCS contract (RFD 0009) names the consumer
  and the specific tables published.
- A **research artifact** or a **sandbox** dataset goes in the
  team's Research / Sandbox catalog (§ 1.3.4). Nothing here is
  contract-bound and there are no downstream production readers.
  If a research or sandbox dataset identifies a real data-product
  need — domain-aligned or consumer-aligned — the **Data Product
  Creator (DPC) Team** takes ownership and rebuilds it in an
  Application catalog (§ 1.3.2), which then publishes to the
  producing domain's Curated catalog via Delta deep clone; the
  original schema is not lifted into production.

Placement authority is the **data-product registry** per
**`DBX-UC-002`** (severity error): a data product's catalog is
determined by the registry, and hardcoding a catalog name that
deviates from the registry is a coding-standards violation. The
`caspian-core` schema routing macros (RFD 0003 § *Platform
Package: caspian-core* and § *Cross-Domain References*) are the
runtime mechanism that projects registry entries onto dbt
`target.catalog` / `target.schema`. Placement-validating CI
checks and the registry tooling itself ship separately — see
Open Questions. A repository that writes to more than one
Curated catalog is the RFD 0003 § *Multi-Domain Repositories*
case — allowed, but requires architecture review and written
platform-team approval.

#### 1.3 Access model

Access is granted at the **tier** level as a template, with per-catalog
specialization. This section defines *what* each principal gets — the
privilege, the grain, and whether it is standing or exception-scoped.
The **mechanism** for grants is Terraform per **`DBX-UC-008`**
(severity error) — `GRANT` / `REVOKE` are managed as IaC, never ad-hoc
SQL, with a documented break-glass path (temporary grants for
incident response with a follow-up Terraform PR within 24 hours).
§ 3.3 below tracks the *why* of controlled exceptions; `DBX-UC-008`
is the *how*. Auth type, group provisioning, and additional
regulated-data controls beyond `DBX-UC-005` are still out of scope;
see Open Questions.

##### 1.3.1 Source-aligned catalogs

| Principal | Privilege | Grain |
|---|---|---|
| Ingestion SP (one per catalog) | ALL PRIVILEGES on the catalog it lands to | Catalog |
| Domain SPs reading from this source | SELECT on the specific tables declared as dbt sources | Table |
| Platform observability SP | USE CATALOG + BROWSE for lineage / monitoring (SELECT granted at schema / table grain where needed) | Catalog |
| Operations / L3 / production-support group | SELECT for triage (standing, read-only) | Schema or table |
| Operations / L3 human (data-fix activity) | Time-boxed MODIFY on the specific object being repaired | Table |
| Business humans | No standing access | — |

Notes:

- **Triage read** for Operations, L3, and production-support is a
  standing grant, scoped to the tables they support, with periodic
  recertification. This is *not* a per-incident approval path —
  waiting for ad-hoc approval during an incident is too slow.
- **Data-fix write** by an L3 / operations human on a Source-aligned
  table is a **controlled exception** — it violates the "writes are
  via the Ingestion SP only" default. Every occurrence must:
  - Route through the controlled-exception workflow (ticketed,
    approved, time-boxed).
  - Be recorded in the exception register (§ 3.3) after the fact,
    with the ticket ID, tables touched, and reason.
  - Be reviewed on the exception cycle so that recurring fixes are
    lifted into the ingestion pipeline instead of repeated by hand.
- **Schema layout.** One schema per source system inside a
  Source-aligned catalog, regardless of catalog granularity. Whether
  a Source-aligned catalog holds a single source system or several
  related source systems is an open question — see Open Questions on
  catalog granularity and S3 throttling.
- **Per-source sharing.** Access to source data is granted at the
  **schema or table grain of the specific source**, never at the
  catalog grain. A downstream domain or consumer team that consumes
  one source system does **not** thereby gain access to any other
  source that happens to share the catalog. This preserves
  source-system boundaries even when several sources share a catalog.
- Source-aligned catalogs remain internal to their ingestion program
  for **ad-hoc human reads**: cross-team humans without a declared
  consumption need are anti-pattern (§ 3.4). Scoped SP access for
  data-product-creator teams and named consumers (per contract) is
  covered by the per-source sharing rule above and by the Domain-SP
  row in the table. Whether **business humans** should get standing
  read access (via AD groups) on named Source-aligned tables —
  rather than only through Curated — is an open question; see Open
  Questions.
- **Retention and lifecycle** on Source-aligned tables follow the
  source contract with the upstream system. Curated retention is
  set by the ODCS contract (RFD 0009) of the producing data
  product; Research / Sandbox retention follows the tier's
  auto-archive policy (§ 1.3.4). **Regulated-data deletion and
  right-to-erasure** are
  out of scope for this RFD — the enforcement mechanism belongs with
  the Security & Secrets follow-on and the compliance program that
  owns retention policy for MNPI and restricted PII.
- No consumer-aligned or downstream production reads land here —
  downstream consumers read from the Curated catalog. When a
  Source-aligned dataset is itself contract-published as a
  source-aligned data product (RFD 0002), named consumer SPs get
  table-grain SELECT per contract, on the source-specific schema
  only.

##### 1.3.2 Application / Incubation catalogs

Application catalogs are where an **app team** builds and iterates
on a data product *before* it is contract-published to a domain
(Curated) catalog. "App team" here is used broadly: any team
incubating a data product before Curated publication — including
an application-development team building an operational data
product, a **domain team building a domain-aligned product still
under review**, or a DPC team rebuilding a research dataset
(§ 1.3.4). Application is the pre-publication home for all three
shapes; the distinction between them is a role / handoff
question that Phase 3 Design (RFD 0002) records, not a tier
question. Unlike the sandbox schemas in the Research / Sandbox
catalog (§ 1.3.4), an Application catalog is
code-managed, runs a real pipeline, and follows the same lifecycle
discipline as a production tier — but it is **not** contract-bound,
has **no** downstream production reads, and holds only work that is
on a promotion path to a domain.

**When to use.**

- Building a new data product where the target Curated / Domain owner
  is not yet ready to receive it, or the model / contract is still
  under review.
- Piloting a candidate model against real data on a real pipeline
  before requesting a domain to adopt it.
- Iterating on a candidate model that includes regulated data
  (MNPI, restricted PII) under the same fine-grained controls that
  the destination Curated schema will use.
- **DPC-driven productionization** of a research or sandbox
  dataset from a team's Research / Sandbox catalog (§ 1.3.4).
  The Data Product Creator (DPC) Team takes ownership and
  rebuilds the dataset here as a governed product before
  deep-clone publication to Curated (§ 1.3.3).

**Not for.**

- Individual exploration or ad-hoc analysis — use the team's
  Research / Sandbox catalog (§ 1.3.4).
- Finished products that already have a Curated owner — those land
  in the owning domain's Curated catalog from day one.
- Application catalogs publish to Curated only, never directly to
  a Research / Sandbox catalog. Both domain-aligned canonical
  products and consumer-aligned (use-case-shaped) products land
  in the receiving domain's Curated catalog (§ 1.3.3); alignment
  describes the shape of the product, not the tier.

| Principal | Privilege | Grain |
|---|---|---|
| App team producer SP | ALL PRIVILEGES on the app team's Application catalog | Catalog |
| App team developer group | SELECT + BROWSE for iteration and review | Catalog |
| Named review consumers (prospective domain / consumer teams, product owners) | Time-boxed SELECT during review | Table |
| App team Ops / L3 / production-support group | SELECT for triage (standing, read-only) | Schema or table |
| Ops / L3 human (data-fix activity) | Time-boxed MODIFY on the specific object being repaired | Table |
| Downstream production SPs (domain / consumer / another app team) | No access | — |
| Humans outside the app team | No standing access | — |

Notes:

- **No downstream production reads.** A Curated pipeline must not
  `source()` or `ref()` an Application table; cross-team
  consumption happens only after deep-clone publication.
  Enforcement is via the UC grant model — the access table above
  gives *Downstream production SPs — No access* — so the read
  simply fails at query time. Compile-time / macro-level
  enforcement (rejecting an Application `source()` in a Curated
  project's dbt DAG) is a prospective control in `caspian-core`;
  see RFD 0003 Open Questions.
- **No consumer contract.** Because the product is still under
  review, there is no ODCS contract (RFD 0009) and no published
  freshness / quality SLA. The app team may run internal quality
  checks, but they are not a governance artifact.
- **Regulated data is allowed under the § 1.3.5 pattern.** An app
  team building a candidate model that will land in Curated with
  MNPI, restricted PII, or other regulated content works with that
  content in the Application catalog under the same fine-grained
  controls the destination Curated schema will enforce: table ACLs,
  row filters, column masks, tag-based access, and full audit
  logging. If the destination requires the § 1.3.5 escalation
  (dedicated Regulated schema), the Application catalog uses the
  same pattern in-place, in a schema inside the app team's own
  Application catalog. The compliance approver named in the
  eventual contract must sign off on the Application-catalog
  handling before regulated content lands there. When the
  Application catalog contains regulated tables, the **App team
  developer group** grant reverts from catalog-grain
  `SELECT + BROWSE` to **table-grain SELECT** on regulated
  objects per § 1.3.5 additive controls (`no schema-wide or
  catalog-wide read` on regulated objects); non-regulated
  schemas in the same catalog keep the catalog-grain default.
- **Environment strategy.** An Application catalog exists per
  environment where the pipeline runs (typical name pattern
  `<env>_app_<team-or-product>`); non-prod environments follow the
  same access model with the app team's non-prod SP.
- **Auto-archive.** Application schemas untouched beyond a team-
  defined threshold are auto-archived, similar to research and
  sandbox schemas in § 1.3.4 *(exact threshold is an open
  question)*.

**Publication path.**

Unlike an ownership handoff, publication from an Application
catalog to a domain's Curated catalog is a **Delta deep clone**
(§ 1.3.3). The app team continues to own and curate the
source-of-truth in its Application catalog after publication; the
domain's Curated catalog holds a governed deep-clone copy that
downstream consumers read from. Application catalogs never publish
directly into a Research / Sandbox catalog. Both
domain-aligned canonical products and consumer-aligned
(use-case-shaped) products land in the receiving domain's
Curated catalog (§ 1.3.3) as the deep-clone target; the choice
of shape is a design decision recorded in the ODCS contract,
not a tier decision.

1. **Design.** The Phase 3 Design artifact (RFD 0002) names the
   receiving domain and the destination Curated catalog / schema /
   table for the deep clone.
2. **Contract and sign-off.** The ODCS contract (RFD 0009) is
   drafted and signed off by the receiving domain team. Where the
   product carries regulated content, the compliance approver signs
   off on the deep-clone handling and on any § 1.3.5
   escalation-schema arrangements at both source (Application) and
   target (Curated).
3. **Deep-clone publication.** The domain provisions the target
   schema in its Curated catalog and, via Terraform per
   `DBX-UC-008`, grants the write path that executes the deep
   clone from the Application source table on the cadences in
   step 4.
   The deep-clone target is registered by the domain, is what
   the contract points at, and inherits the § 1.3.3 access model
   (domain producer SP owns writes; only contract-named consumers
   can read).
4. **Ongoing curation stays in the Application catalog.** The app
   team keeps iterating in Application — fixes, v-next work, and
   any pre-release changes to the source-of-truth. The deep clone
   is republished on **both** cadences: each **data-refresh run**
   of the product's pipeline (so downstream consumers see fresh
   data on the pipeline's normal cadence) and each **release
   cycle** of the pipeline code itself (so contract-approved
   pre-release changes to the source-of-truth reach Curated).
   Application-catalog data is still not directly readable by
   downstream production consumers; they read the Curated
   deep-clone target only.

Because curation stays in Application after publication, the
auto-archive rule does not apply to the actively-curated product
schema. An app team may also keep separate v-next candidate schemas
in the same Application catalog, subject to the same
no-downstream-production-reads rule.

##### 1.3.3 Curated / Domain catalogs

| Principal | Privilege | Grain |
|---|---|---|
| Domain producer SP | ALL PRIVILEGES on the domain's own Curated catalog | Catalog |
| Downstream domain SPs | SELECT on tables named in `_cross_domain__sources.yml` | Table |
| Consumer team SPs | SELECT on tables named in the consumer's contract (RFD 0009) | Table |
| Domain read-user group | SELECT on all schemas of the domain's catalog | Schema |
| Cross-domain read-user group (per approved subject area) | SELECT on named tables | Table |
| Domain Ops / L3 / production-support group | SELECT for triage (standing, read-only) | Schema or table |
| Ops / L3 human (data-fix activity) | Time-boxed MODIFY on the specific object being repaired | Table |
| Delta Sharing recipients | SELECT via a named share | Share |
| Humans outside the domain | No standing access | — |

Notes:

- **Holds both domain-aligned and consumer-aligned products.**
  A domain's Curated catalog can host both canonical
  domain-aligned models and consumer-aligned (use-case-shaped)
  outputs backing BI dashboards, downstream APIs, and analytical
  applications. Alignment describes the shape of the product, not
  the tier it lives in; both kinds are contract-bound and named
  in the ODCS contract (RFD 0009).
- Contract-bound: the ODCS contract (RFD 0009) names the exact tables
  published for cross-domain / consumer consumption.
- Writes are always via the domain producer SP; **any human write is a
  controlled exception** and must route through the controlled-
  exception workflow, be logged in the exception register (§ 3.3),
  and be reviewed for pipeline lift.
- Because Curated is contract-bound, human data-fix writes carry
  extra risk of silent contract drift. The exception review must
  confirm the fix does not alter the published schema or invalidate
  the contract's freshness / quality guarantees.
- Triage read for domain Ops / L3 / prod-support is a standing grant
  with periodic recertification, scoped to the domain they support.
- Placement authority is the data-product registry (`DBX-UC-002`);
  enforcement is the UC grant model — the domain producer SP holds
  ALL PRIVILEGES only on its own Curated catalog (first row above).
  `caspian-core` schema routing is the runtime mechanism that
  *projects* the registry entry onto dbt targets (RFD 0003); the CI
  check validating targets against the registry is still prospective
  (see Open Questions).
- **Deep-clone-published models** — datasets published from an
  app team's Application catalog (§ 1.3.2) land here as Delta deep
  clones. The domain producer SP owns the write path for the clone
  target and the domain registers the table; the app team continues
  to curate the source-of-truth in its Application catalog and the
  clone is republished on both cadences (each data-refresh run and
  each release cycle — see § 1.3.2 step 4).

##### 1.3.4 Research / Sandbox catalogs

Research / Sandbox catalogs are a single physical catalog per team
(or per line of business) that hosts two overlapping kinds of
exploratory, team-owned work:

- **Research** — analyst and data-science exploration.
- **Sandbox** — individual users' ad-hoc work.

The tier is **not contract-bound, has no downstream production
readers, and is never a publication target for a governed data
product**. Consumer-aligned outputs (use-case-shaped tables backing
BI dashboards, downstream APIs, and analytical applications) do
**not** live here — they live in the producing domain's Curated
catalog (§ 1.3.3) alongside domain-aligned canonical models.
Alignment describes the shape of a product, not the tier it lives in.

| Principal | Privilege | Grain |
|---|---|---|
| Team producer SP | ALL PRIVILEGES on the team's own catalog | Catalog |
| Individual users (research / sandbox) | ALL PRIVILEGES on their own schema in the catalog | Schema |
| Team members (peer review, shared research) | Configurable per team; default read-only on team schemas | Schema |
| Ops / L3 (on request) | Ad-hoc, owner-invited, time-boxed SELECT for troubleshooting; no standing grant | Schema |
| Everyone else | No access | — |

Notes:

- **Prod-hosted, exploratory, not contract-bound.** The catalog
  lives on the production UC / platform, but its contents carry no
  ODCS contract (RFD 0009), no published freshness / quality SLA,
  and no downstream production readers. No BI dashboard, downstream
  API, or analytical application takes a production dependency on
  a Research / Sandbox schema; those consumers read from Curated
  (§ 1.3.3).
- **Reads from Source-aligned and Curated.** The team producer SP
  has SELECT on the Source-aligned (§ 1.3.1) and Curated (§ 1.3.3)
  catalogs its access agreement names — both domain-aligned canonical
  models in Curated and the underlying source-aligned data are valid
  inputs for research and sandbox work. No ambient read on other
  Curated or Source-aligned catalogs, and no cross-team read into
  another team's Research / Sandbox catalog.
- **Individual workspaces are owner-scoped by default.** Each
  research / sandbox user has their own schema with owner-only
  access; sharing within the team is configurable per team. There
  is no data-fix exception path for individual schemas — the owner
  fixes their own workspace.
- **Owner vs. grantee (`DBX-UC-004`).** Per `DBX-UC-004`, every
  UC schema owner is a service principal or group, never an
  individual. The ALL PRIVILEGES granted to the individual
  research / sandbox user above is a **grant**, not UC ownership —
  the schema is owned by the team producer SP (or a team-scoped
  group) that provisioned the user's workspace, and the ALL
  PRIVILEGES grant is what gives the user practical control while
  ownership stays with the team SP for bus-factor and lifecycle
  purposes.
- **Ops / L3 access is ad-hoc.** No standing grants. Access is
  invited by the schema owner via a support ticket and time-boxed
  to the troubleshooting window. There is no data-fix exception
  path in this tier.
- **Auto-archive.** Schemas untouched beyond a team-defined
  threshold are auto-archived *(exact threshold is an open
  question)*.
- **Regulated data is exception-only.** Research / Sandbox is not
  a default landing spot for PII, MNPI, or other regulated content.
  Named research use cases that legitimately require regulated data
  must apply the § 1.3.5 pattern with per-dataset compliance-
  approver sign-off. Where the use case is durable rather than
  one-off, DPC-driven productionization (below) is the preferred
  path.
- **Productionization is via DPC + Application, never in place.**
  When a research or sandbox dataset identifies a real data-product
  need — domain-aligned or consumer-aligned — ownership transfers
  to the **Data Product Creator (DPC) Team**. The DPC Team rebuilds
  the dataset in an Application / Incubation catalog (§ 1.3.2),
  drives Phase 3 Design (RFD 0002) and RFD 0009 contract sign-off
  with the producing domain, and publishes to the domain's Curated
  catalog via Delta deep clone. The original Research / Sandbox
  schema is not lifted into production.

##### 1.3.5 Regulated data

Regulated data — MNPI, restricted PII, dataset-specific compliance
controls — has **two placement modes**. The default keeps the data in
its home schema with fine-grained controls; the escalation isolates
it in a **dedicated schema within the same home catalog**. The choice
is made per dataset in the Phase 3 Design artifact and reviewed by the
data owner and the compliance approver.

**Default: fine-grained controls in the home schema.**

The dataset stays in its natural Source-aligned, Application,
Curated, or Research / Sandbox schema and inherits that tier's access model
(§ 1.3.1 – § 1.3.4). On
top of the tier grant, the following controls are **additive** and
required:

- **Table ACLs.** `GRANT SELECT` only on the specific tables the
  consumer is approved for; no schema-wide or catalog-wide read.
- **Row-level filters.** Restrict rows to those the consumer is
  entitled to see (e.g., filter by book, region, or entitlement list).
- **Column masks.** Hash, redact, or null-out sensitive columns for
  consumers who lack the higher-privilege role.
- **Attribute-based (tag-based) access.** Regulated objects carry
  the `DBX-UC-005` tag schema — `data_classification`
  (`confidential` or `restricted` for regulated content), `pii`
  (`true` / `false`), `retention_days`, and `data_product`
  (registry identifier). Row-filter and column-mask policies grant
  access on tag value + consumer attribute. **MNPI tagging is an
  open question**: whether MNPI is a distinct `mnpi=true` boolean
  parallel to `pii`, or a reserved `data_classification` value, is
  deferred to a follow-up amendment of `DBX-UC-005` — see Open
  Questions.
- **Audit.** All reads on any object carrying a regulated tag are
  captured in the workspace / UC audit log per **`DBX-SEC-005`**
  (audit log delivery, severity error); metadata queries against
  `system.access.audit` follow `DBX-UC-009` (advisory).

The default is preferred because it avoids catalog- and
schema-sprawl, keeps lineage intact, and lets the same table serve
both restricted and non-restricted consumers under a single contract.

**Escalation: dedicated Regulated schema in the home catalog.**

A dedicated Regulated schema — inside the dataset's existing
Source-aligned, Application, Curated, or Research / Sandbox
catalog — is used **only** when
the in-schema controls of the default cannot meet the required
protection. Common triggers:

- Strict information barrier (e.g., MNPI wall) where row filters and
  column masks on a shared schema cannot be relied on to hold under
  materialized-view fanout, in-place clones, or shared compute.
- Audit / recertification cadence higher than the surrounding schema
  can accommodate.
- **Object-level** storage-path isolation is required for the
  regulated objects (distinct S3 prefix for retention / backup /
  lifecycle policy) and can be met by a schema-level managed /
  external location. Note that **credential-level** isolation
  cannot be met at schema grain — § 1.3.6 makes the storage
  credential catalog-scoped, so a mandated distinct storage
  credential is one of the triggers for the
  separate-Regulated-catalog sub-exception below.

A **separate Regulated catalog** is **not** the default escalation and
is used only if schema-level isolation demonstrably cannot meet the
compliance requirement (e.g., mandated distinct metastore, storage
credential, or workspace). Such cases are logged as exceptions
(§ 3.2) on top of the escalation-schema exception and reviewed by the
platform team plus compliance.

A separate Regulated catalog **inherits the access model of the
home tier it isolates** — the catalog is still classified as e.g.
Source-aligned, Application, Curated, or Research / Sandbox for
§ 1.1 and § 1.3 purposes, just physically carved out. The producer
SP that owns the home catalog also owns the separate Regulated
catalog and holds ALL PRIVILEGES on it (satisfying § 1.3.6); the
escalation access table below applies at schema grain within the
isolated catalog rather than only within a schema of the home
catalog.

When escalated to a Regulated schema, the access model is:

| Principal | Privilege | Grain |
|---|---|---|
| Producer SP that owns the home catalog | ALL PRIVILEGES on the Regulated schema | Schema |
| Named consuming SPs (per contract) | SELECT on approved tables only | Table |
| Named restricted humans | SELECT with row-filter / column-mask policies | Table + RLS/CLS |
| Named Ops / L3 / production-support (cleared for the dataset) | SELECT for triage on approved tables | Table + RLS/CLS |
| Ops / L3 human (data-fix activity) | Time-boxed MODIFY on the specific object being repaired | Table |
| Everyone else (including other users of the same catalog) | No access to the Regulated schema | — |

Notes (apply to both modes unless specified):

- Data classification recorded at the table level in UC comments and
  enforced tags.
- Ops / L3 access is **not** the same as the general prod-support
  grant elsewhere: only individuals specifically approved and
  cleared for the regulated dataset receive access. No blanket
  team-wide access.
- Data-fix writes require **regulatory review in addition to the
  standard controlled-exception review** — the exception register
  entry must name the compliance approver, not just the technical
  approver.
- **Platform observability SP.** The observability SP (§ 1.3.1) does
  **not** have standing SELECT on Regulated schemas or on
  regulated-tagged objects in the default in-schema mode. Lineage and
  monitoring coverage of regulated objects is granted case-by-case as
  a controlled exception, with the compliance approver named in the
  register entry.
- Approvals expire and require recertification (frequency TBD).
- The specific enforcement (auth hardening, network / MFA controls,
  approval-workflow tooling, and — for the escalation mode — the
  schema-level storage-isolation controls) is deferred; see Open
  Questions.

##### 1.3.6 Cross-cutting rules

Apply to every tier:

- **Three-part names.** Every ref uses `catalog.schema.table`
  (`DBX-UC-001`).
- **External tables preferred** over managed (`DBX-UC-003`,
  severity warning; the rule's verbatim exception allows
  managed tables for test / sandbox convenience and calls
  itself out as current-state, not a permanent architectural
  commitment); access to the underlying object storage follows
  the catalog's storage credential.
- **Unity Catalog privilege names.** All DML on a UC table is
  governed by the single **`MODIFY`** privilege; UC does not expose
  separate `INSERT` / `UPDATE` / `DELETE`. Catalog-grain access uses
  `USE CATALOG` (+ `BROWSE` for metadata discovery); `SELECT` is a
  schema- or table-grain privilege and must be granted at that grain.
- **Owning producer SP only** may hold ALL PRIVILEGES on its own
  production catalog. Never grant ALL PRIVILEGES to a human or to a
  non-owning SP on a production catalog.
- **Standing grants go to groups**, not to individual users, so
  joiner / leaver is handled at the identity-provider boundary.
  Standing human read access on Curated / consumer-aligned data
  goes through AD / UC groups (§ 1.3.3), which keeps onboarding
  of large BI user populations out of the exception register.
  Individual-user grants are reserved for two named cases: (a)
  a research or sandbox owner on their own schema in the
  Research / Sandbox catalog (§ 1.3.4), and (b) time-boxed
  controlled exceptions logged in the register (§ 3.3) — most
  commonly named restricted humans (§ 1.3.5) and Ops / L3
  data-fix activity (§§ 1.3.1–1.3.3 and § 1.3.5; § 1.3.4
  has no data-fix exception path — the owner fixes their own
  workspace).
- **No secondary grants.** Grantees may not GRANT onward; all grants
  originate from the catalog owner.
- **Least privilege on the grain.** Prefer table-grain SELECT over
  schema-grain SELECT; prefer schema-grain over catalog-grain.

### Part 2: Lakehouse vs. direct-to-BOR consumption

> **Scope note.** Enumeration of concrete consumption mechanisms
> (direct query, materialized views, Delta Sharing, extract, API) is
> out of scope. This part covers the prior question: *should the
> consumer read from the lakehouse at all, or go direct to the Book of
> Record?*

Not every consumer should read from the lakehouse. Reading from the
lakehouse adds a hop, a freshness lag, and a shared dependency; it is
only justified when the lakehouse adds value the consumer would
otherwise have to build themselves.

**Principle.** A consumer should read from the lakehouse **if and only
if** the lakehouse provides a value-add on top of the Book of Record
(BOR) that the consumer needs, **and** the resulting freshness is
within the consumer's tolerance. Otherwise, the consumer should read
directly from the BOR and apply their own transformations.

Recognized lakehouse value-adds:

- **Integration.** Multiple BORs unioned or joined into a single
  domain-aligned view that the consumer would otherwise have to
  reconstruct.
- **History.** Bitemporal / SCD2 history beyond what the BOR retains
  (e.g., BOR keeps current-state only; lakehouse keeps as-of
  history — see `rfd/0008/common/bi-temporal.md` for the reference
  pattern; RFD 0010 owns lake versioning but not the SCD2 / as-of
  contract itself).
- **Reconciliation.** Cross-source keying, deduplication, or master-data
  resolution already performed in the domain-aligned model.
- **Governance.** Contract-bound schema, quality checks, and access
  controls that the BOR does not enforce, and that the consumer would
  otherwise have to replicate.
- **Scale / cost.** The BOR cannot serve the consumer's query volume,
  or the lakehouse read is materially cheaper at the required volume.
- **Decoupling.** The consumer must not couple to BOR availability or
  BOR schema churn.

If none of the above applies and the BOR is directly reachable within
policy, **direct-to-BOR is the right answer.** The lakehouse is not a
mandatory hop.

##### Decision rule

Choose lakehouse consumption if **all four** hold:

1. At least one recognized value-add above applies to this consumer.
2. Lakehouse freshness is **inside** the consumer's freshness
   tolerance. The freshness figure comes from the Curated
   model's ODCS contract (RFD 0009) — specifically its
   **Timeliness** data-quality dimension per RFD 0019, which
   owns how freshness is expressed as a contract dimension. If
   the contract does not publish a Timeliness SLA the gate
   cannot be evaluated and Curated is not eligible.
3. The consumer is **eligible to be authorized** to read the
   relevant Curated catalog under § 1.3 — i.e., a grant exists or
   can be granted per the § 1.3.3 access template. Whether the
   grant is already in place is a mechanism question, not a
   design gate.
4. The lakehouse value-add(s) **outweigh the coupling cost** of
   the extra hop — the added freshness lag, the shared
   dependency, and the operational tie to Curated's release
   cadence. This is qualitative but explicit: if the value-add is
   marginal and the consumer already owns the BOR, direct-to-BOR
   is the right answer even when conditions 1–3 hold.

Otherwise, choose direct-to-BOR. When direct-to-BOR is chosen, the
consumer owns the transformation logic and any resulting divergence
from lakehouse-derived numbers — this divergence must be acknowledged
in the consumer's own contract or documentation.

##### Selection matrix

*Illustrative, not exhaustive.* The four-condition rule above is
the normative gate; this table applies it to common shapes.

| Situation | Read from | Rationale |
|---|---|---|
| Consumer needs BOR data as-is, near-real-time, and can query the BOR directly | **BOR** | No value-add; lakehouse hop adds only lag |
| Consumer needs multiple BORs joined into one domain view | **Lakehouse (Curated)** | Integration value-add |
| Consumer needs point-in-time history the BOR does not retain | **Lakehouse (Curated)** | History value-add (bi-temporal reference: `rfd/0008/common/bi-temporal.md`) |
| Consumer needs a contract-bound schema they can pin against | **Lakehouse (Curated)** | Governance value-add (RFD 0009); contract binding only exists in Curated |
| Consumer needs sub-second latency the lakehouse cannot meet | **BOR** (or a dedicated serving layer outside UC) | Freshness gate fails |
| Consumer's read volume would overload the BOR | **Lakehouse (Curated)** | Scale value-add; protects BOR |
| Consumer is a BI dashboard on curated financials | **Lakehouse (Curated)** | Integration + governance value-add; consumer-aligned outputs live in Curated |
| Consumer is an operational app that already owns the BOR | **BOR** | Value-add does not exceed coupling cost |

##### Recording the decision

The consumer's Phase 3 Design (RFD 0002) records the choice:

- If **lakehouse**: cite the value-add(s) from the list above and
  the Curated object being read.
- If **direct-to-BOR**: cite which value-add(s) do not apply and
  acknowledge ownership of the resulting transformation logic.

This is an explicit design step, not a default. "We always read from
the lakehouse" and "we always read from the BOR" are both anti-patterns
— the choice is per consumer per use case.

### Part 3: Standards vs. exceptions

#### 3.1 What is a standard

A **standard** is a design that conforms to the catalog topology
(Part 1) and applies the lakehouse-vs-BOR decision rule (Part 2)
honestly. Standards do not require per-product approval — a team
following the standards proceeds through the DPLC without additional
governance touchpoints.

#### 3.2 What is an exception

An **exception** is any of the following:

- Catalog placement that violates § 1.2 (e.g., a research or
  sandbox dataset written directly into a Curated catalog to
  avoid promotion overhead, bypassing the DPC + Application
  publication path).
- Access model that violates § 1.3 (e.g., a human account granted
  **standing** write access to a production catalog, or ALL PRIVILEGES
  on any production scope). Time-boxed human data-fix writes are
  called out separately below.
- **Human data-fix writes** to any production catalog or schema —
  Source-aligned, Application, Curated, or an escalation Regulated
  schema — always an exception (per § 1.3.1 – § 1.3.3 and
  § 1.3.5), even when
  routed correctly through the controlled-exception workflow. The
  exception log is the audit trail; recurring fixes must be lifted
  into the producing pipeline.
- Lakehouse consumption where no § 2 value-add applies ("lakehouse
  hop for its own sake"), or direct-to-BOR consumption where the
  consumer needs a value-add the lakehouse already provides.
- Use of the **escalation Regulated schema** (§ 1.3.5) — always an
  exception because the schema-isolation triggers vary per dataset
  and require compliance sign-off. The default in-schema mode
  (§ 1.3.5) is **not** an exception; it is the standard treatment for
  regulated data.
- Use of a **separate Regulated catalog** — a rarer sub-exception on
  top of the escalation-schema exception, and only when schema-level
  isolation demonstrably cannot meet the compliance requirement
  (§ 1.3.5).

#### 3.3 Exception process

Exceptions are recorded and reviewed, not blocked:

1. **Declare** the exception in the product's Phase 3 Design artifact
   using an `exceptions:` block that names the standard being deviated
   from, the reason, and the compensating control.
2. **Review** in the DPLC design review. The reviewer records
   acceptance, rejection, or "accept with sunset date".
3. **Track** accepted exceptions in a per-domain register (path TBD
   during discussion). The register is read by the build preflight so
   CI does not flag the exception as a violation. **Interim path
   until the register and preflight are wired up:** accepted
   exceptions are recorded in the product's Phase 3 Design artifact
   under an `exceptions:` block, and the build preflight treats a
   Design-declared exception as accepted so CI does not block. This
   manual path is superseded once the register and preflight-reader
   ship.
4. **Revisit** every accepted exception at least annually, or when the
   standards catalog changes in a way that could subsume it.

#### 3.4 Anti-patterns (always rejected)

The following are not exceptions — they are rejected outright. Teams
encountering these should redesign, not request an exception:

- Writing to another team's Curated catalog.
- Ad-hoc human reads on a Source-aligned catalog without a declared
  consumption need — Source-aligned catalogs are internal to their
  ingestion program (§ 1.3.1). Scoped SP or contract-driven access is
  the sharing model.
- Storing PII or MNPI in a production tier — including
  Source-aligned, **Application**, and Curated catalogs — without
  the § 1.3.5 fine-grained controls (table ACLs + row filters +
  column masks + tag-based policy + audit). For § 3 purposes
  Application is a production tier (§ 1.3.2 runs a real
  pipeline and permits regulated content under § 1.3.5).
  Research / Sandbox is not a default landing spot for regulated
  data (§ 1.3.4); the exception-only allowance there carries the
  same § 1.3.5 controls.
- Granting `ALL PRIVILEGES` on a production catalog to any principal
  other than that catalog's owning producer SP (§ 1.3.6).
- Cross-catalog copy jobs that duplicate curated data instead of
  reading it in place (violates single-source-of-truth).
- Reading an Application catalog table from a downstream
  production pipeline (Curated, another Application catalog, or
  a consumer-aligned product built in Curated) — Application
  catalogs are pre-publication (§ 1.3.2); cross-team
  consumption goes through the deep-clone publication path
  only. This is enforced by the § 1.3.2 grant model
  (*Downstream production SPs — No access*), but is listed here
  because § 3.1 makes standards self-service and the reader
  needs to see it enumerated in Part 3.

## Impact

**Domain teams.**

- Every existing data product is classified into a catalog tier.
  Products already conforming need no change; products in the wrong
  tier are migrated on a scheduled path (not a big-bang cutover).
- Phase 3 Design gains a required `catalog_tier:` declaration and,
  for consumer designs, an explicit lakehouse-vs-BOR record. Phase 4
  build preflight validates the declaration.
- The `caspian-core` schema routing macros are updated to enforce
  placement rules. Domain teams update the pinned version.

**Platform team.**

- Owns the catalog topology (§ 1.1) as governance artifact:
  provisioning, naming, and access model per tier.
- Owns the lakehouse-vs-BOR decision rule and its value-add list
  (§ 2); amendments go through RFD updates.
- Owns the exception register format and the tooling that reads it
  during CI.

**Consumers.**

- Every consumer records its lakehouse-vs-BOR choice with cited
  value-add(s) or acknowledged transformation ownership.
- Cross-domain lakehouse consumption still follows the RFD 0003
  cross-domain sources mechanism; today's ad-hoc cross-catalog
  reads are migrated to declared sources.

**Migration.**

- Existing products are inventoried and tagged with a catalog tier;
  gaps are recorded as exceptions with sunset dates.
- No production data movement is required for the initial adoption —
  existing placements are grandfathered as exceptions and revisited
  on the annual cycle.
- New products built after this RFD is `published` must conform on
  day one.

**Open questions for discussion.**

- **Exact naming convention for catalogs** (§ 1.1 note). Two specific
  sub-questions:
  - *Parseability.* With `_` used as both the separator and an
    intra-segment character, `prd_curated_pricing_valuation` cannot be
    split back into `<env>` / `<tier>` / `<domain-or-program>`
    reliably. If CI validation, the exception register, or routing
    macros need to derive the tier from the catalog name, either the
    tier tokens must come from a fixed vocabulary or a reserved
    separator (e.g., `__`) must delimit segments.
  - *Environments.* Whether the `<env>` prefix implies every tier
    exists in every environment. § 1.3 today reads as prod-focused;
  research and sandbox schemas in § 1.3.4 are **prod-hosted only**
  (typically a single prod catalog per team/user, not replicated
  as `dev_*` / `sqa_*` variants); the Regulated pattern (§ 1.3.5)
  is only
    meaningful where regulated data physically lands. This needs to
    be stated per tier.
- **Controlled business-human read on Source-aligned tables.**
  § 1.3.1 today grants business humans **no standing access** — they
  read from Curated. Should we allow standing SELECT via **AD groups**
  on named Source-aligned tables (scoped per source schema, with the
  same fine-grained controls of § 1.3.5 applied where sensitivity
  warrants)? Arguments **for**: analysts often need source-level
  reconciliation against Curated, and some exploratory questions
  cannot be answered from the canonical model alone. Arguments
  **against**: source data is neither reconciled nor contract-bound,
  upstream schema churn can silently break business dashboards, and
  standing human reads on source data weaken the "read from Curated"
  default. If accepted, the model would be an AD-group grant per
  source schema, named use cases documented in the ingestion
  program's consumer list, and sensitive columns masked / rows
  filtered per § 1.3.5.
- **Source-aligned catalog granularity.** Whether each source system
  gets its own catalog (`prd_src_<system>`) or several related source
  systems share a catalog with schema-per-source. Each Unity Catalog
  catalog is attached to a single physical storage location, so a
  high-throughput source may benefit from its own catalog even when
  naming and permissioning could work at schema grain. The trade-off
  is **physical storage / S3 throttling and lifecycle isolation**
  (favoring one-catalog-per-source) vs **catalog-count sprawl and
  operational overhead** (favoring one-catalog-many-schemas). Either
  way, § 1.3.1 requires one schema per source system.
- **Access enforcement mechanism** — the technical means by which each
  § 1.3 grant is realized (service-principal vs group, auth type such
  as OAuth M2M vs personal SSO, controlled-exception / break-glass
  tooling, and additional controls such as MFA, network restriction,
  or approval-workflow specifics for regulated data — both the
  default in-schema mode and the escalation Regulated schema).
  Deferred to a Security & Secrets follow-on once the model in § 1.3
  is agreed.
- Location of the per-domain exception register (§ 3.3).
- Interaction with the future Security & Secrets RFD (RFD 0003
  § secret management interim rules) for regulated data in both modes.
- Whether Research / Sandbox catalogs are per-user, per-team,
  or per-line-of-business.
- **Application / Incubation catalog scoping and opt-in.**
  § 1.3.2 introduces Application catalogs as a first-class tier for
  app-team incubation, but two sub-questions remain: (a) whether the
  Application catalog is scoped per app team, per product, or per
  repo — mirroring the Research / Sandbox scoping question
  above; and (b)
  whether Application catalog use is mandatory for all new data
  products or opt-in per team. Building directly in a Curated schema
  under a `_dev` naming convention is the alternative; the trade-off
  is per-team overhead of a second catalog vs clearer separation from
  contract-bound production and the ability to enforce no-downstream-
  reads in routing macros.
- **Data-product registry tooling.** `DBX-UC-002` names the
  registry as the authority for catalog assignment, but the
  registry itself and the CI check that validates dbt targets
  against it do not yet exist in this repo. Where the registry
  lives (this repo vs. a platform repo), its schema, and how
  `caspian-core` reads it at compile time are open.
- **MNPI tag key.** `DBX-UC-005` (severity error) fixes the
  regulated-data tag schema as `data_classification`
  (`public|internal|confidential|restricted`) + `pii`
  (`true` / `false`) and does not include MNPI. § 1.3.5 in this
  RFD calls out MNPI as a distinct sensitivity class. Two
  candidate resolutions, both amendments to `DBX-UC-005`
  rather than 0022: (a) add an `mnpi` boolean key parallel to
  `pii`; (b) reserve a `data_classification` value (e.g.,
  `restricted-mnpi`) — approach (a) is easier to filter on
  and does not overload the classification enum. Open on the
  0008 side.
