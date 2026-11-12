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
D["d3-snapshot"] = """
flowchart LR
  subgraph R1 ["Raw table, first delivery"]
    r1["GBP · 5 Nov · <b>1.268</b>"]
  end
  subgraph R2 ["Raw table, after the vendor restates"]
    r2["GBP · 5 Nov · <b>1.300</b>"]
  end
  subgraph S ["Snapshot table: every version kept"]
    direction TB
    s1["GBP · 5 Nov · <b>1.268</b><br/>valid from: snapshot 1<br/>valid to: snapshot 2 · <i>closed</i>"]
    s2["GBP · 5 Nov · <b>1.300</b><br/>valid from: snapshot 2<br/>valid to: empty · <i>current</i>"]
  end
  R1 ==>|"vendor restates"| R2
  r1 -.->|"dbt snapshot 1"| s1
  r2 -.->|"dbt snapshot 2"| s2
  R2 -.- N["1.268 is gone<br/>from the raw table"]
  class r1,s1 grey
  class r2 blue
  class s2 focus
  class N red
"""
D["d3-snapshot-run"] = """
flowchart LR
  Run["<b>dbt snapshot</b><br/>each run"] --> C{"Each source row:<br/>is there a current version<br/>with the same key?"}
  C -->|"no: a new key"| A["Insert it<br/><i>current</i>"]
  C -->|"yes, rate unchanged"| B["Do nothing"]
  C -->|"yes, rate changed"| D["Close the old version<br/>(set dbt_valid_to)<br/>insert the new one, <i>current</i>"]
  K["<b>unique_key</b> [from_ccy, rate_dt]<br/>which rows are the same thing<br/><b>check_cols</b> [rate]<br/>which change makes a new version"] -.- C
  class Run blue
  class C yellow
  class A,D focus
  class B grey
  class K green
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
D["d4-bt-path"] = """
flowchart TB
  subgraph R1 ["First: build the history table"]
    direction LR
    A["<b>1 Start</b><br/>yesterday's price sheet<br/>dbt build"] --> B["<b>2 Deliveries</b><br/>three FX files<br/>dbt seed"] --> C["<b>3 Model</b><br/>two clocks on<br/>every row"] --> D["<b>4 Macro</b><br/>how a delivery<br/>lands"]
  end
  subgraph R2 ["Then: load it, and ask it questions"]
    direction LR
    E["<b>5 Load 1</b><br/>the first day"] --> F["<b>6 Load 2</b><br/>a new day,<br/>one wrong rate"] --> G["<b>7 Load 3</b><br/>the vendor's<br/>correction"] --> H["<b>8 Questions</b><br/>as is, as of,<br/>as was"]
  end
  R1 --> R2
  class A,B grey
  class C,D blue
  class E,F,G focus
  class H green
"""
D["d4-two-clocks"] = """
flowchart LR
  subgraph B ["Business clock: when was it true?"]
    direction TB
    B1["The GBP rate <b>for 4 November</b>"]
    B2["dl_business_start_dt<br/>dl_business_end_dt"]
  end
  subgraph S ["System clock: when did we believe it?"]
    direction TB
    S1["We loaded it <b>on Wednesday at 06:00</b>,<br/>and corrected it <b>on Thursday</b>"]
    S2["dl_system_start_ts<br/>dl_system_end_ts"]
  end
  R["One row =<br/>one rate<br/>+ both clocks"] --> B
  R --> S
  B -.- QB["Answers: what was the rate<br/>on that day?"]
  S -.- QS["Answers: what did Wednesday's<br/>report say?"]
  class R focus
  class B1,B2 blue
  class S1,S2 aqua
  class QB,QS green
"""
D["d4-bt-macro"] = """
flowchart LR
  In["Each row in<br/>the new delivery"] --> C{"Is there a current row<br/>for this currency?"}
  C -->|"no"| A["<b>Insert</b><br/>current"]
  C -->|"yes, same rate"| B["<b>Nothing</b><br/>safe to re-run"]
  C -->|"yes, different rate"| Dd{"Is the business date<br/>later, or the same?"}
  Dd -->|"later: a new day"| N["1 close the old row's <b>system</b> clock<br/>2 copy it with its <b>business</b> clock ended<br/>3 insert the new rate, current"]
  Dd -->|"the same: a correction"| X["1 close the old row's <b>system</b> clock<br/>3 insert the corrected rate, current"]
  class In blue
  class C,Dd yellow
  class A,N,X focus
  class B grey
