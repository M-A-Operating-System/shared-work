#!/usr/bin/env python3
"""
Weekly AI research catalog update.

Reads docs/research/weekly-agentic-ai-research.md for task instructions.
Uses Claude Opus with extended thinking plus Exa and/or Tavily web search.

Writes:
  docs/research/research.json          — updated catalog
  docs/research/runs/YYYY-MM-DD.md     — run log
  docs/research/sources/YYYY-MM-DD.json — sources consulted

Search engines are selected automatically from available environment variables:
  SEARCH_EXA_KEY    — enable Exa neural search
  SEARCH_TAVILY_KEY — enable Tavily research search

Requires: ANTHROPIC_API_KEY
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import anthropic

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESEARCH_DIR = REPO_ROOT / "docs" / "research"
RESEARCH_FILE = RESEARCH_DIR / "research.json"
SCHEMA_FILE = RESEARCH_DIR / "inventory.schema.json"  # research.schema.json not yet created
INVENTORY_FILE = RESEARCH_DIR / "inventory.json"      # seed source if research.json absent
INSTRUCTIONS_FILE = RESEARCH_DIR / "weekly-agentic-ai-research.md"
RUNS_DIR = RESEARCH_DIR / "runs"
SOURCES_DIR = RESEARCH_DIR / "sources"

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ── File helpers ───────────────────────────────────────────────────────────────

def load_file(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8") if path.exists() else default


def load_catalog() -> str:
    if RESEARCH_FILE.exists():
        return load_file(RESEARCH_FILE)
    if INVENTORY_FILE.exists():
        print("research.json not found — seeding from inventory.json for this run")
        return load_file(INVENTORY_FILE)
    return "{}"


# ── Search engine calls ────────────────────────────────────────────────────────

def exa_search(query: str, num_results: int = 5, use_autoprompt: bool = True) -> dict:
    resp = requests.post(
        "https://api.exa.ai/search",
        headers={
            "x-api-key": os.environ["SEARCH_EXA_KEY"],
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "numResults": num_results,
            "useAutoprompt": use_autoprompt,
            "contents": {"text": {"maxCharacters": 2000}},
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def tavily_search(query: str, max_results: int = 5, search_depth: str = "advanced") -> dict:
    resp = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": os.environ["SEARCH_TAVILY_KEY"],
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


class _TextExtractor(HTMLParser):
    """Strips HTML tags, scripts and styles; returns readable text."""
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "header", "footer", "noscript"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "header", "footer", "noscript"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self._parts.append(stripped)

    def text(self) -> str:
        return " ".join(self._parts)


def web_fetch(url: str, max_chars: int = 8000) -> str:
    try:
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 ResearchBot/1.0"},
        )
        resp.raise_for_status()
        parser = _TextExtractor()
        parser.feed(resp.text)
        return parser.text()[:max_chars]
    except Exception as exc:
        return f"fetch error: {exc}"


# ── Tool definitions ───────────────────────────────────────────────────────────

def build_tools(exa: bool, tavily: bool) -> list:
    tools = []

    if exa:
        tools.append({
            "name": "exa_search",
            "description": (
                "Neural/semantic web search via Exa. "
                "Best for conceptual queries about AI technologies, frameworks, and platforms."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "default": 5, "description": "1–10"},
                    "use_autoprompt": {"type": "boolean", "default": True},
                },
                "required": ["query"],
            },
        })

    if tavily:
        tools.append({
            "name": "tavily_search",
            "description": (
                "Research-optimised web search via Tavily. "
                "Returns structured results with extracted content snippets."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 5, "description": "1–10"},
                    "search_depth": {
                        "type": "string",
                        "enum": ["basic", "advanced"],
                        "default": "advanced",
                    },
                },
                "required": ["query"],
            },
        })

    tools.append({
        "name": "web_fetch",
        "description": "Fetch the full text content of a URL for detailed reading.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "URL to fetch"}},
            "required": ["url"],
        },
    })

    tools.append({
        "name": "write_output",
        "description": (
            "Finalise the research run. Call exactly once when all research is complete. "
            "Provide the complete updated catalog and run artefacts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "updated_catalog": {
                    "type": "object",
                    "description": (
                        "Complete updated research.json content. "
                        "Full object — not a diff. Must validate against the schema."
                    ),
                },
                "run_log_markdown": {
                    "type": "string",
                    "description": (
                        f"Concise markdown run summary for docs/research/runs/{TODAY}.md. "
                        "Include: products added/updated, capabilities added, "
                        "reference implementations added, and human review items."
                    ),
                },
                "sources_json": {
                    "type": "object",
                    "description": (
                        f"Structured source list for docs/research/sources/{TODAY}.json. "
                        'Top-level keys: "date", "sources" (array of objects with '
                        '"title", "url", "relevance").'
                    ),
                },
            },
            "required": ["updated_catalog", "run_log_markdown", "sources_json"],
        },
    })

    return tools


# ── Tool execution ─────────────────────────────────────────────────────────────

def run_tool(name: str, tool_input: dict) -> str:
    if name == "exa_search":
        return json.dumps(exa_search(**tool_input), indent=2)
    if name == "tavily_search":
        return json.dumps(tavily_search(**tool_input), indent=2)
    if name == "web_fetch":
        return web_fetch(tool_input["url"])
    if name == "write_output":
        return json.dumps({"status": "acknowledged"})
    return f"unknown tool: {name}"


# ── Content block serialiser ───────────────────────────────────────────────────

def serialise_block(block) -> dict:
    if block.type == "thinking":
        return {"type": "thinking", "thinking": block.thinking}
    if block.type == "text":
        return {"type": "text", "text": block.text}
    if block.type == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    return {"type": block.type}


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is required", file=sys.stderr)
        sys.exit(1)

    exa_available = bool(os.environ.get("SEARCH_EXA_KEY"))
    tavily_available = bool(os.environ.get("SEARCH_TAVILY_KEY"))
    engines = ", ".join(filter(None, [
        "Exa" if exa_available else "",
        "Tavily" if tavily_available else "",
    ]))
    print(f"Date        : {TODAY}")
    print(f"Search      : {engines or 'none — repository-only run'}")

    client = anthropic.Anthropic()

    instructions = load_file(INSTRUCTIONS_FILE)
    current_catalog = load_catalog()
    schema = load_file(SCHEMA_FILE)

    if exa_available and tavily_available:
        search_note = "Both Exa and Tavily are available — use both engines to cross-validate findings."
    elif exa_available:
        search_note = "Exa is available for semantic web research."
    elif tavily_available:
        search_note = "Tavily is available for web research."
    else:
        search_note = "No web search is available. Update the catalog from repository knowledge only."

    system = f"""You are an enterprise AI research catalog maintainer. Today is {TODAY}.

