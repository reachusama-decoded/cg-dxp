# Turn on Copilot Chat usage reporting

*Takes about 5 minutes. You need to edit one settings file and restart VS Code — no software to install.*

When you turn this on, VS Code reports **how** you use Copilot Chat — how many
chats, which models, how long responses took, whether anything errored. The EDO
team uses it to see which AI Catalyst skills are earning their keep and where
people get stuck.

It does **not** report what you typed or what Copilot replied. See
[What gets reported](#what-gets-reported) below.

## Before you start

- AI Catalyst is installed and working in VS Code — if not, start with
  [Install AI Catalyst](install.md)
- You're signed in to **GitHub Copilot Chat** with your Capital Group account
- You're **on the Capital Group network** — in the office, or connected to VPN.
  This won't work from a home network with the VPN off

## Step 1 — Open your settings file

1. Press `Ctrl+Shift+P` (Windows) or `⌘⇧P` (Mac)
2. Type **Preferences: Open User Settings (JSON)**
3. Press Enter

A file opens containing your VS Code settings. It looks something like this,
possibly with more lines in the middle:

```json
{
  "editor.fontSize": 13
}
```

## Step 2 — Add your settings

Paste this just inside the **first** `{`, replacing `KXY` with your own
Capital Group ID:

```json
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.exporterType": "otlp-http",
  "github.copilot.chat.otel.otlpEndpoint": "https://catalyst-otel.datalake.aws.capgroup.com",
  "github.copilot.chat.otel.captureContent": false,
  "github.copilot.chat.otel.resourceAttributes": {
    "user.id": "KXY"
  },
```

So the file ends up looking like this:

```json
{
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.exporterType": "otlp-http",
  "github.copilot.chat.otel.otlpEndpoint": "https://catalyst-otel.datalake.aws.capgroup.com",
  "github.copilot.chat.otel.captureContent": false,
  "github.copilot.chat.otel.resourceAttributes": {
    "user.id": "KXY"
  },
  "editor.fontSize": 13
}
```

Then save: `Ctrl+S` / `⌘S`.

**If you see red squiggly underlines**, it's almost always a comma. Every line
inside the `{ }` needs a comma at the end *except the last one*. Fix the commas
and the squiggles go away.

Two things to get right:

- **`user.id` must be your own ID** (the one you sign in with, e.g. `KXY`).
  It's what attributes the usage to you — without it your activity is
  anonymous and can't be counted.
- **Leave `captureContent` set to `false`.** That's the setting that keeps your
  conversation text out of the report.

These must go in **User** settings, not Workspace settings — Copilot ignores
them anywhere else.

## Step 3 — Reload the window

This is the step people miss, and nothing works without it.

Press `Ctrl+Shift+P` / `⌘⇧P`, type **Developer: Reload Window**, press Enter.

Reporting only starts when the settings are re-read, so saving the file on its
own does nothing.

That's it. You're done.

## How do I know it worked?

You won't see anything in VS Code — there's no icon or notification, by design.
Reporting runs quietly in the background and never interrupts you.

If you want it confirmed, use Copilot Chat for a few minutes and then ask the
EDO team to check that your data arrived. They can see it within a minute or two
of you using chat.

If you'd rather check the settings took, reopen the settings file from Step 1 and
confirm the four lines are still there and there are no red squiggles.

## What gets reported

**Reported:**

- That a Copilot Chat request happened, and when
- Which model answered, how long it took, how many tokens it used
- Whether it succeeded or errored
- The ID you set as `user.id` in Step 2, so usage can be counted per person

**Not intended to be reported** — what you typed, what Copilot replied, and your
code or file contents.

The `captureContent: false` line in Step 2 is what draws that line, and you should
leave it alone: turning it on would require a formal review by Governance, Risk &
Compliance.

One honest caveat while it is being checked. Conversation-shaped fields have been
seen arriving in the **dev** collector, and it is not yet established whether
`captureContent: false` suppresses them or whether Copilot Chat sends them
regardless of the setting. That is being determined under
[AICAT-336](https://capitalgroup.atlassian.net/browse/AICAT-336). It does not
change what you should do — leave the setting as shown — but until it is answered
this page should not promise more than it can. Treat Copilot Chat the way you
already treat any tool that leaves the machine, and if you have questions about
what is stored or how long it is kept, ask the EDO team.

## If it isn't working

**I set it up and the EDO team says no data is arriving**

- You probably didn't reload the window. Redo [Step 3](#step-3--reload-the-window) — this is the cause the vast majority of the time.
- If a reload didn't do it, **fully quit** VS Code (`⌘Q`, or close every window
  on Windows) and reopen. That always picks the settings up.
- Check the settings went into your **User** settings, not a workspace or folder
  settings file. Reopen via Step 1, which always opens the right one.
- Give it a couple of minutes. Data is sent in batches, not instantly.

**I'm working from home**

You need to be connected to VPN. If you're on VPN and it still isn't working,
mention it to the EDO team — some remote VPN setups can't reach this service, and
they're actively tracking which ones.

**I want to turn it off**

Reopen the settings file from Step 1, delete the four lines you added, save, and
fully quit and reopen VS Code. Nothing further is sent.

## Questions

Ask the EDO team, or open an issue in
[`cg-open-itg/catalyst-otel`](https://github.com/cg-open-itg/catalyst-otel/issues).