"""
D["d4-bt-load-1"] = """
flowchart LR
  F["Delivery D1<br/>GBP for 3 Nov = 1.267013"] ==>|"load 1"| A
  subgraph T ["fx_rates_history: GBP"]
    A["<b>A</b> · 1.267013<br/>business: 3 Nov → open<br/>system: load 1 → open<br/><i>current</i>"]
  end
  class F grey
  class A focus
"""
D["d4-bt-load-2"] = """
flowchart LR
  subgraph D3 ["GBP, the rate for 3 Nov"]
    direction LR
    A["<b>A</b> · 1.267013<br/>business: 3 Nov → open<br/>system: load 1 → <b>load 2</b><br/><i>closed: no longer believed<br/>as it stood</i>"] -->|"carried<br/>forward"| B["<b>B</b> · 1.267013<br/>business: 3 Nov → <b>3 Nov</b><br/>system: load 2 → open<br/><i>still true for its own day</i>"]
  end
  subgraph D4 ["GBP, the rate for 4 Nov"]
    direction LR
    F["Delivery D2<br/>4 Nov = 1.628112<br/>a new day;<br/>the rate is wrong"] ==>|"load 2"| C["<b>C</b> · 1.628112<br/>business: 4 Nov → open<br/>system: load 2 → open<br/><i>current</i>"]
  end
  D3 ~~~ D4
  class F grey
  class A grey
  class B blue
  class C focus
"""
D["d4-bt-load-3"] = """
flowchart LR
  subgraph D3 ["GBP, the rate for 3 Nov: untouched by the correction"]
    direction LR
    A["<b>A</b> · 1.267013<br/>business: 3 Nov → open<br/>system: load 1 → load 2"] --> B["<b>B</b> · 1.267013<br/>business: 3 Nov → 3 Nov<br/>system: load 2 → open"]
  end
  subgraph D4 ["GBP, the rate for 4 Nov"]
    direction LR
    C["<b>C</b> · 1.628112<br/>business: 4 Nov → open<br/>system: load 2 → <b>load 3</b><br/><i>closed: the wrong rate, kept</i>"] -->|"replaced,<br/>not erased"| Dn["<b>D</b> · 1.268112<br/>business: 4 Nov → open<br/>system: load 3 → open<br/><i>current</i>"]
    F["Delivery D2-CORR<br/>4 Nov = 1.268112<br/>the same day, corrected"] ==>|"load 3"| Dn
  end
  D3 ~~~ D4
  class F grey
  class A,B grey
  class C red
  class Dn focus
"""
D["d4-bt-questions"] = """
flowchart LR
  Q1["<b>As is</b><br/>What is the rate now?"] -->|"both clocks open"| Dn["<b>D</b> · 1.268112<br/>4 Nov, corrected"]
  Q2["<b>As of 3 Nov</b><br/>What was the rate that day,<br/>as we know it today?"] -->|"business clock covers 3 Nov,<br/>system clock open"| B["<b>B</b> · 1.267013<br/>3 Nov"]
  Q3["<b>As was</b><br/>What did Wednesday's<br/>report use?"] -->|"system clock covers<br/>Wednesday"| C["<b>C</b> · 1.628112<br/>4 Nov, wrong"]
  class Q1,Q2,Q3 yellow
  class Dn focus
  class B blue
  class C red
"""
D["d4-why-orchestration"] = """
flowchart TB
  subgraph S ["dbt build, typed by hand"]
    S1["<b>When?</b><br/>When someone<br/>remembers"]
    S2["<b>Stale input?</b><br/>It builds<br/>anyway"]
    S3["<b>A blip?</b><br/>It fails;<br/>type it again"]
    S4["<b>It broke?</b><br/>Nobody is<br/>told"]
    S5["<b>Yesterday?</b><br/>No record"]
  end
  subgraph D ["The same build, run by Airflow"]
    D1["A schedule,<br/>in a time zone"]
    D2["A freshness gate<br/>stops the run"]
    D3["Retries,<br/>with backoff"]
    D4["Callbacks alert<br/>the right people"]
    D5["Every run, state<br/>and log is kept"]
  end
  S1 --> D1
  S2 --> D2
  S3 --> D3
  S4 --> D4
  S5 --> D5
  class S1,S2,S3,S4,S5 red
  class D1,D2,D3,D4,D5 green
