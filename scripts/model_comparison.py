#!/usr/bin/env python3
"""
Model Comparison Benchmark for SierraVault Quality Scoring

Compares local Ollama models vs Claude vs GPT on the same pages.
Measures: accuracy, speed, cost, issue detection, consistency.

Usage:
    python3 model_comparison.py                      # Run with 10 sample pages
    python3 model_comparison.py --pages 20           # Run with 20 pages
    python3 model_comparison.py --flagship-only      # Only test flagship series
    python3 model_comparison.py --output report.json # Save detailed results
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Paths
VAULT_PATH = Path(__file__).parent.parent / "vault" / "Games"
RESULTS_DIR = Path(__file__).parent / "comparison_results"

# Mac Studio Ollama
MAC_STUDIO_HOST = os.environ.get("OLLAMA_STUDIO_HOST", os.environ.get("OLLAMA_STUDIO_TAILSCALE", "http://localhost:11434"))

# Models to compare
OLLAMA_MODELS = [
    {"name": "llama3.2:3b", "host": "local", "tier": "fast", "cost_per_1m": 0},
    {"name": "qwen2.5-coder:32b", "host": MAC_STUDIO_HOST, "tier": "coding", "cost_per_1m": 0},
    {"name": "llama3.3:70b", "host": MAC_STUDIO_HOST, "tier": "quality", "cost_per_1m": 0},
    {"name": "deepseek-r1:70b", "host": MAC_STUDIO_HOST, "tier": "reasoning", "cost_per_1m": 0},
    {"name": "qwen2.5:72b", "host": MAC_STUDIO_HOST, "tier": "general", "cost_per_1m": 0},
]

# Check if qwen3-coder-next is available
QWEN3_CODER = {"name": "qwen3-coder-next", "host": MAC_STUDIO_HOST, "tier": "coding-next", "cost_per_1m": 0}

API_MODELS = [
    # Anthropic models
    {"name": "claude-opus-4-6", "provider": "anthropic", "tier": "flagship", "cost_per_1m_in": 15.0, "cost_per_1m_out": 75.0},
    {"name": "claude-sonnet-4-5", "provider": "anthropic", "tier": "premium", "cost_per_1m_in": 3.0, "cost_per_1m_out": 15.0},
    # OpenAI models
    {"name": "gpt-5.2-codex", "provider": "openai", "tier": "flagship-coding", "cost_per_1m_in": 10.0, "cost_per_1m_out": 30.0},
    {"name": "gpt-4o", "provider": "openai", "tier": "premium", "cost_per_1m_in": 2.5, "cost_per_1m_out": 10.0},
    {"name": "gpt-4o-mini", "provider": "openai", "tier": "budget", "cost_per_1m_in": 0.15, "cost_per_1m_out": 0.60},
]

# Flagship series for harder tests
FLAGSHIP_SERIES = ["Kings Quest", "Space Quest", "Quest for Glory", "Leisure Suit Larry", 
                   "Police Quest", "Gabriel Knight", "Phantasmagoria", "Laura Bow"]

# Scoring prompt template
SCORING_PROMPT = """You are a quality scorer for video game documentation pages. 
Analyze this page and provide:
1. A score from 0-100 based on quality, accuracy, completeness
2. A list of specific issues found
3. A brief assessment

Scoring criteria:
- Citation count (15+ is good, 20+ is excellent)
- Factual accuracy (no hallucinated claims)
- Section completeness (Overview, Reception, Legacy, References required)
- Writing quality (no promotional language)
- Cross-references to related games in series
- Proper formatting and structure

PAGE CONTENT:
{content}

