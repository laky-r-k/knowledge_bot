"""Evaluation Benchmark for Knowledge Graph RAG vs Baseline LLM.

Metrics:
1. Factual Accuracy (1-5): Correctness against ground-truth faculty facts
2. Faithfulness / Groundedness (1-5): Freedom from hallucinations
3. Answer Relevance (1-5): How directly the query is answered
4. Retrieval Hit Rate (%): Whether relevant KG triples were found
5. End-to-End Latency (s): Response turnaround time
"""

import json
import os
import time
import google.generativeai as genai
from rich.console import Console
from rich.table import Table

from chat_bot.gemini_chatbot import GeminiChatBot, safe_generate_content
from kg_builder.gemini_kg_builder import GeminiKGBuilder
from chat_bot.CONFIG.config import GEMINI_API_KEY

console = Console()

# Configure LLM Judge
genai.configure(api_key=GEMINI_API_KEY)
judge_model = genai.GenerativeModel("models/gemini-3.5-flash-lite")

# Benchmark Test Suite based on scraped BMSCE faculty facts
BENCHMARK_TESTS = [
    {
        "id": 1,
        "query": "Who is the Head of Department of Information Science and Engineering at BMSCE?",
        "ground_truth": "Dr. M Dakshayini is the Professor and Head of Department (HOD) of Information Science and Engineering.",
        "expected_entity": "Dr. M Dakshayini"
    },
    {
        "id": 2,
        "query": "What is Dr. Gowrishankar's email address and current designation?",
        "ground_truth": "Dr. Gowrishankar's email is gowrishankar.cse@bmsce.ac.in and his designation is Professor.",
        "expected_entity": "Dr. Gowrishankar"
    },
    {
        "id": 3,
        "query": "Who is the HOD of the Machine Learning department at BMSCE?",
        "ground_truth": "Dr. Sandeep Varma N is the Associate Professor and HOD of the Machine Learning department.",
        "expected_entity": "Dr. Sandeep Varma N"
    },
    {
        "id": 4,
        "query": "What is Dr. Monika Puttaramaiah's designation and department?",
        "ground_truth": "Dr. Monika Puttaramaiah is an Associate Professor in the Machine Learning / AI&ML department at BMSCE.",
        "expected_entity": "Dr. Monika Puttaramaiah"
    },
    {
        "id": 5,
        "query": "Where did Dr. Gowrishankar receive his PhD from and in which year?",
        "ground_truth": "Dr. Gowrishankar received his PhD from Visvesvaraya Technological University (VTU) in 2009.",
        "expected_entity": "Dr. Gowrishankar"
    },
    {
        "id": 6,
        "query": "What are Dr. M Dakshayini's primary research interests?",
        "ground_truth": "Dr. M Dakshayini's research interests include Computer Networks, Algorithms, Cloud computing, Ad-hoc Networks, IoT, Data Analytics, and Blockchain Technology.",
        "expected_entity": "Dr. M Dakshayini"
    }
]


def judge_response(query: str, ground_truth: str, answer: str) -> dict:
    """Uses LLM-as-a-Judge to grade accuracy, faithfulness, and relevance (1-5)."""
    prompt = f"""You are an expert NLP evaluation judge. Evaluate the following chatbot answer against the verified Ground Truth.

Query: {query}
Ground Truth: {ground_truth}
Candidate Answer: {answer}

Grade each metric on a scale from 1 to 5:
- accuracy (1-5): Does the answer state the correct facts matching the Ground Truth? Give 1 if facts are wrong or hallucinated. Give 5 if fully correct.
- faithfulness (1-5): Is the answer grounded and free from invented/hallucinated details?
- relevance (1-5): Does the answer directly address the user's question?

Return ONLY a valid JSON object with integer scores:
{{"accuracy": <1-5>, "faithfulness": <1-5>, "relevance": <1-5>, "reason": "<one sentence explanation>"}}
"""
    try:
        res = safe_generate_content(judge_model, prompt)
        text = res.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
    except Exception as e:
        return {"accuracy": 1, "faithfulness": 1, "relevance": 1, "reason": f"Evaluation error: {e}"}