"""
D["d4-airflow-path"] = """
flowchart TB
  subgraph R1 ["Read the DAG"]
    direction LR
    A["<b>1 Why</b><br/>orchestration"] --> B["<b>2 Anatomy</b><br/>of a DAG"] --> C["<b>3 Connect</b><br/>dbt debug"] --> D["<b>4 The gate</b><br/>freshness"] --> E["<b>5 Cosmos</b><br/>the task group"]
  end
  subgraph R2 ["Wire it, run it, break it"]
    direction LR
    F["<b>6 Wire</b><br/>the chain: >>"] --> G["<b>7 Schedule</b><br/>cron + time zone"] --> H["<b>8 Retries</b><br/>and backoff"] --> I["<b>9 First run</b><br/>trigger, check"] --> J["<b>10 Logs</b><br/>fail, fix, clear"]
  end
  R1 --> R2
  class A,B grey
  class C,D,E blue
  class F focus
  class G,H aqua
  class I,J green
"""
D["d4-ps-dag"] = """
flowchart LR
  S["start"] --> F["source_freshness_check<br/><i>is the vendor feed fresh?</i>"] --> G
  subgraph G ["dbt_pipeline: Cosmos, one task per model"]
    direction LR
    St["stg_prices<br/>stg_fx_rates"] --> In["int_prices_usd"] --> Ma["fct_prices_usd<br/>agg_prices_by_ccy"] --> Te["dbt_test"]
  end
  G --> P["publish_to_catalog<br/><i>SLA: 90 minutes</i>"] --> E["end"]
  class S,E grey
  class F yellow
  class St,In,Ma,Te blue
  class P focus
"""
D["d4-dag-anatomy"] = """
flowchart LR
  File["<b>A file in dags/</b><br/>price_sheet_daily.py"] --> Dag["<b>with DAG(...) as dag:</b><br/>dag_id · schedule · start_date<br/>default_args · tags"]
  Dag --> T["<b>Tasks</b> created inside it<br/>EmptyOperator · PythonOperator<br/>DbtTaskGroup"]
  T --> W["<b>a >> b</b><br/>b runs after a"]
  Da["<b>default_args</b><br/>inherited by every task:<br/>owner, retries, callbacks"] -.-> Dag
  Pr["The DAG processor reads the folder<br/>and registers every DAG it finds"] -.-> File
  class File grey
  class Dag focus
  class T blue
  class W green
  class Da,Pr yellow
"""
D["d4-freshness-gate"] = """
flowchart LR
  Feed["Latest vendor_ts<br/>in the raw feed"] --> Age{"How old<br/>is it?"}
  Age -->|"under 4 hours"| Ok["<b>pass</b><br/>the run carries on"]
  Age -->|"4 to 6 hours<br/>warn_after"| Warn["<b>warn</b><br/>a warning in the log;<br/>the run carries on"]
  Age -->|"over 6 hours<br/>error_after"| Err["<b>error</b><br/>the task fails;<br/>nothing is built"]
  Ok --> Build["dbt_pipeline"]
  Warn --> Build
  Err -.->|"upstream_failed"| Skip["no build,<br/>no publish"]
  class Feed grey
  class Age yellow
  class Ok green
  class Warn focus
  class Err,Skip red
  class Build blue
"""
D["d4-cosmos"] = """
flowchart TB
  subgraph P ["The dbt project: source() and ref() give the order"]
    direction LR
    M1["stg_prices"] --> M3["int_prices_usd"]
    M2["stg_fx_rates"] --> M3
    M3 --> M4["fct_prices_usd"] --> M5["agg_prices_by_ccy"]
  end
  P ==>|"Cosmos reads the project"| A
  subgraph A ["Airflow tasks: nobody wrote them by hand"]
    direction LR
    T1["stg_prices_run"] --> T3["int_prices_usd_run"]
    T2["stg_fx_rates_run"] --> T3
    T3 --> T4["fct_prices_usd_run"] --> T5["agg_prices_by_ccy_run"] --> T6["dbt_test"]
  end
  class M1,M2,M3,M4,M5 blue
  class T1,T2,T3,T4,T5 focus
  class T6 green