{search_note}

Your task instructions:

---
{instructions}
---

Current catalog (docs/research/research.json):
```json
{current_catalog}
```

Schema (docs/research/research.schema.json):
```json
{schema}
```

When all research is complete, call write_output once with:
- updated_catalog: the full updated catalog JSON validated against the schema
- run_log_markdown: a concise markdown summary of changes and human review items
- sources_json: a structured list of all sources consulted
"""

    tools = build_tools(exa_available, tavily_available)
    messages = [{"role": "user", "content": "Run the weekly AI research catalog update."}]

    final_output = None
    max_iterations = 30
    _interleaved_beta = ["interleaved-thinking-2025-05-14"]
    _use_beta = True  # disabled automatically if the API rejects it

    def call_api(msgs: list) -> anthropic.types.Message:
        kwargs = dict(
            model="claude-opus-4-8",
            max_tokens=16000,
            thinking={"type": "enabled", "budget_tokens": 10000},
            system=system,
            tools=tools,
            messages=msgs,
        )
        for attempt in range(4):
            try:
                return client.messages.create(
                    **kwargs,
                    **({"betas": _interleaved_beta} if _use_beta else {}),
                )
            except anthropic.BadRequestError as exc:
                if _use_beta and "beta" in str(exc).lower():
                    nonlocal _use_beta  # type: ignore[misc]
                    _use_beta = False
                    print("  interleaved-thinking beta rejected — retrying without it")
                    continue
                raise
            except anthropic.RateLimitError:
                wait = 5 * (2 ** attempt)
                print(f"  rate limited — retrying in {wait}s...")
                time.sleep(wait)
        raise RuntimeError("Rate limit retries exhausted")

    for iteration in range(1, max_iterations + 1):
        print(f"\n[iter {iteration}] calling model...")

        # Prune old exchanges to stay within context window.
        # Always keep the first (user task) message + the last 16 messages.
        if len(messages) > 17:
            messages = messages[:1] + messages[-16:]

        response = call_api(messages)

        block_types = [b.type for b in response.content]
        print(f"  stop_reason={response.stop_reason}  blocks={block_types}")

        assistant_content = [serialise_block(b) for b in response.content]
        messages.append({"role": "assistant", "content": assistant_content})

        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if not tool_uses:
            if response.stop_reason == "end_turn":
                print("  Model finished without calling write_output.")
            break

        tool_results = []
        for tu in tool_uses:
            preview = json.dumps(tu.input)[:120]
            print(f"  tool={tu.name}  input={preview}")

            if tu.name == "write_output":
                final_output = tu.input
                result = json.dumps({"status": "acknowledged"})
            else:
                result = run_tool(tu.name, tu.input)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

        if final_output:
            print("  write_output received — research complete.")
            break

        time.sleep(0.5)

    if not final_output:
        print("ERROR: write_output was never called. No files written.", file=sys.stderr)
        sys.exit(1)

    # ── Write outputs ──────────────────────────────────────────────────────────
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    updated = final_output.get("updated_catalog")
    if updated:
        RESEARCH_FILE.write_text(
            json.dumps(updated, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Written : {RESEARCH_FILE.relative_to(REPO_ROOT)}")

    run_log_path = RUNS_DIR / f"{TODAY}.md"
    run_log_path.write_text(
        final_output.get("run_log_markdown", ""),
        encoding="utf-8",
    )
    print(f"Written : {run_log_path.relative_to(REPO_ROOT)}")

    sources_path = SOURCES_DIR / f"{TODAY}.json"
    sources_path.write_text(
        json.dumps(final_output.get("sources_json", {}), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Written : {sources_path.relative_to(REPO_ROOT)}")

    print("\nResearch run complete.")


if __name__ == "__main__":
    main()
