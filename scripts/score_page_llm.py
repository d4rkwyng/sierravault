#!/usr/bin/env python3
"""
LLM-Based Page Quality Scorer

Uses local Ollama models to score SierraVault game pages on:
- Citation quality and distribution
- Content depth and accuracy
- Structural completeness
- Accuracy of facts and links

Model Priority (cascading fallback):
1. qwen3.5:35b-a3b-q4_K_M (Mac Mini local, 10 t/s) — PRIMARY
2. qwen3.5:35b (Mac Mini local, 11 t/s) — FALLBACK 1
3. qwen2.5-coder:32b (Mac Mini local, 9 t/s) — FALLBACK 2
4. qwen2.5-coder:7b (Mac Mini local, 40 t/s) — FALLBACK 3
5. llama3.2:3b (Mac Mini local, 71 t/s) — FALLBACK 4

Usage:
    python3 score_page_llm.py vault/Games/SomeGame/Year-Title.md
    python3 score_page_llm.py vault/Games/SomeGame/Year-Title.md --local-model qwen3.5:35b
    python3 score_page_llm.py vault/Games/SomeGame/Year-Title.md --model cloud  # Use Claude API (requires ANTHROPIC_API_KEY)
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Tuple, Optional
import os
import urllib.request
import urllib.error

# MLX endpoints (Mac Studio 122B for heavy tasks @ 45-50 t/s, Mac Mini 35B fallback @ 50-60 t/s)
MLXSTUDIO_ENDPOINT = "http://100.90.195.80:8080"
MLXMINI_ENDPOINT = "http://localhost:8080"

# Model priority chain (cascade on failure)
LOCAL_MODELS = [
    "nightmedia/Qwen3.5-122B-A10B-Text-mxfp4-mlx",  # Studio 45-50 t/s (PRIMARY, heavy tasks)
    "nightmedia/Qwen3.5-35B-A3B-Text-qx64-hi-mlx",  # Mini 50-60 t/s (FALLBACK)
]


def get_available_local_models() -> list:
    """Fetch available models from MLX servers."""
    try:
        # Try Mac Studio first (100 t/s)
        req = urllib.request.Request(f"{MLXSTUDIO_ENDPOINT}/v1/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            available = [m["id"] for m in data.get("data", [])]
            if available:
                return available
    except Exception as e:
        print(f"⚠️  Mac Studio unavailable, trying Mac Mini: {e}", file=sys.stderr)
    
    # Fallback to Mac Mini
    try:
        req = urllib.request.Request(f"{MLXMINI_ENDPOINT}/v1/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            available = [m["id"] for m in data.get("data", [])]
            return available
    except Exception as e:
        print(f"⚠️  Could not fetch MLX models: {e}", file=sys.stderr)
    return []


def get_working_model() -> Optional[str]:
    """Find first available model from priority chain."""
    available = get_available_local_models()
    for model in LOCAL_MODELS:
        if model in available:
            return model
    return None


def score_with_local_model(content: str, model: str) -> Tuple[int, str, str]:
    """
    Score page using local MLX model via OpenAI-compatible API.
    
    Returns: (score, reasoning, model_used)
    """
    prompt = f"""Evaluate this Sierra game page for quality. Rate on a scale of 0-100 based on:

1. **Citations** (20 points): Count and quality of references. Target 15+, prefer 20+.
2. **Content Depth** (25 points): Does it cover story, gameplay, design, legacy? Is it substantive?
3. **Accuracy** (20 points): Are facts verifiable? Are links/dates correct?
4. **Structure** (20 points): Clear sections, proper formatting, logical flow?
5. **Completeness** (15 points): All required sections present? No obvious gaps?

PAGE CONTENT:
---
{content[:4000]}
---

Respond with ONLY a JSON object:
{{"score": <0-100>, "reasoning": "<2-3 sentence explanation>", "issues": ["<issue1>", "<issue2>"]}}
"""

    # Try Mac Mini (Mac Studio has response issues)
    endpoints = [
        (MLXMINI_ENDPOINT, "Mac Mini (52.7 t/s)"),
    ]
    
    for endpoint, name in endpoints:
        try:
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
            }).encode()
            
            req = urllib.request.Request(
                f"{endpoint}/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
                response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                
                # Parse JSON from response
                try:
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                        score = result.get("score", 0)
                        reasoning = result.get("reasoning", "No reasoning provided")
                        print(f"✅ Scored with {name}", file=sys.stderr)
                        return int(score), reasoning, model
                except json.JSONDecodeError:
                    print(f"⚠️  Could not parse response: {response_text[:200]}", file=sys.stderr)
                    continue
        except Exception as e:
            print(f"⚠️  {name} failed: {e}", file=sys.stderr)
            continue
    
    return 0, "Failed to score (all endpoints unavailable)", model


def score_with_claude_api(content: str) -> Tuple[int, str, str]:
    """Score using Claude API if available (requires ANTHROPIC_API_KEY)."""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        message = client.messages.create(
            model="claude-opus-4-5-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Evaluate this Sierra game page for quality. Rate on 0-100.

CONTENT:
{content[:3000]}

Respond with JSON: {{"score": <0-100>, "reasoning": "<brief>"}}""",
                }
            ],
        )
        
        response_text = message.content[0].text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return int(result.get("score", 0)), result.get("reasoning", ""), "claude-opus"
    except ImportError:
        print("❌ Anthropic library not installed", file=sys.stderr)
    except Exception as e:
        print(f"❌ Claude API error: {e}", file=sys.stderr)
    
    return 0, "Claude API failed", "claude-opus"


def score_page(filepath: str, model_override: Optional[str] = None) -> None:
    """Score a single page."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    
    content = path.read_text()
    
    # Determine which model/API to use
    if model_override == "cloud":
        print("📱 Using Claude API...")
        score, reasoning, model = score_with_claude_api(content)
    elif model_override and model_override in LOCAL_MODELS:
        # Try specific model
        print(f"🔧 Using {model_override}...")
        score, reasoning, model = score_with_local_model(content, model_override)
    else:
        # Find best available local model
        working_model = get_working_model()
        if not working_model:
            print("❌ No local models available. Install Ollama or use --model cloud")
            sys.exit(1)
        
        print(f"🚀 Using {working_model}...")
        score, reasoning, model = score_with_local_model(content, working_model)
    
    # Output result
    print(f"\n📄 {path.name}")
    print(f"Score: {score}/100")
    print(f"Model: {model}")
    print(f"Reasoning: {reasoning}\n")
    
    if score < 90:
        print("⚠️  Below target (90+). Consider:\n  - Adding more citations\n  - Expanding weak sections\n  - Verifying links")


def main():
    parser = argparse.ArgumentParser(
        description="Score SierraVault pages using local LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 score_page_llm.py vault/Games/Kings_Quest/1984.md
  python3 score_page_llm.py vault/Games/Kings_Quest/1984.md --local-model qwen2.5-coder:7b
  python3 score_page_llm.py vault/Games/Kings_Quest/1984.md --model cloud
        """,
    )
    parser.add_argument("files", nargs="+", help="Markdown files to score")
    parser.add_argument(
        "--local-model",
        help=f"Force specific local model (choices: {', '.join(LOCAL_MODELS)})",
    )
    parser.add_argument(
        "--model",
        choices=["local", "cloud"],
        default="local",
        help="Use local Ollama (default) or Claude API",
    )
    
    args = parser.parse_args()
    
    model_override = None
    if args.model == "cloud":
        model_override = "cloud"
    elif args.local_model:
        model_override = args.local_model
    
    for filepath in args.files:
        score_page(filepath, model_override)


if __name__ == "__main__":
    main()