"""
D["d4-cron"] = """
flowchart TB
  C["<b>0 6 * * 1-5</b>"]
  C --> A["<b>0</b><br/>minute"]
  C --> B["<b>6</b><br/>hour"]
  C --> D["<b>*</b><br/>day of month:<br/>any"]
  C --> E["<b>*</b><br/>month:<br/>any"]
  C --> F["<b>1-5</b><br/>day of week:<br/>Monday to Friday"]
  Tz["<b>start_date</b> in Europe/London<br/>06:00 stays 06:00 UK,<br/>summer and winter"] -.-> C
  K["<b>catchup=False</b>: no backfill of missed days<br/><b>max_active_runs=1</b>: never two runs at once"] -.-> C
  class C focus
  class A,B,D,E,F blue
  class Tz,K yellow
"""
D["d4-cron-syntax"] = """
flowchart TB
  subgraph F ["Five fields, read left to right"]
    direction LR
    A["<b>0</b><br/>minute<br/>0 to 59"] ~~~ B["<b>6</b><br/>hour<br/>0 to 23"] ~~~ Cc["<b>*</b><br/>day of month<br/>1 to 31"] ~~~ Dd["<b>*</b><br/>month<br/>1 to 12"] ~~~ E["<b>1-5</b><br/>day of week<br/>0 to 6, Sunday is 0"]
  end
  subgraph S ["Four symbols"]
    direction LR
    S1["<b>*</b><br/>every value"] ~~~ S2["<b>,</b><br/>a list<br/>9,17"] ~~~ S3["<b>-</b><br/>a range<br/>1-5"] ~~~ S4["<b>/</b><br/>a step<br/>*/15"]
  end
  subgraph X ["Read these"]
    direction LR
    X1["<b>0 6 * * 1-5</b><br/>06:00,<br/>Monday to Friday"] ~~~ X2["<b>*/15 * * * *</b><br/>every 15 minutes"] ~~~ X3["<b>0 9,17 * * *</b><br/>09:00 and 17:00,<br/>every day"] ~~~ X4["<b>30 2 1 * *</b><br/>02:30 on the 1st<br/>of every month"]
  end
  F --> S --> X
  class A,B,Cc,Dd,E blue
  class S1,S2,S3,S4 yellow
  class X1 focus
  class X2,X3,X4 green
"""
D["d4-retries"] = """
flowchart TB
  subgraph T ["One task, three attempts (retries: 2)"]
    direction LR
    A1["Attempt 1<br/><b>fails</b>"] -->|"wait:<br/>retry_delay"| A2["Attempt 2<br/><b>fails</b>"] -->|"wait: twice<br/>as long"| A3["Attempt 3<br/><b>fails</b>"] --> Fd["Task is <b>failed</b><br/>the tasks after it:<br/>upstream_failed"]
  end
  subgraph N ["What each one triggers"]
    direction LR
    R1["Attempts 1 and 2:<br/>the task is <b>up_for_retry</b><br/>on_retry_callback: a ticket (P3)"] ~~~ Cb["Attempt 3:<br/>on_failure_callback:<br/>Datadog event (P1) + Teams (P2)"] ~~~ Ok["If any attempt succeeds:<br/>the run carries on,<br/>and nobody is paged"]
  end
  T --> N
  class A1,A2 focus
  class A3,Fd red
  class R1 yellow
  class Cb red
  class Ok green
"""
D["d4-clear"] = """
flowchart TB
  subgraph F ["The failed run"]
    direction LR
    G1["source_freshness_check<br/><b>failed</b>"] --> G2["dbt_pipeline<br/>upstream_failed"] --> G3["publish_to_catalog<br/>upstream_failed"]
  end
  F -->|"1 read the log · 2 fix the cause · 3 Clear the failed task, with Include Downstream"| R
  subgraph R ["The same run, re-queued from the task you cleared"]
    direction LR
    H1["source_freshness_check<br/><b>success</b>"] --> H2["dbt_pipeline<br/>success"] --> H3["publish_to_catalog<br/>success"]
  end
  class G1 red
  class G2,G3 grey
  class H1,H2,H3 green