def run_evaluation():
    console.print("\n[bold cyan]🚀 Starting Knowledge Bot Evaluation Benchmark[/bold cyan]\n")

    # 1. Load Knowledge Graph from cache
    kg = GeminiKGBuilder()
    triples_path = "data/kg_cache/triples.json"
    graph_path = "data/kg_cache/graph.graphml"

    if not kg.load(triples_path, graph_path):
        console.print("[red]❌ KG cache not found. Please run visualize_kg.py first to build the graph.[/red]")
        return

    kg.build_graph(kg.triples)
    console.print(f"[green]✔ Loaded Knowledge Graph: {len(kg.triples)} triples, {kg.graph.number_of_nodes()} nodes[/green]\n")

    # 2. Initialize bots
    bot_with_kg = GeminiChatBot(kg_builder=kg)
    bot_baseline = GeminiChatBot(kg_builder=None)

    results = []
    kg_retrieval_hits = 0

    for item in BENCHMARK_TESTS:
        qid = item["id"]
        q = item["query"]
        gt = item["ground_truth"]
        expected_entity = item["expected_entity"]

        console.print(f"[yellow]Test {qid}/{len(BENCHMARK_TESTS)}:[/yellow] {q}")

        # Test Baseline (Gemini without KG)
        t0 = time.time()
        ans_baseline = bot_baseline.ask(q, use_kg=False)
        base_latency = round(time.time() - t0, 2)
        score_base = judge_response(q, gt, ans_baseline)

        # Test KG-Augmented Bot
        t0 = time.time()
        # Check retrieval hit
        matching_triples = kg.search(expected_entity)
        has_hit = len(matching_triples) > 0
        if has_hit:
            kg_retrieval_hits += 1

        ans_kg = bot_with_kg.ask(q, use_kg=True)
        kg_latency = round(time.time() - t0, 2)
        score_kg = judge_response(q, gt, ans_kg)

        results.append({
            "id": qid,
            "query": q,
            "ground_truth": gt,
            "baseline": {
                "answer": ans_baseline,
                "scores": score_base,
                "latency": base_latency
            },
            "with_kg": {
                "answer": ans_kg,
                "scores": score_kg,
                "retrieval_hit": has_hit,
                "latency": kg_latency
            }
        })

        console.print(f"  [dim]Baseline Acc: {score_base.get('accuracy', 1)}/5 | KG Acc: {score_kg.get('accuracy', 1)}/5[/dim]")
        time.sleep(4)

    # 3. Calculate Averages
    avg_base_acc = sum(r["baseline"]["scores"]["accuracy"] for r in results) / len(results)
    avg_base_faith = sum(r["baseline"]["scores"]["faithfulness"] for r in results) / len(results)
    avg_base_rel = sum(r["baseline"]["scores"]["relevance"] for r in results) / len(results)
    avg_base_lat = sum(r["baseline"]["latency"] for r in results) / len(results)

    avg_kg_acc = sum(r["with_kg"]["scores"]["accuracy"] for r in results) / len(results)
    avg_kg_faith = sum(r["with_kg"]["scores"]["faithfulness"] for r in results) / len(results)
    avg_kg_rel = sum(r["with_kg"]["scores"]["relevance"] for r in results) / len(results)
    avg_kg_lat = sum(r["with_kg"]["latency"] for r in results) / len(results)

    hit_rate = (kg_retrieval_hits / len(results)) * 100

    # 4. Display Results Table
    table = Table(title="📊 Benchmark Comparison: Baseline vs KG-Augmented Bot", show_header=True, header_style="bold magenta")
    table.add_column("Query ID", style="dim", width=8)
    table.add_column("Test Query", width=40)
    table.add_column("Baseline Acc", justify="center")
    table.add_column("KG Acc", justify="center")
    table.add_column("KG Faithfulness", justify="center")
    table.add_column("KG Hit?", justify="center")

    for r in results:
        table.add_row(
            str(r["id"]),
            r["query"],
            f"{r['baseline']['scores']['accuracy']}/5",
            f"[bold green]{r['with_kg']['scores']['accuracy']}/5[/bold green]",
            f"{r['with_kg']['scores']['faithfulness']}/5",
            "✔ Yes" if r["with_kg"]["retrieval_hit"] else "❌ No"
        )

    console.print("\n")
    console.print(table)

    # 5. Summary Card
    console.print("\n[bold cyan]📈 Overall Metric Summary:[/bold cyan]")
    console.print(f"• [bold]Factual Accuracy:[/bold]    Baseline: {avg_base_acc:.2f}/5.0  →  [bold green]With KG: {avg_kg_acc:.2f}/5.0[/bold green] (+{((avg_kg_acc - avg_base_acc)/max(avg_base_acc, 0.01))*100:.1f}%)")
    console.print(f"• [bold]Faithfulness:[/bold]        Baseline: {avg_base_faith:.2f}/5.0  →  [bold green]With KG: {avg_kg_faith:.2f}/5.0[/bold green]")
    console.print(f"• [bold]Answer Relevance:[/bold]    Baseline: {avg_base_rel:.2f}/5.0  →  [bold green]With KG: {avg_kg_rel:.2f}/5.0[/bold green]")
    console.print(f"• [bold]KG Retrieval Hit Rate:[/bold] [bold green]{hit_rate:.1f}%[/bold green]")
    console.print(f"• [bold]Average Latency:[/bold]      Baseline: {avg_base_lat:.2f}s  |  With KG: {avg_kg_lat:.2f}s\n")

    # 6. Save JSON & Markdown Reports
    os.makedirs("data", exist_ok=True)
    with open("data/evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Markdown Report for Presentation Slides
    md_report = f"""# 📊 Knowledge Graph Help Bot - Evaluation Report

## 1. Executive Summary
- **Retrieval Hit Rate**: {hit_rate:.1f}%
- **Factual Accuracy Uplift**: {avg_base_acc:.2f}/5.0 → **{avg_kg_acc:.2f}/5.0** (+{((avg_kg_acc - avg_base_acc)/max(avg_base_acc, 0.01))*100:.1f}%)
- **Faithfulness (Anti-Hallucination)**: {avg_base_faith:.2f}/5.0 → **{avg_kg_faith:.2f}/5.0**
- **Average Latency**: {avg_kg_lat:.2f}s

## 2. Head-to-Head Comparison Table

| ID | Test Query | Baseline (No KG) | With KG (Graph-RAG) | KG Grounded? |
|---|---|:---:|:---:|:---:|
"""
    for r in results:
        md_report += f"| {r['id']} | {r['query']} | {r['baseline']['scores']['accuracy']}/5 | **{r['with_kg']['scores']['accuracy']}/5** | {'✔ Yes' if r['with_kg']['retrieval_hit'] else '❌ No'} |\n"

    md_report += f"""
## 3. Metric Definitions
1. **Factual Accuracy**: Degree to which response matches institutional ground truth facts.
2. **Faithfulness**: Absence of fabricated information / hallucinations.
3. **KG Retrieval Hit Rate**: Percentage of queries where graph successfully retrieved required entity triples.
"""

    with open("data/evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(md_report)

    console.print("[green]💾 Saved evaluation report to data/evaluation_report.json and data/evaluation_report.md[/green]")


if __name__ == "__main__":
    run_evaluation()
