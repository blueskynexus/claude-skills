# Update-loop architectures

Two ways a generated dashboard can refresh itself. Default to the first.

---

## A. Direct REST polling (default)

The page fetches `api.blueskyapi.com` straight from the browser on a timer.
Verified: the API sends `Access-Control-Allow-Origin: *`, so this works from
`file://`, localhost, or any host, with no proxy and no backend.

```js
const BASE = "https://api.blueskyapi.com/v1/data";

async function pollQuotes(symbols, token) {
  const url = `${BASE}/CORE/QUOTE/${symbols.join(",")}` +
    `?token=${encodeURIComponent(token)}&filter=${QUOTE_FIELDS}`;
  const t0 = performance.now();
  const res = await fetch(url);
  logCall("quote", symbols.length, res.status, performance.now() - t0);
  if (res.status === 401 || res.status === 403) throw new TokenError();
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

Loop skeleton — one in-flight request max, pause when hidden, keep stale data
on failure:

```js
let timer = null, busy = false;

function schedule(ms) {
  clearInterval(timer);
  if (ms) timer = setInterval(tick, ms);
}

async function tick() {
  if (busy || document.hidden) return;
  busy = true;
  try {
    render(await pollQuotes(ALL_SYMBOLS, getToken()));
    markFresh();
  } catch (e) {
    markStale(e);          // banner + keep last good render
  } finally {
    busy = false;
  }
}

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) tick();   // catch up immediately on refocus
});
```

Cadence guidance: 60s default. 30s is fine for ≤25 symbols. Don't go below
10s — quotes blend VNX realtime with 15-minute delayed SIP, so sub-10s polling
burns quota without showing meaningfully fresher data.

**Token handling**: read from a header input persisted to `localStorage`
(`vnx_token`). pk_ tokens only. The token rides in the query string by API
design; that's fine for a local file, but it means generated pages must never
be published with a token baked in.

## B. Agentic refresh via the Anthropic API MCP connector (advanced)

For the demo where the *model* is visibly in the loop: the page POSTs to the
Anthropic Messages API with the viaNexus MCP server attached, instructs the
model to make exactly one `fetch` tool call and reply "OK", then parses the
`mcp_tool_result` block from the response — **not** the model's text. Numbers
stay verbatim tool output; the model only pulls the trigger.

Requirements and costs, stated up front to the user:

- An **Anthropic API key** in the page (`anthropic-dangerous-direct-browser-access: true`
  header required for browser calls) — a second credential to protect.
- The MCP connector beta header (`anthropic-beta: mcp-client-2025-04-04`) and a
  `mcp_servers` entry for `https://vast.blueskyapi.com/vianexus/mcp` with the
  user's authorization token.
- Each refresh costs Anthropic tokens and adds seconds of latency vs. option A.

Sketch of the request body:

```js
{
  model: "claude-haiku-4-5-20251001",   // cheapest that reliably makes the call
  max_tokens: 300,
  mcp_servers: [{
    type: "url",
    url: "https://vast.blueskyapi.com/vianexus/mcp",
    name: "vianexus",
    authorization_token: VNX_TOKEN
  }],
  messages: [{
    role: "user",
    content: `Call the vianexus fetch tool exactly once: dataset_name=quote, ` +
             `product=core, symbols=${SYMBOLS}, filter=${QUOTE_FIELDS}. ` +
             `Then reply OK. Do not summarize the data.`
  }]
}
```

Then walk `response.content` for the `mcp_tool_result` block and parse its JSON.
Keep the call-log panel — with two APIs in the chain it's the only way users can
see which hop failed.

Use B only when the user explicitly wants the agentic demo; A is faster,
cheaper, and has one credential instead of two.
