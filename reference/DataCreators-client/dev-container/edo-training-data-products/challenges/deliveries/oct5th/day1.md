# Data Creators, Day 1

## SLIs, SLAs, SLOs


* Service level indicator
    * metric -- measurable quantity which operationalizes a promise 
* Service level objective
    * ideal value of an indicator 
* Service level agreement
    * permissible departure from ideal SLO 

* Ideal value of "delay" could be... zero... 
* within 1 day 


* SLIs
    * delay 
    * successful requests  / time 
    * uptime -- 
        * 90 - a month
        * 99 - a working week
        * 99.9 - a working day 
        * 99.99 - an hour
        * 99.999 - a minute 
    * thruput, latency
        * throughput -- count of req / sec
        * latency -- time to first response 
    * recovery time
        * service goes down, time to back up
    * recovery point...
        * how much, or duration, of data loss 
    * exceptions...
        * data exceptions... 
    * response time (eg., email)
        * price, volume...



Spend 20-5min creating your two contracts & comparing them. Iterate on the data contract when its created. Provide more informaton, increase the quality.
Use copilot effectively to improve the accuracy
and completeness of the contract sections. 


Challenge ends ~12.15pm -- We're back here at 1.30pm 

Work in pairs.. or otherwise, produce two contracts
for "the same product" and comapre them...

What are the differences?
Which ones are better?
Anything concerning you notice? Incorrect?
Anything impressively correct?

What model did you use?
Did changing the model, change the output?
What effort level? 
Did changing the effort level?


What prompt did you use to improve the contract?


* what was the data product? who did what?
* what did you spend most time talking about?
* what was suprising, complex, difficut, intersting about the interview?


## Group: 🤣 🤣 

* user profile data...
* defref(joel) = data creator...
    * SLAs around notifications on late data...
    * support different SLAs --- under different contracts?
    * we dont need to support historical data?
    * volume is low for now....
    * PII, data sensitivity..
* currently: product is an API.. could this be in a different form. 


## Group: 🤔

* producer giving prices of all products CG sells
    * reporting, analysis... 
    * global prices 
* consumer requires specific US market not global
    * SLAs around timing critical, esp. data contract
    * "real time"
    * delay report if data incomplete... 
* does it need to be real time?
    * ... real time in engineering 
    * lack of clear adoption, freq. of visit.. theref. not RT
    * what are the options with missing data?
    * they require pricing on all the products... 
    *
## Group: 😉 😮‍💨 🙃

* what sections of the data contract could be filled out by the interview?
    * a suprising amount!
* data product: market comparison, or internal product comparison
    * eg., 20 yr return on mutual fund, perf. of ETF
    * faster to respond to sales questions 





## Challenge: Designing Data Products with Interviews (2.15pm)

Choose an existing data product, one you have discussed
... or you could try to come up with one (hard).

Producer is the specialist on the existing data sources, or data products

Consumer is the person who needs a new data product

Data creator is the interviewer of both....

Consider the following questions, but ask open ended questions that you would need  to ... to eventually, create a data contract...

* What decisions depend on the data?
* What happens when the data is late?
* What work around or existing products or practices are there?
* What would an ideal data product look like?

And think about:

* What makes the data product of value / desirable?
* What would make the data product useful?
* How would the consumer recommend adopting, etc.?
* How does the interview help fill-out the data contract?
* What sections of the data contract does the interview help fill?



## Challenge: Designing Data Products

* Data Product?
* Feasible?
* Desirable?
* Design?
* Access, Adoption?


### Group: "We need a nyoo! team name?!?!?!?!??1111...1one1.1one..!?"
* Data Product?
    * EM Screener... Emerging Markets 
        * domain: fixed income securities .. gov bonds/corp bonds..
    * Design?
        * already exists on databricks accroding to The Paved Path !
        * up-stream: bloombergy, internal refernce data
        * front-end UI: long list of securities, searchable by reference fields.. 
    * Feasibility?
        * internal proof of concept... skunkworks... 
            * can one person use AI to create a data product? YES!!!
            * we have a person...
    * Desiability?
        * is it that usefu?
    * Adoption?
        * for analysts and PMs who specialize in EM bonds...
        * "unowned bonds" tools exists... but each PM uses different tool etc. 
        * "all in one place" seems great value to them...
        * doesnt solve clear pressing problem for potential users... 
        * 60-70% not interested in buying.. 
        * no "front-door" owner to tackle... 
        * lack of familairty with workflows of PM 


### Group: Cabled Employee Access

* Product Research portal...
    * consumer: internal, external advisors, ...
* Feasible? Yes, we have the data, different places 
    * licences? constracts? ... we will get.... 
    * Team of people exists...
    * months...
    * priotisation...
* Desirable?
    * Retiring existing application...
    * ... new system lacks information
* Design?
    * web portable, AI discoverability... 
    * integrate with a chatbot... or something like that... 
    * chatbot needs to have product infor. 
* Adoption?
    * internal associates already spend days to access this info...
    * massive time savings... instantly access. 
    * lack of trust... data quality..
        * ease of access... affordance 

### Group: Wireless Guest Access

* Security xref Asset Data Product
* desire? 
    * save millions of dollars.... maintaining homegrown soln with existing dev/maintaince, transactions
    * focus on results... 
    * team solves problem of security mapping.. ie., team specialization.. 
* feasible..
    * have dara, we have resouces... we already known what to do... 
* What is the effort needed for your team to use homegrown soln... vs., product?
    * we'll absorb most of the switching costs... 
    * people don't like change... safety... 
* Rule?
    * equity security... icalkwuhwii34kqicif 
        * for express...

        * XF4-Q -> 66619 





## What are Data Products?

* Three views:
    * promises
        ..
    * alignment
        * source -> consumer alignment
        * source = data meets THEIR!!! needs
        * consumer = data meets OUR needs!
    * assets... 
        * data + code + infra/platforms
* Trustworthy dataset?
* not a platform...

* at least: dataset...
* business objective...


---


## Challenge Debrief: Data Pain Points 

* Shared hobbies?
* Data Products?
* Pain points?


### Group: Three Musckateers 

* children... lego...
* Data Products:
    * exchange rates
    * asset info: listing issuer instrument 
    * positions, corp actions... 
    * security xref. -- eg., vendor A security ID <-xref-> instrument ID 
* Pain points:
    * multiple contracts for the same information which we publish...
        * multiple output formats: APIs, files, etc. 
        * multiple consumers.. etc. 
        * pain to introduce new field
    * eg., 48 downstream apps



### Group: We are the whiners (, roamers....)

* Travelling
* Profile management, advisor related information... org...
    * participant outcome data... "data product" --- brining client data to CG
        * run email campaigns.. analytics.. 
    * biz unit, "participant outcome" -- "I can retire" 
        * --- value-add exp. for institutional clients... 
        * educate employees to contribute to retirement...
* Pain points -- 
    * integration (up = 3rd party.., downstream = multiple consumers, realtime)
    * clients give data without following data contract.. 

### Group: We need a group name??!

* Tennis, pickleball? 
* Data Products?
    * revenue, payroll, people, expenses
    * derivative risk dashboard
* Pain points?
    * vendor data issues.. timelineness, quality, changing format
    * payroll vendors could be small suppliers --- manually generated small files...
        * data entry people are .............. malicious...... and add additional columns?!?!
    * .... 





