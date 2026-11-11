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
D["d2-compose"] = """
flowchart LR
  L["Your laptop<br/>curl localhost:8000"] -->|"127.0.0.1:8000 → 8000<br/>the one published port"| A
  subgraph N["eod_backend: the project's private network"]
    direction LR
    A["api<br/>queries by name"] -->|"db:5432"| Db["db<br/>Postgres, no ports:"]
  end
  X["Any other container<br/>default network"] -.->|"db? no such host"| Db
  class L yellow
  class A blue
  class Db focus
  class X grey
"""
D["d2-git"] = """
flowchart LR
  W["Working copy<br/>edit files"] -->|git add · git commit| B["Branch<br/>feature/…"]
  B -->|git push| R["GitHub<br/>the shared copy"]
  R --> PR["Pull request<br/>diff · review · checks"]
  PR -->|merge| M["main"]
  M -->|Harness deploys| P["Astro · Databricks"]
  M -.->|git pull| W
  class W yellow
  class B blue
  class R,PR focus
  class M green
  class P grey
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
# Landscape versions of two Day 2 platform pictures, for the Day 3 recap: each fits one screen.
D["d3-recap-lakehouse"] = """
flowchart LR
  subgraph W ["Data warehouse"]
    direction LR
    W1["Tables, SQL, ACID"] --- W2["Proprietary storage"] --- W3["Costly to scale,<br/>structured only"]
  end
  subgraph L ["Data lake"]
    direction LR
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
D["d3-recap-databricks"] = """
flowchart LR
  S["<b>Sources</b><br/>Vendor files<br/>Databases<br/>Streams, APIs"] --> I["<b>Ingestion</b><br/>Auto Loader, COPY INTO<br/>dbt seed, notebooks<br/>Kafka, Lakeflow"]
  I --> D["<b>Storage: S3</b><br/>Delta tables<br/>Parquet + _delta_log"]
  D <--> E["<b>Compute: Databricks</b><br/>Spark clusters<br/>SQL warehouses (Photon)"]
  E --> U["<b>Consumers</b><br/>dbt<br/>Notebooks, BI<br/>Marketplace, APIs"]
  G["<b>Governance: Unity Catalog</b><br/>catalog.schema.table<br/>permissions, lineage"] -.-> D
  G -.-> E
  class S grey
  class I aqua
  class D focus
  class E blue
  class G green
  class U yellow
"""
D["d3-recap-tools"] = """
flowchart LR
  A["<b>Catalyst, dev container</b><br/>write the code"] --> B["<b>GitHub, Harness</b><br/>review, deploy"]
  B --> C["<b>Airflow on Astro</b><br/>decides when"]
  C -->|Cosmos| D["<b>dbt</b><br/>rules and tests"]
  D -->|SQL| E["<b>Databricks (Spark)</b><br/>does the work"]
  E --> F["<b>Delta on S3</b><br/>Unity Catalog, Marketplace"]
  class A,B aqua
  class C,E blue
  class D focus
  class F green
"""
D["d3-journey"] = """
flowchart TB
  subgraph R1 ["First: make it run"]
    direction LR
    A["<b>1 Set up</b><br/>project + profile<br/>dbt debug"] --> B["<b>2 Load</b><br/>raw data<br/>dbt seed"] --> C["<b>3 Model</b><br/>source + SELECT<br/>dbt run"] --> D["<b>4 Connect</b><br/>ref() + a join<br/>dbt run"]
  end
  subgraph R2 ["Then: make it right, and say what it is"]
    direction LR
    E["<b>5 Promise</b><br/>tests in YAML<br/>dbt test"] --> F["<b>6 Fix</b><br/>edit the model<br/>dbt build"] --> G["<b>7 Your own test</b><br/>a SQL file in tests/<br/>dbt test"] --> H["<b>8 Explain</b><br/>docs + lineage<br/>dbt docs"]
  end
  R1 --> R2
  class A,B grey
  class C,D blue
  class E,F,G focus
  class H green
"""
D["d3-script-vs-dbt"] = """
flowchart TB
  subgraph S ["A SQL script, run by hand"]
    S1["<b>Is it right?</b><br/>Someone looks,<br/>sometimes"]
    S2["<b>What order?</b><br/>Someone<br/>remembers"]
    S3["<b>What does<br/>it mean?</b><br/>Ask the author"]
    S4["<b>Same rule in<br/>five places?</b><br/>Copy and paste"]
    S5["<b>Dev and prod?</b><br/>Edit the script"]
    S6["<b>What changed?</b><br/>Nobody knows"]
  end
  subgraph D ["The same work in dbt"]
    D1["Tests on<br/>every build"]
    D2["ref() sets<br/>the order"]
    D3["Docs and lineage,<br/>generated"]
    D4["Written once,<br/>as a macro"]
    D5["Same files,<br/>another target"]
    D6["Git and<br/>pull requests"]
  end
  S1 --> D1
  S2 --> D2
  S3 --> D3
  S4 --> D4
  S5 --> D5
  S6 --> D6
  class S1,S2,S3,S4,S5,S6 red
  class D1,D2,D3,D4,D5,D6 green
"""
D["d3-jinja"] = """
flowchart LR
  J1["{{ source('vendor_feed', 'prices_raw') }}"] --> O1["a raw table's full name"]
  J2["{{ ref('stg_prices') }}"] --> O2["another model's name,<br/>and an edge in the graph"]
  J3["{{ config(materialized = 'table') }}"] --> O3["a setting for this model"]
  J4["{{ this }}"] --> O4["this model's own table"]
  J5["if · for · macro<br/>(in curly-brace-percent tags)"] --> O5["logic that writes SQL:<br/>at 13:00"]
  class J1,J2,J3,J4 blue
  class J5 grey
  class O1,O2,O3,O4 green
  class O5 grey
"""
D["d3-yaml"] = """
flowchart LR
  E["<b>.yml = .yaml</b><br/>same format,<br/>two spellings"]
  E --> Fx
  E --> An
  subgraph Fx ["Two fixed names"]
    F1["dbt_project.yml"]
    F2["profiles.yml"]
  end
  subgraph An ["Any other name: dbt reads the keys inside"]
    K1["sources:<br/>raw tables"]
    K2["models:<br/>descriptions, tests"]
    K3["seeds: · snapshots:"]
    K4["unit_tests:"]
  end
  class E focus
  class F1,F2 yellow
  class K1,K2,K3,K4 blue
"""
D["d3-demo-to-challenge"] = """
flowchart LR
  subgraph A ["You just saw"]
    A1["debug · seed · the raw rows"]
    A2["dbt_project.yml · profiles.yml"]
    A3["sources.yml · source()"]
    A4["staging/stg_prices: rename, cast, clean"]
    A5["config() · dbt build · --select"]
    A6["schema.yml tests"]
    A7["int_ and fct_ models: ref(), a join"]
    A8["a singular test · docs"]
  end
  subgraph B ["In the challenge README"]
    B1["S1 Inspect the raw data"]
    B2["S2 Read the project"]
    B3["S3 Sources and freshness"]
    B4["S4, S5 Staging models"]
    B5["S6, S7 Materialise and build"]
    B6["S8, C5 Tests"]
    B7["C1 to C4 Joins and marts"]
    B8["C6 Reconciliation · C8 Docs"]
  end
  A1 --> B1
  A2 --> B2
  A3 --> B3
  A4 --> B4
  A5 --> B5
  A6 --> B6
  A7 --> B7
  A8 --> B8
  class A1,A2,A3,A4,A5,A6,A7,A8 blue
  class B1,B2,B3,B4,B5,B6,B7,B8 focus
"""
D["d3-optimize"] = """
flowchart LR
  subgraph B ["After many writes: lots of small files"]
    direction LR
    f1["file"] ~~~ f2["file"] ~~~ f3["file"] ~~~ f4["file"]
    f5["file"] ~~~ f6["file"] ~~~ f7["file"] ~~~ f8["file"]
  end
  subgraph A ["After OPTIMIZE: a few large files"]
    direction LR
    g1["large file"] ~~~ g2["large file"]
  end
  B ==>|"OPTIMIZE table"| A
  A -.- N["Same rows.<br/>Fewer files to open: faster reads.<br/>Old files kept until VACUUM."]
  class f1,f2,f3,f4,f5,f6,f7,f8 grey
  class g1,g2 focus
  class N green
"""
D["d3-zorder"] = """
flowchart TB
  Q["Query: where fund_id = 'F12'"]
  subgraph U ["Without ZORDER: every file holds every fund"]
    direction LR
    u1["file 1<br/>funds A to Z"] ~~~ u2["file 2<br/>funds A to Z"] ~~~ u3["file 3<br/>funds A to Z"] ~~~ u4["file 4<br/>funds A to Z"]
  end
  subgraph Z ["With ZORDER BY (fund_id): similar rows share a file"]
    direction LR
    z1["file 1<br/>funds A to F<br/>READ"] ~~~ z2["file 2<br/>funds G to M<br/>skipped"] ~~~ z3["file 3<br/>funds N to S<br/>skipped"] ~~~ z4["file 4<br/>funds T to Z<br/>skipped"]
  end
  Q -->|"reads all 4 files"| U
  Q -->|"reads 1 file, skips 3"| Z
  class Q blue
  class u1,u2,u3,u4,z1 focus
  class z2,z3,z4 grey
"""
D["d3-layers"] = """
flowchart LR
  R[("<b>Raw tables</b><br/>landed by other tools<br/>(seeds, in training)")] -->|"source()"| S["<b>staging/</b> · stg_<br/>one model per raw table<br/>rename, cast, clean<br/><i>view</i>"]
  S -->|"ref()"| I["<b>intermediate/</b> · int_<br/>joins and business rules<br/><i>view</i>"]
  I -->|"ref()"| M["<b>marts/</b> · fct_ agg_<br/>the tables consumers read<br/><i>table</i>"]
  M --> C["Consumers:<br/>reports, dashboards,<br/>other products"]
  class R,C grey
  class S aqua
  class I blue
  class M focus
"""

