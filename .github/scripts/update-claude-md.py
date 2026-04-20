#!/usr/bin/env python3
"""Rewrite CLAUDE.md so it reflects the current state of the repo.

Called by .github/workflows/update-claude-md.yml on every push to main.
Reads the current CLAUDE.md plus the project source files, asks Claude
to produce an updated version, and writes the result back to disk. The
workflow then commits the change (if any) with [skip-claudemd] in the
message so it does not loop.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error


MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 8000
# Files to feed Claude as ground truth. Keep this short — the prompt
# has to fit in context and bigger files are expensive.
SOURCE_FILES = ["index.html", "site.html"]


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def build_prompt(current_md: str, sources: dict[str, str]) -> str:
    source_blocks = "\n\n".join(
        f"=== {path} ===\n{content}" for path, content in sources.items() if content
    )
    return f"""You are updating a project's CLAUDE.md (the memory file that future Claude \
sessions read to understand this codebase).

Review the current CLAUDE.md and the current source files. Produce an updated \
CLAUDE.md that accurately reflects the current state of the project.

Rules:
- Preserve the existing tone, voice, and section structure.
- Preserve the "Non-obvious decisions" callouts verbatim unless they are now \
factually wrong (they encode design intent that should not be lost).
- Only change what no longer matches reality. If a section is still accurate, \
leave it alone.
- Do not invent features. If you are not sure whether something changed, do not \
mention it.
- Do not add a changelog, a diff summary, or meta-commentary about what you \
changed.
- Return ONLY the raw Markdown contents of the new CLAUDE.md. No code fences, \
no preamble, no trailing commentary.

=== CURRENT CLAUDE.md ===
{current_md}

{source_blocks}
"""


def call_anthropic(prompt: str, api_key: str) -> str:
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"Anthropic API error {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error calling Anthropic API: {e}", file=sys.stderr)
        sys.exit(1)

    result = json.loads(body)
    blocks = result.get("content") or []
    texts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
    combined = "".join(texts).strip()
    if not combined:
        print(f"Empty response from Anthropic API: {body}", file=sys.stderr)
        sys.exit(1)
    return combined


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ANTHROPIC_API_KEY is not set. Add it as a repo secret at "
            "Settings → Secrets and variables → Actions.",
            file=sys.stderr,
        )
        sys.exit(1)

    current_md = read("CLAUDE.md")
    sources = {path: read(path) for path in SOURCE_FILES}

    prompt = build_prompt(current_md, sources)
    new_md = call_anthropic(prompt, api_key)

    # Guardrail: refuse to write a suspiciously small file. If the API
    # returns something tiny it almost certainly did not produce a full
    # CLAUDE.md — better to fail loud than to truncate the real one.
    if len(new_md) < max(400, len(current_md) // 4):
        print(
            f"New CLAUDE.md is unexpectedly short ({len(new_md)} chars vs "
            f"{len(current_md)} current). Refusing to overwrite.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Ensure the file ends with a single newline.
    if not new_md.endswith("\n"):
        new_md += "\n"

    with open("CLAUDE.md", "w", encoding="utf-8") as f:
        f.write(new_md)

    print(f"CLAUDE.md rewritten ({len(new_md)} chars).")


if __name__ == "__main__":
    main()
