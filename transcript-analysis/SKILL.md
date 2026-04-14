---
name: transcript-analysis
description: >
  Extracts insights from earnings call transcripts and corporate events: key
  management quotes, guidance changes, analyst Q&A themes, and sentiment tone.
  Powered by Aiera transcripts through viaNexus. Use whenever the user asks about
  an earnings call, management commentary, guidance, or analyst questions — e.g.
  "summarize Apple's last earnings call", "what did Nvidia's CEO say about AI
  demand", "any guidance changes on the Tesla call", "pull quotes about margins
  from AMZN's Q2 call", "what are analysts asking Meta about", or "find the
  Microsoft transcript for their latest event".
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:current_date
---

# Transcript Analysis

Pulls Aiera earnings call and corporate event transcripts via viaNexus and produces
a structured breakdown of what management said, what analysts pushed on, and how
the tone shifted.

---

## Step 1 — Identify the Event

From the user's message, extract:
- **Ticker** (required)
- **Event window**: "latest" (default), "most recent quarter", or a specific date

## Step 2 — Find the Event

Call `viaNexus:fetch`:

- `dataset_name`: `events_calendar`
- `product`: `edge`
- `endpoint`: `data`
- `symbols`: the ticker
- `last`: `5` (shows most recent events)

Pick the right `eventId` / `subkey` based on `eventDate` and `eventType` (prefer
`earnings` unless the user asked for `shareholder_meeting`, `investor_day`, etc).

## Step 3 — Fetch the Transcript

Call `viaNexus:fetch`:

- `dataset_name`: `historical_events_transcripts`
- `product`: `edge`
- `endpoint`: `data`
- `symbols`: the ticker
- `subkey`: the `eventId` from Step 2 (or omit and use `last: 1` for most recent)

The response contains:
- `title`, `eventDate`, `eventType`, `publicShareUrl` (user-facing Aiera link)
- `transcripts`: array of speaker-tagged paragraphs with `speakerId`, `startMs`,
  `text`
- `people`: list of named speakers (management + analysts)
- `linguistics.sentiment` + `linguistics.topics` / `summaries` if present
- `hasTranscripts`: false means the event wasn't captured — fall back to an
  earlier event

Edge case: `transcriptionStatus: "missed"` → tell the user the event has no
transcript and suggest the prior earnings call.

## Step 4 — Structure the Transcript

Split `transcripts[]` into:
- **Prepared remarks** — speeches by management (CEO / CFO) before Q&A
- **Q&A** — alternating analyst questions and executive answers
  (use `people[]` to label speakers by name and affiliation)

## Step 5 — Synthesize

Output format:

```
## [Company] ([TICKER]) — [Event Type] — [Event Date]
[Aiera link: publicShareUrl]

### 🎤 Management Highlights (Prepared Remarks)
- **[CEO Name]**: "[direct quote]" — [one-line context]
- **[CFO Name]**: "[direct quote]" — [one-line context]
- 3–5 quotes total, focused on: strategy, product momentum, capital allocation

### 📊 Guidance & Outlook
- Revenue guidance: [what was said, vs prior]
- Margin commentary: [...]
- Segment-level callouts: [...]

### 🎯 Analyst Q&A Themes
Most-asked topics (count / lead analyst):
1. **[Theme]** — asked by [Analyst, Firm]: short paraphrase of push + management's
   answer.
2. ...

### 🎭 Tone
- Overall sentiment: [positive / cautious / defensive] — cite 1 line that
  supports it.
- If `linguistics.sentiment` is populated, report the average score.

### ⚠️ Notable
- Unusual admissions, guidance cuts, new disclosures, leadership changes.
```

**Rules:**
- Quote management verbatim — do not paraphrase direct quotes.
- Attribute every quote to a named person (look up via `speakerId` → `people[]`).
- If an analyst question is vague, paraphrase; if management's answer is
  non-committal, flag it.
- Never speculate about tone from the text alone if `linguistics.sentiment` is
  absent — just describe word choice.
- Always include the `publicShareUrl` so the user can replay the audio.

---

## Example Triggers

- "Summarize Apple's last earnings call"
- "What did Jensen say about AI demand on NVDA's Q4 call?"
- "Pull the transcript for Tesla's investor day"
- "Any guidance changes on AMZN's latest call?"
- "What are analysts pushing Meta on?"
- "Find MSFT's most recent earnings transcript"
