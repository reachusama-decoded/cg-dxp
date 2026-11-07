# Day 2


## Challenge: Create an STTM and use a transcript to create a PRD (11am)

* use apple voice memos on your macbook CG laptops to record the conversation
* define an STTM for a new data product or existing you've discussed
    * consider multiple input tables as sources
    * and what specific rules are required to produce the consumer aligned table
    * ask catalyst for STTM rule types
    * discuss these rule types and what's relevant for your use case
    * add tables to inputs if not interesting enough
* Take the transcript from apple voice memos and add it to copilot catalyst
    * Create a product requirements document from the transcript. 

```/ai-catalyst product-requirements-document``` OR
```/product-requirements-document```


### Group: Still Roaming... 

* Consolidating information on all CG products
    * wholistic view...
* Use transcript to generate PRD
* Generate STTM mapping ( direct maps?)
* Asked for suggested rules
    * eg., append, round-up... 




### Group: Yak Yak, yugyuygighghg 

* Data product: end of day instrument prices
* Talked about data reqs... use transcript to created PRD
* Reviewed doc... talked about STTM rules
* Found existing dataset... 
* Transforms:
    * USD currency prices, only CG price plan
    * CGTC --- price plan by currency 
    * look up rule for currency ID
* Edge cases... decimal, null...


### Group

* People data.... employees at CG
* Recorded talking thru STTM of employee data
* Direct rules... one application for associaes, one for contractors...
* Transforms: concats for names, ... 
* Fed into catalyst for PRD...
* very accurate PRD... and caught issue with terminal dates being non-nullable 




: We still need a group name?! No.