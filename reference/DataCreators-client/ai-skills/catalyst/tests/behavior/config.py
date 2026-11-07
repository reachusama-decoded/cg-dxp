from __future__ import annotations
import os
import re
from dataclasses import dataclass

ENV_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")

@dataclass
class Config:
    anthropic_api_key: str | None
    test_catalog: str | None
    test_schema: str | None
    test_databricks_host: str | None = None
    test_databricks_token: str | None = None
    test_databricks_warehouse_id: str | None = None
    test_confluence_page_id: str | None = None
    test_confluence_page_title: str | None = None
    test_confluence_space: str | None = None
    runner_model: str = "claude-sonnet-4-6"
    judge_model: str = "claude-sonnet-4-6"
    judge_temperature: float = 0.0
    # Tools the runner is pre-authorized to call without an interactive prompt.
    # Catalyst skills today need: Bash (to drive databricks SDK / shell), Read
    # (skill source files), Glob / Grep (repo navigation). Override per case
    # via `--allowed-tools`; anything outside this list still goes through the
    # default permission flow.
    allowed_tools: tuple[str, ...] = ("Bash", "Read", "Glob", "Grep")
    # JSONL transport buffer for the runner. SDK default is 1 MB; large Bash
    # outputs (e.g. a full information_schema dump) routinely exceed that.
    max_buffer_size: int = 32 * 1024 * 1024
    # Hard ceiling on agent turns per case, applied even when the case YAML
    # sets a higher max_steps. Prevents an agent that hits a wall (e.g.
    # permission denial it can't recover from) from thrashing through the
    # entire session budget — we observed a 47-min, 34K-token failure mode.
    # Tune via $BEHAVIOR_TESTS_MAX_TURNS_CEILING.
    max_turns_ceiling: int = 60
    # Wall-clock timeout per case. max_turns_ceiling alone isn't enough
    # because a single turn that calls Agent or thrashes Bash can run
    # 5-10 min. With ceiling=60 and 10 min/turn, a single case could
    # eat 10 hours. Cap at 6 min by default.
    # Tune via $BEHAVIOR_TESTS_CASE_TIMEOUT_S.
    case_wall_clock_timeout_s: int = 360
    # Hard per-case dollar backstop. Catches anything that slips past
    # turn / wall-clock bounds (e.g. one huge-context turn that costs
    # more than the typical case). $5 is ~10× a heavy case (observed
    # ~$0.50/case for orchestrators with sub-agents) — runaway-only,
    # not a budget squeeze. None disables. Tune via
    # $BEHAVIOR_TESTS_MAX_BUDGET_USD.
    max_budget_usd: float | None = 5.00
    # Domains the macOS bash sandbox lets the agent reach. Default covers
    # Capital Group's Databricks workspaces, Atlassian Cloud (Confluence +
    # Jira), and internal AWS endpoints. Override via
    # $BEHAVIOR_TESTS_ALLOWED_DOMAINS (comma-separated) so other orgs can
    # point this at their own gateways.
    allowed_network_domains: tuple[str, ...] = (
        "*.cloud.databricks.com",
        "*.databricks.com",
        "*.atlassian.net",
        "*.capgroup.com",
        "*.aws.capgroup.com",
    )

    @classmethod
    def from_env(cls) -> "Config":
        env_tools = os.getenv("BEHAVIOR_TESTS_ALLOWED_TOOLS")
        max_buf_env = os.getenv("BEHAVIOR_TESTS_MAX_BUFFER_BYTES")
        max_turns_env = os.getenv("BEHAVIOR_TESTS_MAX_TURNS_CEILING")
        case_timeout_env = os.getenv("BEHAVIOR_TESTS_CASE_TIMEOUT_S")
        budget_env = os.getenv("BEHAVIOR_TESTS_MAX_BUDGET_USD")
        domains_env = os.getenv("BEHAVIOR_TESTS_ALLOWED_DOMAINS")
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            test_catalog=os.getenv("TEST_CATALOG"),
            test_schema=os.getenv("TEST_SCHEMA"),
            # TEST_DATABRICKS_* falls back to the production DATABRICKS_* vars,
            # so existing setups keep working without test-specific creds.
            test_databricks_host=(os.getenv("TEST_DATABRICKS_HOST") or os.getenv("DATABRICKS_HOST")),
            test_databricks_token=(os.getenv("TEST_DATABRICKS_TOKEN") or os.getenv("DATABRICKS_TOKEN")),
            test_databricks_warehouse_id=(os.getenv("TEST_DATABRICKS_WAREHOUSE_ID") or os.getenv("DATABRICKS_WAREHOUSE_ID")),
            test_confluence_page_id=os.getenv("TEST_CONFLUENCE_PAGE_ID"),
            test_confluence_page_title=os.getenv("TEST_CONFLUENCE_PAGE_TITLE"),
            test_confluence_space=os.getenv("TEST_CONFLUENCE_SPACE"),
            runner_model=os.getenv("BEHAVIOR_TESTS_RUNNER_MODEL", "claude-sonnet-4-6"),
            judge_model=os.getenv("BEHAVIOR_TESTS_JUDGE_MODEL", "claude-sonnet-4-6"),
            allowed_tools=(
                tuple(t.strip() for t in env_tools.split(",") if t.strip())
                if env_tools
                else ("Bash", "Read", "Glob", "Grep")
            ),
            max_buffer_size=int(max_buf_env) if max_buf_env else 32 * 1024 * 1024,
            max_turns_ceiling=int(max_turns_env) if max_turns_env else 60,
            case_wall_clock_timeout_s=int(case_timeout_env) if case_timeout_env else 360,
            max_budget_usd=(float(budget_env) if budget_env else 5.00),
            **(
                {"allowed_network_domains": tuple(d.strip() for d in domains_env.split(",") if d.strip())}
                if domains_env else {}
            ),
        )

    def substitute(self, s: str, *, strict: bool = True) -> str:
        """Expand ${VAR} placeholders. strict=False replaces unset vars with
        '<unset:VAR>' instead of raising — useful for dry runs in fake-runner mode.
        """
        def _replace(m: re.Match) -> str:
            name = m.group(1)
            value = os.getenv(name)
            if value is None:
                if not strict:
                    return f"<unset:{name}>"
                raise KeyError(f"Env var ${{{name}}} is not set")
            return value
        return ENV_PATTERN.sub(_replace, s)