"""
D["d4-alert-tiers"] = """
flowchart LR
  subgraph Ev ["What happened"]
    direction TB
    E1["A task <b>failed</b><br/>after all its retries"]
    E2["The run is <b>slow</b>:<br/>the SLA was missed"]
    E3["A task is about<br/>to <b>retry</b>"]
    E4["The run <b>succeeded</b>"]
  end
  subgraph Cb ["The callback, and where it is attached"]
    direction TB
    C1["on_failure_callback<br/><i>default_args: every task</i>"]
    C2["sla_miss_callback<br/><i>on the DAG</i>"]
    C3["on_retry_callback<br/><i>default_args: every task</i>"]
    C4["on_success_callback<br/><i>on the last task only</i>"]
  end
  subgraph Ch ["Who hears about it"]
    direction TB
    P1["<b>P1</b> Datadog event;<br/>support pages the on-call<br/>(xMatters) + Teams"]
    P2["<b>P2</b> Microsoft Teams:<br/>notify, do not page"]
    P3["<b>P3</b> a ticket:<br/>nobody is disturbed"]
    P4["One Teams message<br/>per green run"]
  end
  E1 --> C1 --> P1
  E2 --> C2 --> P2
  E3 --> C3 --> P3
  E4 --> C4 --> P4
  class E1,P1 red
  class E2,P2 focus
  class E3,P3 yellow
  class E4,P4 green
  class C1,C2,C3,C4 blue
"""
D["d4-monitoring"] = """
flowchart TB
  A1["<b>Alerting: something just broke</b><br/>a task failed, an SLA was missed<br/>callbacks fire when it happens"]
  A1 --> M
  subgraph M ["Monitoring: something is drifting. Six panels"]
    direction TB
    M1["1 Run status"] ~~~ M4["4 SLA compliance"]
    M2["2 Run duration"] ~~~ M5["5 Source freshness<br/><i>watches the clock</i>"]
    M3["3 Task failure rate"] ~~~ M6["6 Source volume<br/><i>watches the row count:<br/>on time, but short</i>"]
  end
  class A1 red
  class M1,M2,M3,M4 blue
  class M5 yellow
  class M6 focus
"""
D["d4-two-shapes"] = """
flowchart TB
  subgraph Co ["Cosmos: dbt runs on the Airflow worker"]
    direction LR
    W1["Airflow worker<br/>runs dbt"] -->|"SQL"| DB1[("Databricks<br/>SQL warehouse")] --- N1["One Airflow task per model:<br/>you see which model failed"]
  end
  subgraph Sr ["Submit-run: dbt runs inside Databricks (CG's paved path)"]
    direction LR
    W2["Airflow task submits<br/>a job, then waits"] -->|"DatabricksSubmitRunOperator"| DB2[("Databricks job<br/>runs dbt")] --- N2["One task per step: the job is one box.<br/>Logs live in Databricks;<br/>the worker stays free"]
  end
  Co ~~~ Sr
  class W1,W2 blue
  class DB1,DB2 focus
  class N1,N2 yellow