# The price-sheet build as a progress tracker: the same graph at each step of the Day 3 demo, with what is
# not built yet (dashed), what was built earlier (green), what this step built (yellow) and failing tests (red).
def _tracker(state, note=None):
    note = note or {}
    lab = lambda key, name: f'{name}<br/>{note[key]}' if key in note else name
    cls = {"todo": [], "done": [], "now": [], "fail": []}
    for key in ("R1", "R2", "S1", "S2", "I", "M"):
        cls[state.get(key, "todo")].append(key)
    lines = ["flowchart LR",
             '  subgraph raw ["Raw (seeds)"]',
             f'    R1[("{lab("R1", "vendor_prices_raw")}")]', f'    R2[("{lab("R2", "fx_rates_raw")}")]', "  end",
             '  subgraph stg ["staging/ (views)"]',
             f'    S1["{lab("S1", "stg_prices")}"]', f'    S2["{lab("S2", "stg_fx_rates")}"]', "  end",
             '  subgraph int ["intermediate/ (view)"]',
             f'    I["{lab("I", "int_prices_usd")}"]', "  end",
             '  subgraph mart ["marts/ (table)"]',
             f'    M["{lab("M", "fct_prices_usd")}"]', "  end",
             '  R1 -->|"source()"| S1', '  R2 -->|"source()"| S2', '  S1 -->|"ref()"| I', '  S2 -->|"ref()"| I', '  I -->|"ref()"| M']
    lines += [f"  class {','.join(v)} {k}" for k, v in cls.items() if v]
    lines += ["classDef todo fill:#FFFFFF,stroke:#999999,stroke-dasharray:5 4,color:#888888",
              "classDef done fill:#C9DAF8,stroke:#434343,color:#1a1a1a",
              "classDef now fill:#F8DB59,stroke:#434343,stroke-width:3px,color:#1a1a1a",
              "classDef fail fill:#F4CCCC,stroke:#990000,stroke-width:3px,color:#1a1a1a"]
    return "\n".join(lines) + "\n"

