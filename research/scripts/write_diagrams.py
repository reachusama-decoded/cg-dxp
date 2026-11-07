#!/usr/bin/env python3
"""Write the Mermaid sources for every whiteboard diagram into courseware/common/diagrams/src/.
Rule: few words per node; the explanation lives in the notebook bullets next to the figure.
Render with courseware/common/diagrams/render.sh."""
import pathlib, textwrap
ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "courseware/common/diagrams/src"
SRC.mkdir(parents=True, exist_ok=True)
for old in SRC.glob("*.mmd"):
    old.unlink()
STYLE = """
classDef blue fill:#C9DAF8,stroke:#434343,color:#1a1a1a
classDef yellow fill:#FFF2CC,stroke:#434343,color:#1a1a1a
classDef focus fill:#F8DB59,stroke:#434343,color:#1a1a1a
classDef green fill:#D9EAD3,stroke:#434343,color:#1a1a1a
classDef aqua fill:#D0E0E3,stroke:#434343,color:#1a1a1a
classDef grey fill:#F3F3F3,stroke:#434343,color:#1a1a1a
classDef red fill:#F4CCCC,stroke:#434343,color:#1a1a1a
"""
D = {}
D["week-map"] = """
flowchart LR
  D1["Day 1<br/>Design"] --> D2["Day 2<br/>Platform"] --> D3["Day 3<br/>dbt"] --> D4["Day 4<br/>Airflow"] --> D5["Day 5<br/>Capstone"]
  D1 -.- A1["PRD + contract"]
  D2 -.- A2["STTM, SLAs,<br/>container, generated code"]
  D3 -.- A3["tested pipeline"]
  D4 -.- A4["scheduled DAG"]
  D5 -.- A5["your data product"]
  class D1,D2,D3,D4 blue
  class D5 focus
  class A1,A2,A3,A4,A5 grey
"""
D["d1-personas"] = """
flowchart TB
  C["Consumers"] --> X
  O["Business data owners"] --> X
  P["Platform providers<br/>(the paved path)"] --> X
  X["Data product creator"] --> R["Trusted, reusable<br/>products in the catalog"]
  class C,O,P blue
  class X focus
  class R green
"""
D["d1-three-views"] = """
mindmap
  root((A data product))
    Promises
      trusted, reusable, accessible
      written in a contract
      enforced by tests and code
    Assets
      data
      code
      infrastructure
    Alignment
      source-aligned: their shape
      consumer-aligned: our decision
      about people, not code
"""
D["d1-alignment"] = """
flowchart LR
  S["Source-aligned<br/>their shape"] -->|rules| M["Domain-aligned<br/>one meaning"] -->|shaped for<br/>the decision| C["Consumer-aligned"]
  P["Promises enforced:<br/>tests, schedules, owners"] -.-> C
  N["Not a product:<br/>a bare file, a stranded extract"]
  class S grey
  class M blue
  class C focus
  class P green
  class N red
"""
D["d1-triage"] = """
flowchart TD
  Q1["Who needs it?<br/>Which decision?"] --> Q2["Does it exist?<br/>What do people do today?"] --> Q3["Can we build it?"] --> Q4["Is it worth it?"]
  Q4 -->|yes| B["Design it"]
  Q4 -->|exists| R["Reuse it"]
  Q4 -->|no| S["Stop"]
  class Q1,Q2,Q3,Q4 yellow
  class B focus
  class R green
  class S grey
"""
D["d1-value-adoption"] = """
mindmap
  root((Build it?))
    Costs
      ownership and maintenance
      opportunity cost
      licences and data
      SME and alignment time
      adoption
    Payoffs
      consistency
      time saved
      new opportunities
      trust and scale
      lower transaction costs
    Barriers
      integration
      low trust
      liability
      awareness, training
      cost of change
    Responses
      leadership takes the risk
      show it working
      train, document
      deadlines
      follow through
"""
D["d1-catalyst"] = """
flowchart TB
  subgraph tiers ["Catalyst skills"]
    direction TB
    O["Orchestrators<br/>dplc-concierge"] --> W["Workflow<br/>source / domain / consumer-aligned"] --> Dd["Document<br/>PRD, data contract, runbook"] --> Cp["Capability<br/>query-catalog, write-dbt-model"]
  end
  subgraph phases ["Nine lifecycle phases"]
    direction LR
    P0["0 prereq"] --> P1["1 triage"] --> P2["2 discovery"] --> P3["3 design"] --> P4["4 build"] --> P5["5 validate"] --> P6["6 publish"] --> P7["7 operate"] --> P8["8 evolve"]
  end
  class O grey
  class W aqua
  class Dd focus
  class Cp green
  class P0,P1,P2,P3 yellow
  class P4,P5,P6 blue
  class P7,P8 green
"""
D["d1-harness"] = """
sequenceDiagram
  participant You
  participant H as Harness (Copilot, Claude Code)
  participant M as Model
  participant T as Tools
  You->>H: prompt + skill + context
  H->>M: the whole conversation
  M-->>M: hidden reasoning
  M->>H: tool call (JSON)
  H->>T: run it
  T->>H: result
  H->>M: result appended
  M->>H: answer
  H->>You: artefact
  Note over You,T: harness plus model is an agent, and a skill steers the model
"""
D["d1-interview"] = """
flowchart LR
  P["Producer<br/>knows the source"] --> Cr
  Cn["Consumer<br/>knows the decision"] --> Cr
  Cr["Creator<br/>asks the seven questions"] --> T["Transcript"] --> PRD["PRD"] --> DC["Data contract"] --> Rv["Review:<br/>find the invented detail"]
  class P,Cn blue
  class Cr focus
  class T,PRD,DC grey
  class Rv yellow
"""
D["d1-discovery-methods"] = """
flowchart LR
  I["Interview<br/>dynamic"] --> X
  O["Observe<br/>what they really do"] --> X
  S["Survey<br/>scales"] --> X
  R["Read docs and code<br/>what exists"] --> X
  X["A product they adopt"]
  class I focus
  class O,S,R blue
  class X green
"""
D["d1-ai-foundations"] = """
flowchart LR
  subgraph training ["Training"]
    direction TB
    C["Corpus"] --> PT["Pre-training<br/>(compression)"] --> IT["Instruction tuning"] --> RL["Preference tuning"]
  end
  subgraph inference ["Inference"]
    direction TB
    Pr["Prompt =<br/>whole conversation"] --> Re["Hidden reasoning"] --> Co["Completion<br/>or tool call"]
  end
  RL --> Pr
  W["Context window fills:<br/>summarise, start fresh"] -.-> Pr
  class C,PT,IT,RL blue
  class Pr,Re,Co yellow
  class W grey
"""
D["d2-sttm"] = """
flowchart LR
  A["Vendor prices"] --> R
  B["Instrument master"] --> R
  F["FX rates"] --> R
  R["Rules per column<br/>direct · constant · lookup<br/>aggregate · derive<br/>+ row rules: dedup, filter"] --> T["rpt_eod_prices_us<br/>one row per instrument<br/>per business date"]
  class A,B,F grey
  class R focus
  class T green
"""
D["d2-service-levels"] = """
flowchart LR
  SLI["SLI<br/>what you measure"] --> SLO["SLO<br/>the ideal"] --> SLA["SLA<br/>the agreed tolerance"] --> Cq["Consequence<br/>notify, explain, escalate"]
  class SLI blue
  class SLO yellow
  class SLA focus
  class Cq green
"""
D["d2-warehouse-lake-lakehouse"] = """
flowchart TB
  subgraph W ["Data warehouse"]
    direction TB
    W1["Tables, SQL, ACID"] --- W2["Proprietary storage"] --- W3["Costly to scale,<br/>structured only"]
  end
  subgraph L ["Data lake"]
    direction TB
    L1["Files in object storage<br/>(S3), any format"] --- L2["Cheap, scales"] --- L3["No guarantees:<br/>the swamp"]
  end
  subgraph H ["Lakehouse"]
    direction TB
    H1["Files in object storage"] --- H2["+ open table format<br/>(Delta): ACID, versions"] --- H3["+ SQL engine (Spark)<br/>+ governance (Unity Catalog)"]
  end
  W --> H
  L --> H
  class W1,W2,W3 grey
  class L1,L2,L3 yellow
  class H1,H2 blue
  class H3 focus
"""
D["d2-databricks-under-the-hood"] = """
flowchart TB
  subgraph src ["Sources"]
    direction LR
    S1["Vendor files"]
    S2["Databases"]
    S3["Streams, APIs"]
  end
  subgraph ing ["Ingestion"]
    direction LR
    I1["Auto Loader / COPY INTO"]
    I2["dbt seed, notebooks"]
    I3["Kafka, Lakeflow"]
  end
  subgraph sto ["Storage: S3"]
    direction LR
    D1["Delta tables<br/>Parquet + _delta_log"]
  end
  subgraph eng ["Compute: Databricks"]
    direction LR
    E1["Spark clusters"]
    E2["SQL warehouses<br/>(Photon)"]
  end
  subgraph gov ["Governance"]
    G1["Unity Catalog<br/>catalog.schema.table<br/>permissions, lineage"]
  end
  subgraph use ["Consumers"]
    direction LR
    U1["dbt"]
    U2["Notebooks, BI"]
    U3["Marketplace, APIs"]
  end
  src --> ing --> sto
  sto <--> eng
  gov -.-> sto
  gov -.-> eng
  eng --> use
  class S1,S2,S3 grey
  class I1,I2,I3 aqua
  class D1 focus
  class E1,E2 blue
  class G1 green
  class U1,U2,U3 yellow
"""
D["d2-delta-format"] = """
flowchart LR
  subgraph T ["A Delta table (a folder in S3)"]
    direction TB
    P1["part-0001.parquet"]
    P2["part-0002.parquet"]
    P3["part-0003.parquet"]
    LG["_delta_log/<br/>000.json  000.json<br/>001.json  002.json"]
  end
  LG -->|gives| A["ACID commits"]
  LG -->|gives| V["Versions,<br/>time travel"]
  LG -->|gives| M["MERGE, UPDATE,<br/>DELETE"]
  LG -->|gives| S["Schema enforcement"]
  O["OPTIMIZE / ZORDER:<br/>compact and co-locate"] -.-> P1
  class P1,P2,P3 grey
  class LG focus
  class A,V,M,S green
  class O yellow
"""
D["d2-spark-engine"] = """
flowchart LR
  Q["dbt model (SQL)"] --> Pl["Driver<br/>plans the query"]
  Pl --> E1["Executor"]
  Pl --> E2["Executor"]
  Pl --> E3["Executor"]
  E1 --> F1["partition<br/>of files"]
  E2 --> F2["partition<br/>of files"]
  E3 --> F3["partition<br/>of files"]
  F1 --> R["Result:<br/>a Delta table"]
  F2 --> R
  F3 --> R
  N["Many machines,<br/>one query.<br/>Databricks runs it;<br/>you write SQL."] -.-> Pl
  class Q yellow
  class Pl focus
  class E1,E2,E3 blue
  class F1,F2,F3 grey
  class R green
  class N aqua
"""
D["d2-tools-together"] = """
flowchart LR
  Ca["Catalyst<br/>generates"] --> Dc["Dev container<br/>(Docker)"]
  Dc --> G["GitHub<br/>pull request"]
  G -->|merge| H["Harness<br/>CI/CD"]
  H -->|deploys| Af["Airflow on Astro"]
  Af -->|Cosmos| dbt["dbt"]
  dbt -->|SQL| Db["Databricks<br/>(Spark)"]
  Db --> Dl["Delta on S3"]
  Dl --> UC["Unity Catalog"]
  UC --> Mk["Marketplace"]
  Af -.->|metrics, alerts| Dd["Datadog"]
  Db -.-> Dd
  class Ca,Dc,G aqua
  class H yellow
  class Af,dbt,Db blue
  class Dl focus
  class UC,Mk green
  class Dd red
"""
D["d2-scheduled-run"] = """
sequenceDiagram
  participant S as Airflow scheduler
  participant C as Cosmos task
  participant D as dbt
  participant B as Databricks (Spark)
  participant L as Delta on S3
  participant M as Datadog
  S->>C: 06:00, run due
  C->>D: dbt run --select model
  D->>B: compiled SQL
  B->>L: read inputs, write table
  L-->>B: commit v+1
  B-->>D: rows, status
  D-->>C: success / failure
  C-->>S: task state
  S->>M: metrics, failure event
"""
D["d2-data-systems"] = """
timeline
  title From files to the lakehouse
  1950s : File systems. No structure, every program knows every file.
  1970 : Relational databases. Tables, keys, ACID.
  1990s : Non-relational. Faster, by dropping the guarantees.
  2000s : Internet scale. Many machines, files in the cloud (S3), Hadoop.
  2014 : Spark. Fast queries over files; a data lake.
  Now : Lakehouse. Delta on S3 queried by Databricks. Tables and ACID are back.
"""
D["d2-docker"] = """
flowchart LR
  Df["Dockerfile<br/>FROM · WORKDIR · COPY · CMD"] -->|docker build| Im["Image"]
  Im -->|docker run| C1["Container"]
  Im -->|docker run| C2["Container"]
  Im -->|docker push| Rg["Registry"]
  Dv["Dev container:<br/>VS Code inside"] -.-> C1
  class Df yellow
  class Im focus
  class C1,C2 blue
  class Rg,Dv grey
"""
D["d2-dbt-flow"] = """
flowchart LR
  M["SELECT per model<br/>+ Jinja"] -->|dbt run| W["CREATE VIEW / TABLE<br/>in order"]
  Y["YAML:<br/>sources, tests, config"] --> W
  W --> T["Tests:<br/>zero rows = pass"]
  subgraph layers [" "]
    direction LR
    St["staging"] --> In["intermediate"] --> Ma["marts"]
  end
  class M,Y yellow
  class W focus
  class T green
  class St,In,Ma blue
"""
D["d2-contract-to-code"] = """
flowchart LR
  Ctr["Contract + STTM + SLAs"] --> Sk["Catalyst skills"]
  Sk --> P["dbt project + tests"]
  Sk --> Dg["Airflow DAG"]
  P -->|dbt build| Tb["Tables in your schema"]
  Dg -->|astro dev start| Ru["A scheduled run"]
  Rv["You review every line"] -.-> P
  Rv -.-> Dg
  class Ctr focus
  class Sk aqua
  class P,Dg blue
  class Tb,Ru green
  class Rv yellow
"""
D["d3-pipeline"] = """
flowchart LR
  subgraph src ["sources"]
    H["holdings_raw"]
    Po["positions_raw"]
    Pr["prices_raw"]
    Fx["fx_rates_raw"]
    Fm["fund_master_raw"]
  end
  subgraph stg ["staging (views)"]
    SH["stg_holdings"]
    SP["stg_positions"]
    SPr["stg_prices"]
    SF["stg_fx_rates"]
    SFm["stg_funds"]
  end
  subgraph int ["intermediate (views)"]
    IH["int_holdings_enriched"]
    IP["int_positions_dated"]
    IF["int_fund_attributes"]
  end
  subgraph marts ["marts (tables)"]
    F["fct_portfolio_returns"]
    A["agg_fund_exposure"]
    AD["agg_fund_daily_exposure"]
  end
  H --> SH --> IH
  Pr --> SPr --> IH
  Fx --> SF --> IH
  Po --> SP --> IP
  Fm --> SFm --> IF
  IH --> F
  IF --> F
  IH --> A
  IF --> A
  A --> AD
  T["tests"] -.-> marts
  class H,Po,Pr,Fx,Fm grey
  class SH,SP,SPr,SF,SFm aqua
  class IH,IP,IF blue
  class F,A,AD focus
  class T green
"""
D["d3-materialisations"] = """
flowchart TB
  Cfg["dbt_project.yml per folder<br/>or config() in the model"] --> V["view<br/>built on read"]
  Cfg --> Tb["table<br/>written at build"]
  Cfg --> Inc["incremental<br/>new rows only"]
  Cfg --> Sn["snapshot<br/>SCD type 2 history"]
  class V aqua
  class Tb focus
  class Inc blue
  class Sn yellow
  class Cfg grey
"""
D["d3-commands"] = """
flowchart LR
  Dg["dbt debug"] --> Sd["dbt seed"] --> Rn["dbt run"] --> Ts["dbt test"] --> Dc["dbt docs"]
  Bd["dbt build<br/>run + test, in graph order"] -.-> Rn
  Sel["--select<br/>model · tag:layer · +upstream · downstream+"] -.-> Rn
  class Dg,Sd,Rn,Ts,Dc blue
  class Bd focus
  class Sel grey
"""
D["d3-catalogs"] = """
flowchart LR
  Src["Source-aligned catalog<br/>ingested feeds"] --> App["Application catalog<br/>your workspace: build here"]
  App -->|DQ rules pass,<br/>blueprint copies| Dom["Domain catalog<br/>curated, shared"]
  Dom --> Mk["Marketplace"]
  Acc["Access by group;<br/>contract (ODCS) records it"] -.-> Dom
  class Src grey
  class App yellow
  class Dom focus
  class Mk green
  class Acc aqua
"""
D["d3-airflow-federation"] = """
flowchart LR
  Old["One central Airflow<br/>~12,000 DAGs"] --> New["Astro per team<br/>vended from a template"]
  New --> A1["Team A"]
  New --> A2["Team B"]
  A1 -->|asset event| K["Platform plugin<br/>+ Kafka"] -->|subscribe| A2
  class Old red
  class New focus
  class A1,A2 blue
  class K aqua
"""
D["d4-bitemporal-rows"] = """
flowchart TB
  R1["v1 · day 1 file<br/>tenure 53<br/>business: 02 Nov →<br/>system: t1 → t2"] -->|"day 2: changed"| R2["v1 carried forward<br/>tenure 53<br/>business: 02 Nov → 02 Nov<br/>system: t2 → open"]
  R1 --> R3["v2 · day 2 file<br/>title wrong, tenure 54<br/>business: 03 Nov →<br/>system: t2 → t3"]
  R3 -->|"correction, same date"| R4["v2 corrected<br/>business: 03 Nov →<br/>system: t3 → open<br/>current"]
  Q1["as of 02 Nov"] -.-> R2
  Q2["as was at t2.5"] -.-> R3
  Q3["as is"] -.-> R4
  class R1 grey
  class R2 blue
  class R3 red
  class R4 focus
  class Q1,Q2,Q3 yellow
"""
D["d4-dag"] = """
flowchart LR
  S["start"] --> F["source_freshness_check"] --> G
  subgraph G ["dbt_pipeline (Cosmos)"]
    direction LR
    St["staging"] --> In["intermediate"] --> Ma["marts"] --> Te["tests"]
  end
  G --> P["publish_to_catalog"] --> E["end"]
  Cb["callbacks:<br/>failure → Datadog + Teams<br/>retry → ticket<br/>SLA miss → Teams"] -.-> G
  Sc["schedule 06:00 weekdays<br/>retries 2, backoff"] -.-> S
  class S,E grey
  class F yellow
  class St,In,Ma,Te blue
  class P focus
  class Cb red
  class Sc aqua
"""
D["d4-airflow-components"] = """
flowchart LR
  Dp["DAG processor<br/>parses dags/"] --> Db[("Metadata DB")]
  Sc["Scheduler<br/>what is due"] --> Db
  Wk["Workers<br/>run tasks"] --> Db
  Tr["Triggerer<br/>deferred waits"] --> Db
  Ui["API server + UI"] --> Db
  Loc["astro dev start:<br/>all of these<br/>on your laptop"] -.-> Dp
  Cl["Astro hosted:<br/>the same, run for you"] -.-> Sc
  class Dp,Sc,Wk,Tr,Ui blue
  class Db focus
  class Loc,Cl grey
"""
D["d4-cicd"] = """
flowchart LR
  B["feature branch"] --> PR["pull request<br/>review"] --> Mg["merge"]
  Mg -->|webhook| H["Harness pipeline"]
  H --> SQA["SQA<br/>shared: check who<br/>deployed last"]
  SQA --> PRD["Production<br/>release branch + CRQ"]
  PRD --> As["Astro + Databricks"]
  Hs["Git history =<br/>what was live"] -.-> Mg
  class B,PR aqua
  class Mg yellow
  class H focus
  class SQA,PRD blue
  class As green
  class Hs grey
"""
D["d4-blueprints"] = """
flowchart LR
  Y["YAML<br/>in the dataset folder"] --> Bp["Blueprint<br/>Python template<br/>by the platform team"] --> Dg["A DAG in<br/>your Astro"] -->|triggers| Job["Databricks job<br/>dbt deps · seed · run · test"]
  Py["Custom Python DAG<br/>when nothing fits"] -.-> Dg
  class Y yellow
  class Bp focus
  class Dg blue
  class Job green
  class Py grey
"""
D["d5-atlas-pipeline"] = """
flowchart LR
  seed["7 seeds"] --> src["src_*<br/>source-aligned"]
  src --> dt["dom_trading__trade"]
  src --> dd["dom_* dimensions"]
  dt --> lp["dom_trading__latest_price"]
  dt --> gp["dom_positions__position"]
  dd --> gp
  lp --> gp
  gp --> ps["rpt_portfolio_summary"]
  ps --> ab["rpt_advisor_book"]
  ps --> sa["agg_segment_aum"]
  lp --> alp["api_latest_price"]
  dt --> ts["ts_daily_market"]
  dt --> ia["agg_instrument_activity"]
  dd --> fn["agg_fund_nav"]
  lp --> fn
  class seed grey
  class src aqua
  class dt,dd,lp,gp blue
  class ps,ab,sa,alp,ts,ia,fn focus
"""
D["d5-atlas-erd"] = """
erDiagram
  CLIENTS ||--o{ PORTFOLIOS : owns
  ADVISORS ||--o{ PORTFOLIOS : manages
  PORTFOLIOS ||--o{ TRADES : places
  INSTRUMENTS ||--o{ TRADES : traded
  FUNDS ||--o{ FUND_HOLDINGS : holds
  INSTRUMENTS ||--o{ FUND_HOLDINGS : weighted
  TRADES {
    int trade_id PK
    int ts
    int portfolio_id FK
    int instrument_id FK
    string side
    int qty
    int price_cents
    int fee_bps
  }
  INSTRUMENTS {
    int instrument_id PK
    string ticker
    string asset_class
    string ccy
  }
  PORTFOLIOS {
    int portfolio_id PK
    int client_id FK
    int advisor_id FK
    string strategy
  }
  CLIENTS {
    int client_id PK
    string segment
  }
  ADVISORS {
    int advisor_id PK
    string region
  }
  FUNDS {
    int fund_id PK
    string style
  }
  FUND_HOLDINGS {
    int fund_id FK
    int instrument_id FK
    decimal weight_pct
  }
"""
D["d5-capstone-day"] = """
timeline
  title Friday: the Atlas capstone
  9.00 : Brief. Read the README alone.
  9.15 : Table discovery, 45 to 60 minutes. Playback.
  10.15 : Phase 1 baseline, every team. 2 to 3 hours.
  13.00 : Phase 2 extensions. Flexible lunch; back by 13.30.
  13.45 : Presentations, 2 to 3 minutes per table.
  14.00 : Close.
"""
D["d5-alignment-naming"] = """
flowchart LR
  S["src_producer__entity<br/>source-aligned"] --> Dm["dom_domain__entity<br/>domain-aligned"] --> C["rpt_ · agg_ · ts_ · api_<br/>consumer-aligned"]
  M["Older names:<br/>raw / staging / curated,<br/>bronze / silver / gold"] -.-> Dm
  class S grey
  class Dm blue
  class C focus
  class M yellow
"""
for name, body in D.items():
    text = textwrap.dedent(body).strip() + "\n"
    if text.startswith("flowchart") and "classDef" not in text:
        text = text + STYLE.strip() + "\n"
    (SRC / f"{name}.mmd").write_text(text)
print(f"{len(D)} diagram sources in {SRC}")
