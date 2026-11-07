## Version2 airflow — phase-one-certified {#summary-airflow-phase-one-certified}

Core phase. Minimum standard; **75–110minutes**, estimated/unpiloted. Prerequisites: Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace. Execution boundary: Airflow local Dag.test execution; Astro UI and connected adapter gates separate.

| Task | Learner outcome / demonstration concept | Concept ID | Minutes |
|---|---|---|---|
| [airflow-p1-01](13-appendix-h-challenges-v2.md#airflow-p1-01) | Inspect a prepared orchestration baseline | airflow-p1-01-concept | 15–22 |
| [airflow-p1-02](13-appendix-h-challenges-v2.md#airflow-p1-02) | Author a small Python DAG with real dbt tasks | airflow-p1-02-concept | 15–22 |
| [airflow-p1-03](13-appendix-h-challenges-v2.md#airflow-p1-03) | Demonstrate the dependency graph and manual run | airflow-p1-03-concept | 15–22 |
| [airflow-p1-04](13-appendix-h-challenges-v2.md#airflow-p1-04) | Inspect a controlled task failure | airflow-p1-04-concept | 15–22 |
| [airflow-p1-05](13-appendix-h-challenges-v2.md#airflow-p1-05) | Explain the run and environment boundaries | airflow-p1-05-concept | 15–22 |

Completion requires the phase artifacts,independent checks and learner explanation. Optional stretch is outside the fixed core. The full concept explanations,hints,checks and starter notices follow in [AppendixH](13-appendix-h-challenges-v2.md#appendix-h).


## Version2 airflow — phase-two-proficient {#summary-airflow-phase-two-proficient}

Core phase. Advanced clinic/post-course route; **90–120minutes**, estimated/unpiloted. Prerequisites: Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace. Execution boundary: Airflow local Dag.test execution; Astro UI and connected adapter gates separate.

| Task | Learner outcome / demonstration concept | Concept ID | Minutes |
|---|---|---|---|
| [airflow-p2-01](13-appendix-h-challenges-v2.md#airflow-p2-01) | Define bounded replay and input identity | airflow-p2-01-concept | 18–24 |
| [airflow-p2-02](13-appendix-h-challenges-v2.md#airflow-p2-02) | Inject failure and observe useful retry behavior | airflow-p2-02-concept | 18–24 |
| [airflow-p2-03](13-appendix-h-challenges-v2.md#airflow-p2-03) | Prove output correctness after recovery | airflow-p2-03-concept | 18–24 |
| [airflow-p2-04](13-appendix-h-challenges-v2.md#airflow-p2-04) | Use Astro UI to make an operational decision | airflow-p2-04-concept | 18–24 |
| [airflow-p2-05](13-appendix-h-challenges-v2.md#airflow-p2-05) | Write a short incident handoff | airflow-p2-05-concept | 18–24 |

Completion requires the phase artifacts,independent checks and learner explanation. Optional stretch is outside the fixed core. The full concept explanations,hints,checks and starter notices follow in [AppendixH](13-appendix-h-challenges-v2.md#appendix-h).


## Version2 kafka — phase-one-certified {#summary-kafka-phase-one-certified}

Optional clinic. Minimum standard; **60–90minutes**, estimated/unpiloted. Prerequisites: Optional route. Prepared apache/kafka4.1.0 broker,confluent-kafka2.11.1 bridge and isolated Airflow3.1.0 runtime. Instructor supplies topic/group/runtime boundaries. Execution boundary: Kafka broker→consumer→Airflow→dbt; offline payload checks are supporting evidence.

| Task | Learner outcome / demonstration concept | Concept ID | Minutes |
|---|---|---|---|
| [kafka-p1-01](13-appendix-h-challenges-v2.md#kafka-p1-01) | Read the dataset-arrived contract | kafka-p1-01-concept | 12–18 |
| [kafka-p1-02](13-appendix-h-challenges-v2.md#kafka-p1-02) | Start the prepared local broker and inspect a topic | kafka-p1-02-concept | 12–18 |
| [kafka-p1-03](13-appendix-h-challenges-v2.md#kafka-p1-03) | Produce and follow a uniquely identified event | kafka-p1-03-concept | 12–18 |
| [kafka-p1-04](13-appendix-h-challenges-v2.md#kafka-p1-04) | Verify the dbt output belongs to the event | kafka-p1-04-concept | 12–18 |
| [kafka-p1-05](13-appendix-h-challenges-v2.md#kafka-p1-05) | Replay and explain duplicate policy | kafka-p1-05-concept | 12–18 |

Completion requires the phase artifacts,independent checks and learner explanation. Optional stretch is outside the fixed core. The full concept explanations,hints,checks and starter notices follow in [AppendixH](13-appendix-h-challenges-v2.md#appendix-h).
