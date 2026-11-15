# Issue tracker: local Markdown files

Issues, PRDs and tickets for this repo live as Markdown files under `.scratch/`, not on GitHub. Do not create GitHub issues.

`.scratch/` is gitignored: tickets exist only on this machine and are never committed. Do not add them to git.

## Layout

One folder per feature (or effort), one file per ticket:

```
.scratch/
└── <feature-slug>/
    ├── README.md              ← index: goal, links to design docs, ticket table
    └── issues/
        ├── 00-<slug>.md
        ├── 01-<slug>.md
        └── ...
```

- Number tickets with two digits in suggested work order (`00`, `01`, …). Numbers are per feature folder.
- The README's ticket table lists every ticket with its number, title (linked), status and blockers. Keep it in sync whenever a ticket is created, closed or re-blocked.

## Ticket format

Each ticket file starts with a title and a header block, then free-form body (what to do, acceptance criteria as `- [ ]` checkboxes):

```md
# 03. <title>

狀態：open
Blocked by：02、00 的 D1
Labels：ready-for-agent

## 要做什麼
...

## 驗收條件
- [ ] ...
```

- **狀態**: `open`, `done`, or `wontfix`. When done, append the commit hash, e.g. `done（b3cd585）`.
- **Blocked by**: ticket numbers in the same folder (or `無`). A ticket is unblocked when every blocker is `done`.
- **Labels** (optional): triage labels from `docs/agents/triage-labels.md`.
- Ticket content is written in Traditional Chinese for human readers.

## When a skill says "publish to the issue tracker"

Create a ticket file in the relevant `.scratch/<feature-slug>/issues/` folder (create the folder and README if the feature is new), and add it to the README table.

## When a skill says "fetch the relevant ticket"

Read the ticket file. If only a number is given, look it up in the feature README's table.

## Comment / close / label

- **Comment**: append to a `## 紀錄` section at the bottom of the ticket, dated (e.g. `- 2026-11-15：...`).
- **Close**: set `狀態` to `done（<commit>）` or `wontfix`, and update the README table.
- **Label**: edit the `Labels` line.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(`/triage` reads this flag.)_

## Wayfinding operations

Used by `/wayfinder`. The **map** is the feature folder's `README.md`; its tickets are the files in `issues/`.

- **Map**: `README.md` holds the Notes / Decisions-so-far / Fog sections plus the ticket table.
- **Child ticket**: a file in `issues/`. Add `類型：research | prototype | grilling | task` to its header.
- **Blocking**: the `Blocked by` line.
- **Frontier query**: open tickets whose blockers are all `done` and that have no `負責人` line; first in number order wins.
- **Claim**: add `負責人：<name>` to the header. This is the session's first write.
- **Resolve**: append the answer to `## 紀錄`, set `狀態` to `done`, then add a one-line pointer (gist + link to the ticket file) to the README's Decisions-so-far.

## Legacy GitHub issues

GitHub issues #1 and #2 predate this convention. They are not migrated; leave them alone unless the user asks.
