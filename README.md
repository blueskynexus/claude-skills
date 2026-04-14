# claude-skills

Downloadable Claude skill packs powered by the [viaNexus MCP server](https://vast.blueskyapi.com/vianexus/mcp) and the MT Newswires Claude connector. Drop any of these into Claude to give it institutional-grade financial workflows out of the box.

## Skills

| Skill | What it does | Data |
|-------|--------------|------|
| [**financial-research**](./financial-research) | Equity research briefing — valuation, fundamentals, forward estimates, peer comparison, next earnings date. | viaNexus `summary_normalized_financials`, `truebeats_eps_revenue_forecasts`, `earnings_calendar`, `company_descriptions` |
| [**mt-newswires-analyst**](./mt-newswires-analyst) | Real-time financial news briefings for tickers, sectors, or market themes. | MT Newswires (`mt_newswires_north_america`, `mt_newswires_global`) |
| [**transcript-analysis**](./transcript-analysis) | Earnings call + corporate event breakdown — management quotes, guidance, analyst Q&A, tone. | viaNexus Aiera (`events_calendar`, `historical_events_transcripts`) |
| [**portfolio-monitor**](./portfolio-monitor) | Daily portfolio brief combining quotes, alerts, and news for user-supplied holdings. | viaNexus (`quote`, `advanced_dividends`, `advanced_splits`) + MT Newswires |

## Install

Each skill is a directory with a `SKILL.md`. To use:

1. Connect the **viaNexus MCP server** or **MT Newswires Claude connector** in Claude.
2. Copy the skill directory into your Claude skills location (e.g. `~/.claude/skills/`) or zip it as `<skill-name>.skill` and upload.
3. Ask Claude something that matches the skill's triggers — it will auto-select the right one.

## Compatibility

All skills are tested against viaNexus MCP tool schemas: `fetch`, `search`, `current_date`.

The `mt-newswires-analyst` skill also works with the MT Newswires Claude connector (EDGE / MT_NEWSWIRES datasets only).

## License

MIT
