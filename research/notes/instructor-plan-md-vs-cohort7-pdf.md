## Paragraphs in the current instructor-plan.md with no close match in the Cohort 7 PDF

- 09:00–09:20 mappings and service commitments explain mapping rules and the distinction between slis, slos and slas. 09:20–09:45 challenge 6 extend the contract query catalyst, then add realistic mappings and commitments to yesterday’s contract. 09:45–10:00 break 10:00–10:15 review and present a contract review a submitted contract in markdown and generate a readable html version. 10:15–10:45 mappi 

- use the opening examples to establish that a product must serve a particular consumer and purpose. ask what promises make the data usable, who owns those promises, and what enforces them. 

- for challenge 2 , ask each group to choose an opening example or propose a new cg product. give them these questions: 

- have groups note their most difficult or surprising question. early finishers can examine a second product. 

- in the debrief, follow the product beyond an api or intermediate system to the person making a decision. use examples such as advisor/client master data, global differences in definitions, and fragmented engagement data. press for a clear consumer and business owner. 

- ask: “what changes for the person using this?” a platform name or api describes part of the implementation; ask for the decision it supports. each group should leave challenge 2 with a named consumer, purpose and reason to proceed, plus one unresolved question. 

- when discussing lifetime value, include development, licences, data acquisition, maintenance, sme time, coordination, training, and opportunity cost. elicit benefits such as consistency, saved consumer time, trust, new insight, and new business opportunities. connect adoption barriers to practical responses: demonstrations, documentation, training, sponsorship, reliable commitments, and a better f 

- show how catalyst combines reusable prompts and templates with scripts and lifecycle workflows. inspect a contract template, including identity, schema, service commitments, and quality. demonstrate a specific skill before introducing broader orchestration. 

- for challenge 3 , partners must use the same product but keep their descriptions private until both prds are generated. ask them to compare scope, consumers, requirements, and assumptions. draw out how input detail changes the result. have each pair identify one correction or additional piece of context they would provide. pairs who finish first should exchange one requirement with another pair an 

- check: a tidy document can still contain invented fields, owners or approvals. use the planted contract errors if the live outputs do not give you a clear example. keep comparison to one or two differences so the activity finishes before lunch. 

- 1. what decision do you make with the data? 2. how do you make that decision today? 3. who uses the result directly? 4. how is the source generated? 5. what do the terms mean in your work? 6. how do you recognise a usable result? 7. when do you need the result? 

- record and transcribe the conversation. let groups move into collaborative discussion if the role play stalls. have them give the interview transcript to catalyst, generate a prd, then generate a data contract. they should inspect and correct both. 

- keep the interview within the 30 minute activity: about 5 minutes to choose the product and roles, 15 minutes for questions, and 10 minutes to generate and inspect the documents. if generation is slow, retain the interview notes and review one shared output. use the learner interview questions without assigning its longer 60 minute workshop. 

- compare interviews with observing consumers' work and surveying larger groups. emphasise follow up questions, tacit needs, and the difference between stated preferences and actual practice. 

- close by reviewing the prd's purpose, consumers, value, scope, requirements, and success criteria, then the contract's schema, rules, quality, dependencies, glossary, and change management. include invented revision history among the errors learners should check. 

- for challenge 5 , use 14:45–14:55 to ask catalyst for the nine lifecycle phases, build phase prerequisites, and the skills supporting those prerequisites. use 14:55–15:00 for each group to share one correction and the evidence behind it. check the answers against the current organisational guidance. keep the corrected prd and contract for day 2. 

- before learners leave: save the product notes, interview record, reviewed prd, contract and open questions together. the team worksheet provides a place to record evidence, assumptions, mappings and owners. learners should be able to explain one correction they made and why. 

- begin with source to target mapping (sttm): direct mapping, constants, lookups, aggregation, and derived transformations. use a small source and target example to show joins and column rules. retrieve the organisation's specific transformation categories through catalyst. 

- distinguish a measurable service level indicator (sli), its target (slo), and the agreement governing service commitments (sla). elicit latency, throughput, recovery time, delivery delay and time zone, completeness, accuracy, freshness, support turnaround, and availability. discuss replication, failover, load balancing, and disaster recovery where they help explain a commitment's cost. 

