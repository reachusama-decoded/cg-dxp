# Catalyst Release Process

End-to-end steps to cut a **Catalyst platform** release. Pairs with:

- [`release-notes-guide.md`](release-notes-guide.md) — GitHub release notes format
- [`catalyst-release-comms-guide.md`](catalyst-release-comms-guide.md) — the email / Teams comms

> **Scope:** Catalyst product releases (new skills, fixes, improvements). Not for data products built with Catalyst.

## Versioning

- Semver `MAJOR.MINOR.PATCH`: new skills/features → **MINOR**, fixes-only → **PATCH**.
- **Source of truth for the version is `plugin.json`.**
- Tags are **annotated** and **unprefixed**: tag name `1.11.0` (not `v1.11.0`); annotation subject `v1.11.0 — <headline>` (matches prior tags `1.8.0`, `1.9.0`).
- Releases publish from an annotated tag on `main`.

## Scope — "what's in this release"

Scope from the **last published tag**, not from a staged-but-untagged version.

- `git tag --sort=-v:refname | head` shows the last real release.
- Everything merged since that tag's commit is in scope.
- **A version with a CHANGELOG entry but no tag/GitHub release was never shipped.** Confirm against the GitHub Releases page before scoping.

## Steps

1. **Bump the version** in `plugin.json`.
2. **Sync marketplace metadata:** `python scripts/sync_plugin_version.py` (then confirm `--check` passes). `marketplace.json` is generated — never hand-edit it.
3. **Refresh the skills graph:** `python scripts/build_skills_graph.py`. This is a *backstop*, not the primary trigger — the graph is regenerated when a skill PR merges, so at release it should be a no-op. It is idempotent, so running it costs nothing when the graph is already current and silently repairs it when a merge missed the step. Confirm with `python -m pytest tests/ci/test_skills_graph.py -q`.
4. **CHANGELOG.md** — add a dated `## YYYY-MM-DD — vX.Y.Z` section per [`release-notes-guide.md`](release-notes-guide.md), including a one-line thank-you for each contributor outside the core maintainers (see [Contributor credit](#contributor-credit)).
5. **Comms HTML** — create `docs/release-comms/releases/vX.Y.Z.html` per [`catalyst-release-comms-guide.md`](catalyst-release-comms-guide.md), and add a row for it to the **Release comms** list in `docs/index.html`. That list is hand-maintained; miss it and the new page publishes orphaned, reachable only by direct URL.
6. **Open the chore PR** — `chore(release): vX.Y.Z — <headline>`. Put the full GitHub-release narrative **in the PR body** (single source of truth — do not create a separate notes file). Request reviewers.
7. **Merge** to `main`.
8. **Tag + publish** on the merge commit:
   ```bash
   git checkout main && git pull
   git tag -a X.Y.Z -m "vX.Y.Z — <headline>"
   git push origin X.Y.Z
   gh release create X.Y.Z --title "vX.Y.Z — <headline>" --notes-file <notes>
   ```
9. **Mirror the onboarding FAQ to Confluence** — from the **merged, tagged** checkout:
   ```bash
   git checkout main && git pull
   python scripts/publish_faq_to_confluence.py --site-base <published-docs-url>          # dry run
   python scripts/publish_faq_to_confluence.py --site-base <published-docs-url> --apply
   ```
   Publishes `docs/getting-started-faq.html` as **AI Catalyst: Getting Started FAQ** under [AI Catalyst Onboarding](https://capitalgroup.atlassian.net/wiki/spaces/ENTDATA/pages/404951408/AI+Catalyst+Onboarding), beside [0 Pre-Req](https://capitalgroup.atlassian.net/wiki/x/6Y8jG). **After the merge on purpose:** the script reads the working tree, so running it earlier would push an unreviewed FAQ to a shared space that a reviewer could still reject. Idempotent — an unchanged FAQ is a no-op. See [Tooling notes](#tooling-notes).
10. **Send comms** from the HTML (see the comms guide).

## Contributor credit

- Add a **one-line thank-you per contributor outside the core maintainers** (currently **MRQL**, **RBLW**, **RYQF**). The release-chore author is never credited.
- In user-facing comms, use plain **initials** (e.g. "Thank you to AGGB"), not `@handle_capgroup`.

## Recovering a missed tag

If a version was bumped + changelogged (a chore PR merged) but **never tagged**, it was never released. Catch it up by tagging its historical commit:

```bash
git tag -a X.Y.Z <chore-merge-sha> -m "vX.Y.Z — <headline>"
git push origin X.Y.Z
gh release create X.Y.Z --title "vX.Y.Z — <headline>" --notes-file <notes>
```

Then scope the **next** release to only what merged *after* that commit — don't re-announce the caught-up content.

## Tooling notes

- **`publish_faq_to_confluence.py`** converts the FAQ rather than uploading it. Confluence storage format is a constrained XHTML dialect — it drops `<style>`, `class` and inline `style`, and renders callouts and code blocks through its own macros — so the presentational layer is stripped and the structure is translated (`div.note` → info macro, `pre>code` → code macro, the `link pending` chip → literal text). Pasting the file in by hand produces an unstyled wall of text with silently-lost structure, which is the failure this replaces.
  - `--site-base` is **required**: `href="./"` and `href="release-comms/…"` resolve against the published docs site, and the script refuses rather than publishing links that 404 for every Confluence reader.
  - `--print-storage` shows the converted body with no network call and no credentials, which is the cheap way to review a change before publishing.
  - The page carries a hash of the source HTML, so re-running on an unchanged FAQ is a no-op instead of a new version. It also carries a banner naming `docs/getting-started-faq.html` as the source of truth, because a Confluence page that looks editable will get edited.
  - Needs `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` from the repo-root `.env`.
  - **This release step is the only trigger, deliberately.** GitHub Actions are disabled org-wide and this repo has no Harness project, so there is nothing that can fire on merge. The consequence is accepted rather than overlooked: a FAQ change merged mid-cycle reaches Confluence at the next release, not at merge. Because the publish is idempotent and the dry run exits 1 only when a publish is actually pending, running it every release is cheap and catches the releases where the FAQ did change. If the lag ever matters, the options considered were a `pre-push` warning hook or a Harness pipeline.
- `gh pr edit` and reviewer edits go through GraphQL, which needs the `read:org` scope. With only `repo` scope, use REST instead:
  - Edit PR body: `gh api repos/<owner>/<repo>/pulls/<n> -X PATCH -F body=@body.md`
  - Request reviewers: `gh api repos/<owner>/<repo>/pulls/<n>/requested_reviewers -X POST -f 'reviewers[]=<login>'`