_ALL = ("R1", "R2", "S1", "S2", "I", "M")
D["d3-build-plan"] = _tracker({})
D["d3-build-2"] = _tracker({"R1": "now", "R2": "now"})
D["d3-build-3"] = _tracker({"R1": "done", "R2": "done", "S1": "now"})
D["d3-build-4"] = _tracker({"R1": "done", "R2": "done", "S1": "done", "S2": "now", "I": "now", "M": "now"})
D["d3-build-5"] = _tracker({**{k: "done" for k in _ALL}, "M": "fail"}, {"S1": "currency: gbp", "M": "test fails: 3 empty prices"})
D["d3-build-6"] = _tracker({**{k: "done" for k in _ALL}, "S1": "now"}, {"S1": "fixed: GBP", "M": "2 tests pass"})
D["d3-build-7"] = _tracker({**{k: "done" for k in _ALL}, "M": "now"}, {"M": "3 tests pass"})
D["d3-seed-vs-source"] = """
flowchart LR
  subgraph T ["In training"]
    C["CSV files<br/>in seeds/"] -->|"dbt seed"| RT[("raw table")]
  end
  subgraph P ["On a real product"]
    Sy["Source systems"] -->|"an ingestion tool<br/>(not dbt)"| RP[("raw table")]
  end
  RT --> Y["<b>sources.yml</b><br/>declares the raw table"]
  RP --> Y
  Y -->|"source()"| M["Your staging model"]
  class C,Sy grey
  class RT,RP aqua
  class Y focus
  class M blue
"""
D["d3-what-dbt-does"] = """
flowchart LR
  Src["Source systems"] -->|"extract + load<br/>(other tools)"| Raw["Raw tables"]
  subgraph WH["The warehouse: Databricks, or DuckDB on a laptop"]
    Raw --> Mod["Views and tables<br/>built by dbt"]
  end
  Files["SQL + YAML files<br/>in Git"] --> Dbt["dbt<br/>compile · order · run · test · document"]
  Dbt -->|"sends SQL"| Mod
  Mod --> Use["Consumers"]
  class Src,Use grey
  class Raw aqua
  class Mod green
  class Files blue
  class Dbt focus
"""
D["d3-project-anatomy"] = """
flowchart TB
  P["price_sheet/<br/>a dbt project is a folder"] --> Y1["dbt_project.yml<br/>name, defaults per folder"]
  P --> Y2["profiles.yml<br/>connection, targets"]
  P --> M["models/<br/>one SELECT per .sql file<br/>+ YAML: sources, descriptions, tests"]
  P --> Sd["seeds/<br/>small CSVs"]
  P --> T["tests/<br/>singular tests"]
  P --> Mc["macros/<br/>reusable Jinja"]
  P --> Tg["target/<br/>written by dbt"]
  M --> L1["staging/<br/>stg_ : clean one raw table"]
  M --> L2["intermediate/<br/>int_ : joins and rules"]
  M --> L3["marts/<br/>fct_ agg_ : what consumers read"]
  class P focus
  class Y1,Y2 yellow
  class M,L1,L2,L3 blue
  class Sd,T,Mc aqua
  class Tg grey
"""
D["d3-compile"] = """
flowchart LR
  A["models/staging/stg_prices.sql<br/>SELECT with {{ source(...) }}"] -->|compile| B["target/compiled/<br/>plain SELECT,<br/>real table names"]
  B -->|wrap| C["target/run/<br/>create view ... as<br/>SELECT"]
  C -->|send| D["Warehouse<br/>view stg_prices"]
  class A blue
  class B,C grey
  class D green
"""
D["d3-first-dag"] = """
flowchart LR
  subgraph raw ["Raw (seeds)"]
    R1[("vendor_prices_raw")]
    R2[("fx_rates_raw")]
  end
  subgraph stg ["staging/ : views"]
    S1["stg_prices"]
    S2["stg_fx_rates"]
  end
  subgraph int ["intermediate/ : views"]
    I["int_prices_usd"]
  end
  subgraph mart ["marts/ : tables"]
    M["fct_prices_usd"]
  end
  R1 -->|"source()"| S1
  R2 -->|"source()"| S2
  S1 -->|"ref()"| I
  S2 -->|"ref()"| I
  I -->|"ref()"| M
  class R1,R2 grey
  class S1,S2 aqua
  class I blue
  class M focus
"""
D["d3-tests"] = """
flowchart LR
  G["Generic test<br/>YAML, on a column<br/>not_null · unique ·<br/>accepted_values · relationships"] --> Q["A query for the rows<br/>that break the rule"]
  Sg["Singular test<br/>a .sql file in tests/"] --> Q
  Q -->|"no rows"| Pass["PASS"]
  Q -->|"rows"| Fail["FAIL<br/>downstream skipped"]
  class G,Sg blue
  class Q focus
  class Pass green
  class Fail red
"""
D["d3-lifecycle"] = """
flowchart LR
  A["Declare<br/>the source"] --> B["Write<br/>the SELECT"] --> C["Run"] --> D["Test"] --> E["Document"] --> F["Commit,<br/>pull request"]
  D -.->|"fails: fix the model"| B
  F -.->|"next change"| B
  class A,B blue
  class C,E aqua
  class D focus
  class F green
"""
D["d3-macro"] = """
flowchart LR
  Mc["macros/to_usd.sql<br/>the rule, written once"] --> M1["int_prices_usd"]
  Mc --> M2["another model"]
  Mc --> M3["another model"]
  M1 --> Cp["Compiled SQL<br/>the expression, expanded"]
  M2 --> Cp
  M3 --> Cp
  class Mc focus
  class M1,M2,M3 blue
  class Cp grey
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
  Cfg["Set per folder in dbt_project.yml,<br/>or in one model with config()"] --> V["<b>view</b><br/>a saved query:<br/>runs when someone reads it"]
  Cfg --> Tb["<b>table</b><br/>saved when dbt runs:<br/>fast to read"]
  Cfg --> Inc["<b>incremental</b><br/>a table that only<br/>adds the new rows"]
  Cfg --> Sn["<b>snapshot</b><br/>keeps the old versions<br/>of rows that change"]
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