Respond in JSON format:
{{
    "score": <number 0-100>,
    "issues": ["issue1", "issue2", ...],
    "assessment": "brief assessment",
    "citation_count": <number>,
    "has_required_sections": true/false,
    "promotional_language_detected": true/false
}}"""


def get_sample_pages(count: int = 10, flagship_only: bool = False) -> List[Path]:
    """Get random sample of game pages for testing."""
    all_pages = []
    
    for series_dir in VAULT_PATH.iterdir():
        if not series_dir.is_dir():
            continue
        if flagship_only and not any(fs.lower() in series_dir.name.lower() for fs in FLAGSHIP_SERIES):
            continue
        for page in series_dir.glob("*.md"):
            if page.name.startswith("_"):
                continue
            all_pages.append(page)
    
    # Mix of quality levels - some known good, some known bad
    if len(all_pages) > count:
        return random.sample(all_pages, count)
    return all_pages


def run_ollama_model(prompt: str, model: str, host: str, timeout: int = 300) -> Dict[str, Any]:
    """Run prompt through Ollama model and measure performance."""
    start_time = time.time()
    
    try:
        if host == "local":
            # Local ollama command
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            response = result.stdout.strip() if result.returncode == 0 else None
        else:
            # Remote via HTTP API
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 2000, "temperature": 0.3}
            })
            result = subprocess.run(
                ['curl', '-s', '--max-time', str(timeout), '-X', 'POST',
                 '-H', 'Content-Type: application/json',
                 '-d', payload, f"{host}/api/generate"],
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                response = data.get('response', '').strip()
            else:
                response = None
        
        elapsed = time.time() - start_time
        
        # Try to parse JSON from response
        score_data = None
        if response:
            try:
                # Find JSON in response
                json_match = response[response.find('{'):response.rfind('}')+1]
                if json_match:
                    score_data = json.loads(json_match)
            except:
                pass
        
        return {
            "success": response is not None,
            "response": response,
            "parsed": score_data,
            "elapsed_seconds": elapsed,
            "tokens_estimate": len(response.split()) * 1.3 if response else 0
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout", "elapsed_seconds": timeout}
    except Exception as e:
        return {"success": False, "error": str(e), "elapsed_seconds": time.time() - start_time}


def run_claude_model(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> Dict[str, Any]:
    """Run prompt through Claude API."""
    start_time = time.time()
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"success": False, "error": "No ANTHROPIC_API_KEY"}
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        elapsed = time.time() - start_time
        content = response.content[0].text
        
        # Parse JSON
        score_data = None
        try:
            json_match = content[content.find('{'):content.rfind('}')+1]
            if json_match:
                score_data = json.loads(json_match)
        except:
            pass
        
        return {
            "success": True,
            "response": content,
            "parsed": score_data,
            "elapsed_seconds": elapsed,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "elapsed_seconds": time.time() - start_time}


def run_openai_model(prompt: str, model: str = "gpt-4o") -> Dict[str, Any]:
    """Run prompt through OpenAI API."""
    start_time = time.time()
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"success": False, "error": "No OPENAI_API_KEY"}
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        
        elapsed = time.time() - start_time
        content = response.choices[0].message.content
        
        # Parse JSON
        score_data = None
        try:
            json_match = content[content.find('{'):content.rfind('}')+1]
            if json_match:
                score_data = json.loads(json_match)
        except:
            pass
        
        return {
            "success": True,
            "response": content,
            "parsed": score_data,
            "elapsed_seconds": elapsed,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "elapsed_seconds": time.time() - start_time}


def check_ollama_models_available() -> List[Dict]:
    """Check which Ollama models are actually available."""
    available = []
    
    # Check local
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            local_models = result.stdout
            for model in OLLAMA_MODELS:
                if model["host"] == "local" and model["name"].split(":")[0] in local_models:
                    available.append(model)
    except:
        pass
    
    # Check Mac Studio
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '10', f"{MAC_STUDIO_HOST}/api/tags"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            studio_data = json.loads(result.stdout)
            studio_models = [m["name"] for m in studio_data.get("models", [])]
            
            for model in OLLAMA_MODELS:
                if model["host"] == MAC_STUDIO_HOST:
                    if any(model["name"] in sm for sm in studio_models):
                        available.append(model)
            
            # Check for qwen3-coder-next
            if any("qwen3-coder-next" in sm for sm in studio_models):
                available.append(QWEN3_CODER)
    except:
        pass
    
    return available


def run_comparison(pages: List[Path], include_api: bool = True, verbose: bool = True) -> Dict:
    """Run full comparison across all models."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "pages_tested": len(pages),
        "models": {},
        "page_results": [],
        "summary": {}
    }
    
    # Check available models
    ollama_models = check_ollama_models_available()
    if verbose:
        print(f"Found {len(ollama_models)} Ollama models available")
        for m in ollama_models:
            print(f"  - {m['name']} ({m['tier']})")
    
    all_models = ollama_models.copy()
    if include_api:
        all_models.extend(API_MODELS)
    
    # Initialize model results
    for model in all_models:
        model_key = model["name"]
        results["models"][model_key] = {
            "tier": model.get("tier", "unknown"),
            "provider": model.get("provider", "ollama"),
            "total_time": 0,
            "total_tokens": 0,
            "success_count": 0,
            "fail_count": 0,
            "scores": [],
            "cost": 0
        }
    
    # Test each page
    for i, page_path in enumerate(pages):
        if verbose:
            print(f"\n[{i+1}/{len(pages)}] Testing: {page_path.name}")
        
        # Read page content
        content = page_path.read_text()
        if len(content) > 15000:
            content = content[:15000] + "\n...[truncated]..."
        
        prompt = SCORING_PROMPT.format(content=content)
        
        page_result = {
            "page": str(page_path.relative_to(VAULT_PATH)),
            "results": {}
        }
        
        # Run through each model
        for model in all_models:
            model_key = model["name"]
            if verbose:
                print(f"  Running {model_key}...", end=" ", flush=True)
            
            # Run appropriate function based on provider
            if model.get("provider") == "anthropic":
                result = run_claude_model(prompt, model["name"])
            elif model.get("provider") == "openai":
                result = run_openai_model(prompt, model["name"])
            else:
                result = run_ollama_model(prompt, model["name"], model["host"])
            
            if verbose:
                if result["success"]:
                    score = result.get("parsed", {}).get("score", "?")
                    print(f"✓ Score: {score} ({result['elapsed_seconds']:.1f}s)")
                else:
                    print(f"✗ {result.get('error', 'failed')}")
            
            # Record results
            page_result["results"][model_key] = result
            
            model_stats = results["models"][model_key]
            model_stats["total_time"] += result.get("elapsed_seconds", 0)
            
            if result["success"]:
                model_stats["success_count"] += 1
                if result.get("parsed") and "score" in result["parsed"]:
                    model_stats["scores"].append(result["parsed"]["score"])
                
                # Calculate cost for API models
                if model.get("provider") in ["anthropic", "openai"]:
                    in_tokens = result.get("input_tokens", 0)
                    out_tokens = result.get("output_tokens", 0)
                    cost = (in_tokens * model.get("cost_per_1m_in", 0) / 1_000_000 +
                            out_tokens * model.get("cost_per_1m_out", 0) / 1_000_000)
                    model_stats["cost"] += cost
                    model_stats["total_tokens"] += in_tokens + out_tokens
            else:
                model_stats["fail_count"] += 1
        
        results["page_results"].append(page_result)
    
    # Calculate summary statistics
    for model_key, stats in results["models"].items():
        total = stats["success_count"] + stats["fail_count"]
        stats["success_rate"] = stats["success_count"] / total if total > 0 else 0
        stats["avg_time"] = stats["total_time"] / total if total > 0 else 0
        stats["avg_score"] = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else None
        stats["score_std"] = (
            (sum((s - stats["avg_score"])**2 for s in stats["scores"]) / len(stats["scores"]))**0.5
            if stats["scores"] and len(stats["scores"]) > 1 else None
        )
    
    # Cross-model score correlation
    results["summary"]["model_comparison"] = []
    model_keys = list(results["models"].keys())
    for i, m1 in enumerate(model_keys):
        for m2 in model_keys[i+1:]:
            scores1 = []
            scores2 = []
            for page in results["page_results"]:
                s1 = page["results"].get(m1, {}).get("parsed", {}).get("score")
                s2 = page["results"].get(m2, {}).get("parsed", {}).get("score")
                if s1 is not None and s2 is not None:
                    scores1.append(s1)
                    scores2.append(s2)
            
            if scores1:
                avg_diff = sum(abs(a-b) for a,b in zip(scores1, scores2)) / len(scores1)
                correlation = {
                    "models": [m1, m2],
                    "sample_size": len(scores1),
                    "avg_score_diff": avg_diff,
                    "max_diff": max(abs(a-b) for a,b in zip(scores1, scores2))
                }
                results["summary"]["model_comparison"].append(correlation)
    
    return results


