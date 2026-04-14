---
name: mt-newswires-analyst
description: >
  Fetches and analyzes real-time financial news from MT Newswires for specific
  stocks, sectors, or market themes. Use this skill whenever the user asks about
  recent news for a stock ticker, oil companies, energy sector, market updates,
  analyst rating changes, insider trades, or any query like "what's happening with
  [company/sector]", "latest news on [ticker]", "oil company news", "energy market
  update", or "give me a briefing on [topic]". Always use this skill when MT
  Newswires is connected and the user wants current financial news — even casual
  asks like "any news on Tesla?" or "what's going on in energy today?" should
  trigger it.
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:current_date
    - viaNexus:search
    - MT Newswires:fetch
    - MT Newswires:current_date
    - MT Newswires:search
---

# MT Newswires Analyst

Fetches and synthesizes real-time financial news from MT Newswires, then delivers
a clear, structured briefing.

---

## Step 1 — Understand the Request

Identify from the user's message:
- **Tickers** (e.g. XOM, CVX, COP, BP, SHEL) — look for explicit symbols or company names you can map to symbols
- **Sector/theme** (e.g. oil, energy, tech, macro) — use a representative basket of tickers
- **Date scope** — default to today unless user says "this week" or specifies a range

Common oil/energy ticker mappings:
- ExxonMobil → XOM
- Chevron → CVX
- ConocoPhillips → COP
- BP → BP
- Shell → SHEL
- TotalEnergies → TTE
- Halliburton → HAL
- Energy sector broad → XOM,CVX,COP,BP,SHEL

---

## Step 2 — Get Today's Date

Always call `MT Newswires:current_date` first to anchor date-based queries.

---

## Step 3 — Fetch News

Call `MT Newswires:fetch` with:
- `dataset_name`: `mt_newswires_north_america` (default) or `mt_newswires_global` for non-US focus
- `endpoint`: `data`
- `product`: `edge`
- `symbols`: comma-separated tickers (e.g. `"XOM,CVX,COP,BP,SHEL"`)
- `last`: `10` to `20` depending on how much depth is needed
- `from_date` / `on_date`: use today's date from Step 2 if user wants today's news only

**Tip**: For sector-level queries (e.g. "oil news"), use a basket of 4–6 major tickers rather than a single one.

---

## Step 4 — Deduplicate and Prioritize

Articles often repeat across multiple tickers. Before summarizing:
- Deduplicate by `subkey` (unique article ID)
- Prioritize articles where `isPrimary: true` (the ticker is the main focus)
- Sort by `releaseTime` descending (most recent first)
- Flag `headline_only_story` articles — they have no body, just a headline

---

## Step 5 — Synthesize and Present

Structure the output as a briefing:

```
## [Sector/Company] News Briefing — [Date]

### 🔑 Key Themes
[2-3 sentence summary of the dominant story lines across all articles]

### 📰 Top Stories
1. **[Headline]** — [1-2 sentence summary. Source: MT Newswires, [time]]
2. ...

### 📊 Analyst Activity
[Any price target changes or rating actions, grouped by company]

### 🏦 Insider Trades
[Any SEC filings / insider buy/sell activity]

### ⚡ Market Context
[Oil prices, sector index moves, macro backdrop if mentioned]
```

**Rules:**
- Never fabricate quotes — paraphrase article bodies
- Flag "Market Chatter" stories as unconfirmed rumors
- If a story is headline-only (no body), note that and don't speculate on its content
- Keep the briefing scannable — bullets and short paragraphs, not walls of text
- If no relevant news is found, say so clearly and suggest broadening the date range or ticker list

---

## Example Triggers

- "Recent oil company news"
- "What's happening with XOM today?"
- "Give me an energy sector briefing"
- "Any analyst ratings changes on Chevron?"
- "Latest news on BP and Shell"
- "Insider trades at ConocoPhillips"
- "What's driving energy stocks today?"