- use a submitted contract to demonstrate markdown preview and editing. generate a self contained html document with an overview, contents, explanatory prose, diagrams, and navigation. check whether the presentation makes the specification easier to review. 

- return to mapping detail before moving on: resolve identifiers, keys, edge cases, null meanings, and zero/minimum/maximum values. 

- ask: “could someone else implement this rule without asking you what it means?” for a lookup, check the join key and what happens with zero or several matches. for a promise such as “available by 07:30”, ask for the time zone, eligible days, measurement point and action on failure. finish challenge 6 with at least one unambiguous mapping and one measurable commitment. 

- trace the roles of git, catalyst, docker, dbt, databricks, s3, airflow/astronomer, and unity catalog. show where source data, transformations, compute, scheduling, version control, and deployment fit. explain the standard path and how to handle a justified exception. 

- cover relational structure, transactions and acid guarantees, distributed storage, hadoop/mapreduce, spark, and delta metadata and logs. use this progression to explain the training environment. 

- keep the distinction clear: git stores versions of code; docker provides the execution environment; dbt defines transformations and tests; databricks executes sql; airflow coordinates work; unity catalog governs and describes registered data. use the paved path diagram rather than drawing the whole stack from memory. 

- for challenge 7 , use a short classroom version of the docker project: run a prepared image, inspect a shell inside it, complete a small dockerfile, build it and run the result. pull the base image and prepare the supplied app before the session. the full docker guide includes additional tasks; keep the classroom exercise to the steps above and leave the rest for further practice. 

- ask: “why did the container stop, and what survives when you run a fresh one?” check that learners distinguish the image, the running process and its writable files. keep a working example ready for anyone blocked by engine access. pair learners who need support; offer extensions to experienced participants. 

- during challenge 8, pairs who finish the first implementation should choose one further question: how a missing input is handled, whether a lookup can duplicate rows, or what happens when the same input is processed twice. ask them to propose an expected result and a check, then report it during the debrief. experienced learners can investigate a bitemporal macro or airflow to datadog logging, kee 

- debrief in this order: dbt as elt; sql select , jinja, and yaml; tables, views, and materialisation; transactional and analytical workloads; run , test , build , debug , and seed ; then airflow dags, parallel tasks, python, blueprints, databricks operators, and dbt task groups. 

- finish by connecting generated code quality to contract quality. ask learners to explain a design choice, identify an edge case, and revise the specification or implementation. encourage annotation or dictated corrections when reviewing longer design documents. 

- if the code cannot run, review the files and expected behaviour. a learner with a working environment can show the output, but everyone should explain their own rule. at 14:50, give pairs 5 minutes to make or record one correction, then use the final 5 minutes to share the reasons and questions for day 3. 

- before learners leave: retain the revised mapping and commitments, generated project, useful commands and unresolved setup issues. each learner should be able to locate an output table and explain one transformation. record access problems separately from problems in the generated code. 

- use the dbt project for the task sequence and completion criteria. begin with sources and staging, then move into the intermediate models, marts and tests. use the optional variations when the core work is complete. ask learners to keep a list of commands, configuration changes, questions, and discoveries. support different working speeds without requiring everyone to stop at the same exercise. 

- ask: “could this join pass its tests and still double the reported value?” check the row grain, right side uniqueness, unmatched rows and an independent total. a successful build alone is insufficient. 

- for the supplied portfolio analytics case, keep the measure precise: holdings only gbp value divided by 100 million synthetic units, with cash excluded. it is not official fund nav. use the project’s reference checks for the exact results. the eight foundation questions provide short explanations when a learner is stuck. 

- use 14:30–14:45 for the recap. ask learners to explain examples from their own work; use the topic list to fill gaps rather than giving ten separate mini lectures. 

- from 14:45–14:55, pairs exchange one mapping rule and its test. the reviewer proposes a wrong result—a duplicated join, missing dated fx rate, or changed unit—and asks whether the test would catch it. agree one improvement and write the expected failure. during 14:55–15:00, ask for two or three examples, then save the work and questions for orchestration. 

