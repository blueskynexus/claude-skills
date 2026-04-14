# claude-skills

Downloadable Claude skill packs powered by the [viaNexus MCP server](https://vianexus.com/vast/#panel-mcp-service) and the [MT Newswires Claude connector](https://vianexus.com/vast/#sub-connect-mtnewswires). Drop any of these into Claude to give it institutional-grade financial workflows out of the box.

> **New to viaNexus?** [Start here](https://vianexus.com/vast/) — **VAST** (viaNexus Agentic Service Technology) covers what VAST is, how to connect Claude, and the full dataset catalog.

---

## Skills

| Skill | What it does | Data |
|-------|--------------|------|
| [**financial-research**](./financial-research) | Equity research briefing — valuation, fundamentals, forward estimates, peer comparison, next earnings date. | viaNexus `summary_normalized_financials`, `truebeats_eps_revenue_forecasts`, `earnings_calendar`, `company_descriptions` |
| [**mt-newswires-analyst**](./mt-newswires-analyst) | Real-time financial news briefings for tickers, sectors, or market themes. | MT Newswires (`mt_newswires_north_america`, `mt_newswires_global`) |
| [**transcript-analysis**](./transcript-analysis) | Earnings call + corporate event breakdown — management quotes, guidance, analyst Q&A, tone. | viaNexus Aiera (`events_calendar`, `historical_events_transcripts`) |
| [**portfolio-monitor**](./portfolio-monitor) | Daily portfolio brief combining quotes, alerts, and news for user-supplied holdings. | viaNexus (`quote`, `advanced_dividends`, `advanced_splits`) + MT Newswires |

---

## Install

Each skill is a directory with a `SKILL.md`. Three steps:

### 1. Connect the data source in Claude

You need **one** of these active in Claude before the skills will work:

- **viaNexus MCP server** (recommended — unlocks all 40 datasets)
  Full walkthrough: [vianexus.com/vast/#sub-connect-vianexus](https://vianexus.com/vast/#sub-connect-vianexus)
  Endpoint: `https://vast.blueskyapi.com/vianexus/mcp`
  Sign up for an API token: [console.blueskyapi.com/auth/register](https://console.blueskyapi.com/auth/register)

- **MT Newswires Claude connector** (news-only subset, easiest to enable)
  Step-by-step guide: [vianexus.com/vast/#sub-connect-mtnewswires](https://vianexus.com/vast/#sub-connect-mtnewswires)
  Available in Claude's Browse connectors library.

Other MCP clients (OpenAI, custom): [vianexus.com/vast/#sub-connect-openai](https://vianexus.com/vast/#sub-connect-openai)
SDK for building your own agents: [vianexus.com/vast/#panel-sdk](https://vianexus.com/vast/#panel-sdk)

### 2. Install the skill

Pick one method:

**Method A — folder (Claude Code, desktop CLI):**
```bash
cp -r financial-research ~/.claude/skills/
```

**Method B — .skill zip (Claude web/desktop app):**
```bash
cd financial-research && zip -r ../financial-research.skill .
```
Then upload `financial-research.skill` in Claude's skills settings.

### 3. Trigger it

Just ask Claude a question that matches the skill. Each skill has a `description` in its `SKILL.md` frontmatter that Claude uses to auto-select.

| Skill | Example prompts |
|-------|-----------------|
| financial-research | "Research AAPL" · "What's NVDA's forward P/E?" · "Compare MSFT to GOOGL" |
| mt-newswires-analyst | "Any news on Tesla today?" · "Oil sector briefing" · "Chevron analyst ratings" |
| transcript-analysis | "Summarize AAPL's last earnings call" · "What did Nvidia say about AI demand?" |
| portfolio-monitor | "How's my portfolio today? AAPL 100, MSFT 50, NVDA 25" · "Any movers in my holdings?" |

---

## Datasets reference

These skills tap a small slice of the full viaNexus catalog. Browse everything at:

- **Full catalog UI:** [console.blueskyapi.com/catalog](https://console.blueskyapi.com/catalog)
- **On the VAST page:** [vianexus.com/vast/#sub-mcp-available](https://vianexus.com/vast/#sub-mcp-available) (grouped by provider: MT Newswires, Aiera, ExtractAlpha, BMLL, SavaNet)
- **Docs:** [console.blueskyapi.com/docs/vast](https://console.blueskyapi.com/docs/vast)

40 datasets total — 14 CORE (market data, fundamentals, reference) + 26 EDGE (news, transcripts, estimates, alternative data).

---

## Compatibility

All skills are tested against the viaNexus MCP tool schemas: `fetch`, `search`, `current_date`.

The `mt-newswires-analyst` skill also works standalone with the MT Newswires Claude connector (EDGE / MT_NEWSWIRES datasets only — other skills need the full viaNexus MCP).

Each skill's `SKILL.md` declares its `compatibility.tools` array so Claude knows which connectors satisfy it.

---

## Requesting a new skill

This repo is **curated** — skills are authored and verified by the viaNexus team against live MCP data before being published. External PRs adding new skills will not be merged.

Have an idea for a skill you'd like us to build? Email [contact@vianexus.com](mailto:contact@vianexus.com) or open a [GitHub issue](https://github.com/blueskynexus/claude-skills/issues) describing the workflow you want (tickers, datasets, output shape). If it fits the roadmap, we'll build, test, and ship it.

---

## Links

- **VAST page:** [vianexus.com/vast](https://vianexus.com/vast/)
- **Data catalog + pricing:** [console.blueskyapi.com/catalog](https://console.blueskyapi.com/catalog)
- **Docs:** [console.blueskyapi.com/docs/vast](https://console.blueskyapi.com/docs/vast)
- **Register for an API token:** [console.blueskyapi.com/auth/register](https://console.blueskyapi.com/auth/register)

---

## License

MIT
