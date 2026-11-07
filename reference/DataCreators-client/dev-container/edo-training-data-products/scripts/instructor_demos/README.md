# Implementation boundaries

`contracts.py` rejects unknown story/schema fields, unsafe paths and drift.
`terminal.py` owns real PTYs and process groups; ANSI screen state is decoded by
pyte and presented in Chromium. Real output and input events remain private.
`browser.py` operates the actual application with Playwright locators.
`runner.py` records assertions/checkpoints, raw recordings and owned cleanup.
`publish.py` consumes reviewed, current evidence without running workloads.

Assertions are registered handlers (`output-contains`, `file-present`,
`file-absent`, `command`). Commands and story YAML are trusted local instructor
source, never untrusted learner input. `command` checks run argv directly.
Input source directories and shared runner/theme/schema bytes bind each capture.
Review is an explicit recorded inspection; no automatic screenshot approval.

UI draft stories are teaching contracts for the subsequent live rehearsal,
not complete scheduler/API verifiers. Draft status itself blocks capture. The
three ready local dbt stories have observed execution; Docker/advanced dbt/UI
contracts stay draft until their corresponding acceptance work is finished.