- learners who complete the practical before the break should use a copied example to investigate one of those errors and explain its effect on the output. ask experienced learners to demonstrate both the failure and repair, with an independent value check. keep the original working project available for the next day. 

- before learners leave: keep the working dbt project, model/test results, an independent output check and the outstanding questions for orchestration. ask each learner to trace one plain english mapping through its model and test. confirm the airflow practice baseline is ready; completing advanced dbt is not a prerequisite for the next day. 

- check understanding by asking learners which time dimension answers a particular business or audit question. 

- for challenge 10 , use the airflow project and its completion criteria. prepare authentication, worker paths and the supporting dbt baseline before the timed work. follow the exercise sections in order; leave optional extensions until the core workflow works. establish the python foundations before moving to blueprint configuration. encourage learners to inspect task states and logs as they work,  

- for the supplied example, follow source_ready → dbt_build → quality → publication_evidence . ask learners to find the current run, inspect a useful log, and check the warehouse output. in the controlled failure, quality must block the final evidence task; removing the cause should allow a checked repaired run. 

- ask: “which run produced this result, and what proves the data is right?” keep the scheduled interval separate from the fixture’s business date. a parsed dag or green graph alone does not prove the warehouse result. keep credentials and path errors separate from the intended data quality failure. 

- use 13:30–14:00 for the deployment contribution. agree the agenda in advance: where code goes, how deployment is initiated, where execution is visible, and how failures are investigated. keep screenshots ready so the same discussion can run without live access. 

- after the 14:00–14:15 break, run a release decision exercise until 14:35. use the platform review example: a candidate has 500 rows but only 497 distinct ids, and yesterday’s accepted output is still available. give pairs 10 minutes to decide what should happen next and draft a two sentence update to the consumer; discuss their answers for 10 minutes. the failed candidate should remain blocked. wh 

- from 14:35–14:50, ask each pair to write a short note about its airflow failure and repair: the affected run, useful error, cause, action, output check, and anything still unresolved. swap notes for 5 minutes of that time: could another creator locate the run and explain what happened? if execution was blocked, use the prepared failure example and distinguish the expected behaviour from what was o 

- use 14:50–15:00 to check friday’s instructions, starting files and environment, and answer closing questions. record each remaining problem and the person responsible for resolving it. 

- preview friday's v1 capstone and the full instructions. phase 1 covers the required source loading, models, consumer outputs and orchestration; allow roughly two to three hours. phase 2 offers fourteen optional extensions for teams that complete and can explain the required work. this is a separate practical case from the cg example used during the teaching days. check that learners can locate the 

- before learners leave: retain the dag, run and task identities, useful logs, output check and a short explanation of the failure and repair. list any setup issue that could prevent starting friday’s work, with the person responsible for the next action. 

- run the course over four days, 09:00–15:00, with lunch from 12:00–13:00. plan activities through to 15:00 each day. keep the closing reviews in place, and use the suggested follow up questions when learners finish a practical sooner than others. adjust discussion and support within the session times while preserving the sequence. 

- learners develop one product from business need to requirements, contract, transformation code, and orchestration. carry their examples and artefacts forward between sessions. for the supplied technical exercises, use portfolio analytics for dbt and airflow and make the change of case explicit. 

- the timetable here sets the delivery order. learner links open supporting sections; their existing day labels and longer exercise timings do not change this schedule. 


## Paragraphs in the Cohort 7 PDF with no close match in the current instructor-plan.md

- data creators instructor plan · four days of teaching contents 

- course timetable 2 day 1 product discovery and effective ai use . . . . . . . . . . . . . . . . . . . . . . . 2 day 2 mappings service levels and implementation foundations . . . . . . . . . . . . 3 day 3 dbt practical and consolidation . . . . . . . . . . . . . . . . . . . . . . . . . . . 4 day 4 bitemporal loading and airflow orchestration . . . . . . . . . . . . . . . . . . . 5 

- daily learning objectives and teaching summaries 6 day 1 product discovery and effective ai use . . . . . . . . . . . . . . . . . . . . . . . 6 day 2 mappings service levels and implementation foundations . . . . . . . . . . . . 9 day 3 dbt practical and consolidation . . . . . . . . . . . . . . . . . . . . . . . . . . . 12 day 4 bitemporal loading and airflow orchestration . . . . . . . . . . . . 