def print_summary(results: Dict):
    """Print human-readable summary of results."""
    print("\n" + "="*70)
    print("MODEL COMPARISON SUMMARY")
    print("="*70)
    print(f"Pages tested: {results['pages_tested']}")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\n" + "-"*70)
    print(f"{'Model':<30} {'Tier':<12} {'Avg Score':<10} {'Avg Time':<10} {'Cost':<10} {'Success'}")
    print("-"*70)
    
    # Sort by tier then name
    sorted_models = sorted(results["models"].items(), 
                          key=lambda x: (x[1]["tier"], x[0]))
    
    for model_key, stats in sorted_models:
        avg_score = f"{stats['avg_score']:.1f}" if stats['avg_score'] else "N/A"
        avg_time = f"{stats['avg_time']:.1f}s"
        cost = f"${stats['cost']:.4f}" if stats['cost'] > 0 else "FREE"
        success = f"{stats['success_rate']*100:.0f}%"
        
        print(f"{model_key:<30} {stats['tier']:<12} {avg_score:<10} {avg_time:<10} {cost:<10} {success}")
    
    print("\n" + "-"*70)
    print("SCORE AGREEMENT (lower diff = more agreement)")
    print("-"*70)
    
    for comp in sorted(results["summary"]["model_comparison"], key=lambda x: x["avg_score_diff"]):
        print(f"  {comp['models'][0]} vs {comp['models'][1]}: "
              f"avg diff = {comp['avg_score_diff']:.1f}, max diff = {comp['max_diff']}")
    
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description="Compare LLM models for SierraVault quality scoring")
    parser.add_argument("--pages", type=int, default=10, help="Number of pages to test")
    parser.add_argument("--flagship-only", action="store_true", help="Only test flagship series")
    parser.add_argument("--no-api", action="store_true", help="Skip API models (Claude/GPT)")
    parser.add_argument("--output", type=str, help="Save detailed results to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()
    
    # Get sample pages
    pages = get_sample_pages(args.pages, args.flagship_only)
    print(f"Selected {len(pages)} pages for testing")
    
    # Run comparison
    results = run_comparison(pages, include_api=not args.no_api, verbose=not args.quiet)
    
    # Print summary
    print_summary(results)
    
    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove raw responses to save space
        for page in results["page_results"]:
            for model_key in page["results"]:
                if "response" in page["results"][model_key]:
                    del page["results"][model_key]["response"]
        
        output_path.write_text(json.dumps(results, indent=2))
        print(f"\nDetailed results saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    main()