"""
D["d4-demo-to-challenge"] = """
flowchart LR
  subgraph A ["You just saw, on the price sheet"]
    A1["why · the DAG file · dbt debug"]
    A2["the freshness gate, run alone"]
    A3["the Cosmos task group"]
    A4["the chain: one line of >>"]
    A5["the schedule · retries"]
    A6["a green run · the rows it published"]
    A7["a failure: log, fix, clear"]
    A8["alerts · monitoring · runbook · tests"]
  end
  subgraph B ["In the challenge README"]
    B1["1 to 3 Why, anatomy, connect"]
    B2["4 The freshness gate"]
    B3["5 The Cosmos DbtTaskGroup"]
    B4["6 Wire the chain: your one TODO"]
    B5["7, 8 Scheduling, retries"]
    B6["9 First full run"]
    B7["10 Logs and re-running"]
    B8["Phase 2: challenges 1 to 10"]
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
D["d4-loading-strategies"] = """
flowchart LR
  A["<b>Truncate and reload</b><br/>empty the table,<br/>load everything again"] ~~~ B["<b>Insert overwrite</b><br/>replace one slice,<br/>for example one day"] ~~~ C["<b>SCD type 2</b><br/>a changed row gets<br/>a start and an end date"] ~~~ Dd["<b>Bitemporal</b><br/>SCD type 2,<br/>with a second clock"]
  A -.- RA["Remembers:<br/>only the latest load"]
  B -.- RB["Remembers:<br/>the latest version<br/>of each slice"]
  C -.- RC["Remembers:<br/>when each value<br/>was true"]
  Dd -.- RD["Remembers:<br/>when it was true,<br/>and when we believed it"]
  class A,B grey
  class C blue
  class Dd focus
  class RA,RB red
  class RC yellow
  class RD green
"""
D["d4-delivery-types"] = """
flowchart LR
  subgraph F ["Full"]
    F1["The source sends<br/><b>every record</b>, every run"] --> F2["Compare all of it<br/>with the table:<br/>costly on a large table"]
  end
  subgraph I ["Incremental"]
    I1["The source sends only<br/><b>new or changed</b> records,<br/>each with a business key"] --> I2["A known key with new content<br/>ends the previous version"]
  end
  subgraph Bl ["Balance"]
    B1["The source sends<br/><b>balances</b>:<br/>amounts as at a date"] --> B2["Its own strategy:<br/>ask the platform team<br/>which one your model needs"]
  end
  F ~~~ I ~~~ Bl
  class F1,I1,B1 blue
  class F2,I2,B2 yellow
"""
D["d4-correction"] = """
flowchart TB
  subgraph O ["Overwrite: one row, always the latest"]
    direction LR
    O1["Wednesday<br/>GBP = <b>1.628112</b><br/>the report uses it"] -->|"Thursday:<br/>the correction"| O2["GBP = <b>1.268112</b><br/>the old value is gone"] --> O3["What did Wednesday's<br/>report use?<br/><b>Nobody can say</b>"]
  end
  subgraph K ["Keep both: a correction adds a row"]
    direction LR
    K1["Wednesday<br/>GBP = <b>1.628112</b><br/>the report uses it"] -->|"Thursday:<br/>the correction"| K2["1.628112: believed Wed to Thu<br/>1.268112: believed from Thu"] --> K3["As was: 1.628112<br/>As is: 1.268112<br/><b>Both answers</b>"]
  end
  O ~~~ K
  class O1,K1 grey
  class O2,O3 red
  class K2 focus
  class K3 green
"""
D["d4-utc"] = """
flowchart LR
  R["The run starts<br/><b>Thursday 03:00 Pacific</b><br/>and loads Wednesday's rates"] --> B["<b>Business clock</b><br/>dl_business_start_dt<br/>= Wednesday 4 Nov<br/><i>from the data</i>"]
  R --> S["<b>System clock</b><br/>dl_system_start_ts<br/>= Thursday 5 Nov, 11:00 UTC<br/><i>from the load, always UTC</i>"]
  B -.- N["Two dates on one row, and neither is wrong.<br/>Always say which clock a date column is."]
  S -.- N
  class R grey
  class B blue
  class S aqua
  class N yellow
"""
D["d4-cicd-tradeoffs"] = """
flowchart LR
  subgraph G ["What it gives"]
    direction TB
    G1["Faster feedback:<br/>you hear the same day<br/>that something broke"]
    G2["A shared view:<br/>the team sees what changed<br/>and what is live"]
    G3["A record:<br/>who released what,<br/>and when"]
  end
  subgraph C ["What it costs"]
    direction TB
    C1["Automation with no person<br/>looking: a deleted test is<br/>easy to approve"]
    C2["Shared systems fail together:<br/>when the pipeline is down,<br/>nobody releases"]
    C3["Upkeep: approvals,<br/>audit and maintenance<br/>are real work"]
  end
  G1 ~~~ C1
  G2 ~~~ C2
  G3 ~~~ C3
  class G1,G2,G3 green
  class C1,C2,C3 red
"""
D["d4-harness"] = """
flowchart LR
  subgraph Y ["What a creator does"]
    direction TB
    Y1["Open a pull request"] --> Y2["Get it reviewed<br/>and approved"] --> Y3["Merge"]
  end
  subgraph H ["What Harness does, from the merge"]
    direction TB
    H1["Build and test"] --> H2["Deploy to SQA<br/><i>shared: check who<br/>deployed last</i>"] --> H3["Deploy to production<br/><i>needs a change record</i>"]
  end
  Y3 ==>|"the merge<br/>starts the pipeline"| H1
  H -.- R["What a creator reads:<br/>which pipeline ran,<br/>its logs,<br/>who deployed last night"]
  class Y1,Y2,Y3 blue
  class H1,H2,H3 focus
  class R yellow
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