- 09:00–09:20 mappings and service explain mapping rules and the distinction between commitments slis, slos and slas. 09:20–09:45 challenge 6 extend the query catalyst, then add realistic mappings and contract commitments to yesterday’s contract. 09:45–10:00 break 10:00–10:15 review and present a review a submitted contract in markdown and contract generate a readable html version. 10:15–10:45 mappi 

- day 1 product discovery and effective ai use learning objectives by the end of the day, learners should be able to: 

- summary start with learners’ existing products and pain points, then examine business justification, lifetime value, and adoption. introduce catalyst and effective ai practice before the interview challenge, where learners turn a conversation into a checked prd and data contract. close with the lifecycle and build prerequisites. 

- product discovery and justification use the opening examples to establish that a product must serve a particular consumer and purpose. ask what promises make the data usable, who owns those promises, and what enforces them. for challenge 2, ask each group to choose an opening example or propose a new cg product. give them these questions: 

- have groups note their most difficult or surprising question. early finishers can examine a second product. in the debrief, follow the product beyond an api or intermediate system to the person making a decision. use examples such as advisor/client master data, global differences in definitions, and fragmented engagement data. press for a clear consumer and business owner. ask: “what changes for t 

- consistency, saved consumer time, trust, new insight, and new business opportunities. connect adoption barriers to practical responses: demonstrations, documentation, training, sponsorship, reliable commitments, and a better fit with consumers’ work. 

- catalyst and independent prompting show how catalyst combines reusable prompts and templates with scripts and lifecycle workflows. inspect a contract template, including identity, schema, service commitments, and quality. demonstrate a specific skill before introducing broader orchestration. for challenge 3, partners must use the same product but keep their descriptions private until both prds are 

- effective ai practice teach the afternoon concepts in this order: 

- interview challenge for challenge 4, form new groups of three: 

- record and transcribe the conversation. let groups move into collaborative discussion if the role play stalls. have them give the interview transcript to catalyst, generate a prd, then generate a data contract. they should inspect and correct both. keep the interview within the 30 minute activity: about 5 minutes to choose the product and roles, 15 minutes for questions, and 10 minutes to generate 

- compare interviews with observing consumers’ work and surveying larger groups. emphasise follow up questions, tacit needs, and the difference between stated preferences and actual practice. close by reviewing the prd’s purpose, consumers, value, scope, requirements, and success criteria, then the contract’s schema, rules, quality, dependencies, glossary, and change management. include invented rev 

- day 2 mappings service levels and implementation foundations learning objectives by the end of the day, learners should be able to: 

- summary extend day 1’s contract with mappings and service commitments, then improve its presentation and resolve specification ambiguities. explain the platform architecture, practise docker, and use the contract to generate and investigate dbt and airflow implementation. 

- mappings and service commitments begin with source to target mapping (sttm): direct mapping, constants, lookups, aggregation, and derived transformations. use a small source and target example to show joins and column rules. retrieve the organisation’s specific transformation categories through catalyst. distinguish a measurable service level indicator (sli), its target (slo), and the agreement go 

- use a submitted contract to demonstrate markdown preview and editing. generate a self contained html document with an overview, contents, explanatory prose, diagrams, and navigation. check whether the presentation makes the specification easier to review. return to mapping detail before moving on: resolve identifiers, keys, edge cases, null meanings, and zero/minimum/maximum values. ask: “could so 

- action on failure. finish challenge 6 with at least one unambiguous mapping and one measurable commitment. 

- platform architecture and docker trace the roles of git, catalyst, docker, dbt, databricks, s3, airflow/astronomer, and unity catalog. show where source data, transformations, compute, scheduling, version control, and deployment fit. explain the standard path and how to handle a justified exception. cover relational structure, transactions and acid guarantees, distributed storage, hadoop/mapreduce 

- for challenge 7, use a short classroom version of the docker project: run a prepared image, inspect a shell inside it, complete a small dockerfile, build it and run the result. pull the base image and prepare the supplied app before the session. the full foundation phase takes 60–90 minutes; leave its additional tasks for further practice. ask: “why did the container stop, and what survives when y 

- generate and investigate implementation for challenge 8, have learners: 

- during challenge 8, pairs who finish the first implementation should choose one further question: how a missing input is handled, whether a lookup can duplicate rows, or what 

- happens when the same input is processed twice. ask them to propose an expected result and a check, then report it during the debrief. experienced learners can investigate a bitemporal macro or airflow to datadog logging, keeping their findings short enough to explain to the group. debrief in this order: dbt as elt; sql select, jinja, and yaml; tables, views, and materialisation; transactional and 

- if the code cannot run, review the files and expected behaviour. a learner with a working environment can show the output, but everyone should explain their own rule. at 14:50, give pairs 5 minutes to make or record one correction, then use the final 5 minutes to share the reasons and questions for day 3. before learners leave: retain the revised mapping and commitments, generated project, useful  

- day 3 dbt practical and consolidation learning objectives by the end of the day, learners should be able to: 

- summary centre the day on the self paced dbt challenges, with a guest session before lunch and continued practical work afterwards. use the closing recap to consolidate models, dependencies, tests, storage, catalogues, and materialisation, and prepare the next day’s guest contributions. 

- practical facilitation and recap use the dbt project for the task sequence and completion criteria. select the foundation tasks first; advanced work has its own starter and time budget. ask learners to keep a list of commands, configuration changes, questions, and discoveries. support different working speeds without requiring everyone to stop at the same exercise. as you circulate, check three th 

- ask: “could this join pass its tests and still double the reported value?” check the row grain, right side uniqueness, unmatched rows and an independent total. a successful build alone is insufficient. for the supplied portfolio analytics case, keep the measure precise: holdings only gbp value divided by 100 million synthetic units, with cash excluded. it is not official fund nav. use the project’ 

- 1. models and conventions: staging and integration models, cg naming conventions, and the sql behind the transformations. 2. dependencies and change: source documentation and the effects of source or schema changes. 3. testing and contracts: schema and value checks, quality rules, contracts, and catalogue information. 

- use 14:30–14:45 for the recap. ask learners to explain examples from their own work; use the topic list to fill gaps rather than giving ten separate mini lectures. from 14:45–14:55, pairs exchange one mapping rule and its test. the reviewer proposes a wrong result—a duplicated join, missing dated fx rate, or changed unit—and asks whether the test would catch it. agree one improvement and write the 

- day 4 bitemporal loading and airflow orchestration learning objectives by the end of the day, learners should be able to: 

- summary open with bitemporal loading and a worked history example, then introduce airflow and practise orchestration through the supplied challenges. follow with deployment and monitoring demonstrations, and finish by preparing learners for friday’s capstone. 

- bitemporal loading work through the presentation in this order: 

- airflow demonstration and practical teach the orchestration concepts in this order: 

- for challenge 10, use the airflow project and its completion criteria. prepare authentication, worker paths and the supporting dbt baseline before the timed work. select the foundation route; leave advanced recovery work for a separate session. establish the python foundations before moving to blueprint configuration. encourage learners to inspect task states and logs as they work, and use the dat 

- deployment and capstone preparation use 13:30–14:00 for the deployment contribution. agree the agenda in advance: where code goes, how deployment is initiated, where execution is visible, and how failures are investigated. keep screenshots ready so the same discussion can run without live access. after the 14:00–14:15 break, run a release decision exercise until 14:35. use the platform review exam 

- what happened? if execution was blocked, use the prepared failure example and distinguish the expected behaviour from what was observed. use 14:50–15:00 to check friday’s instructions, starting files and environment, and answer closing questions. record each remaining problem and the person responsible for resolving it. preview friday’s capstone: a minimum certification phase of roughly two to thr 

- before the course run the course over four days, 09:00–15:00, with lunch from 12:00–13:00. plan activities through to 15:00 each day. keep the closing reviews in place, and use the suggested follow up questions when learners finish a practical sooner than others. adjust discussion and support within the session times while preserving the sequence. learners develop one product from business need to 

