"""Gemini-based Knowledge Graph Builder.

Uses Google Gemini LLM to extract high-quality (subject, predicate, object)
triples from faculty profile text, producing meaningful relationships like:
  (Dr. Dakshayini, designation, Professor & HOD)
  (Dr. Dakshayini, researches, Cloud Computing)
  (Dr. Dakshayini, guided, 5 PhD candidates)
"""

import json
import os
import google.generativeai as genai
import networkx as nx
from typing import List, Tuple
from kg_builder.base import BaseKGBuilder
from chat_bot.CONFIG.config import GEMINI_API_KEY


class GeminiKGBuilder(BaseKGBuilder):
    def __init__(self, model_name: str = "models/gemini-2.5-flash"):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.graph = nx.DiGraph()
        self.triples = []

    def extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Use Gemini to extract structured triples from text."""
        prompt = f"""You are a knowledge graph extraction engine. 
Extract factual (subject, predicate, object) triples from the following faculty profile text.

Rules:
1. Use the faculty member's FULL NAME as the subject (e.g., "Dr. M Dakshayini"), never "she", "he", or "they".
2. Keep predicates short and clear (e.g., "designation", "email", "researches", "qualified_with", "affiliated_to", "published", "guided", "teaches", "awarded_phd_from", "experience_years").
3. Keep objects concise but informative.
4. Extract ALL meaningful facts: name, designation, department, college, email, qualifications, research interests, experience, publications count, awards, patents, PhD guidance, education history.
5. For education, create separate triples for each degree.
6. For research interests, create a separate triple for each interest area.

Return ONLY a valid JSON array of arrays, no explanation. Example:
[
  ["Dr. M Dakshayini", "designation", "Professor & HOD"],
  ["Dr. M Dakshayini", "department", "Information Science and Engineering"],
  ["Dr. M Dakshayini", "researches", "Cloud Computing"]
]

Faculty Profile Text:
{text}

JSON Output:"""

        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()

            # Clean markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]  # remove first line
                raw = raw.rsplit("```", 1)[0]  # remove last fence
                raw = raw.strip()

            parsed = json.loads(raw)
            triples = [(str(s), str(p), str(o)) for s, p, o in parsed]
            return triples

        except json.JSONDecodeError as e:
            print(f"  ⚠ JSON parse error: {e}")
            print(f"  Raw response: {raw[:300]}")
            return []
        except Exception as e:
            print(f"  ⚠ Gemini extraction error: {e}")
            return []

    def extract_triples_from_files(self, file_paths: List[str]) -> List[Tuple[str, str, str]]:
        """Process each faculty file individually and merge all triples."""
        all_triples = []

        for filepath in file_paths:
            filename = os.path.basename(filepath)
            print(f"\n🔍 Processing: {filename}")

            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            triples = self.extract_triples(text)
            all_triples.extend(triples)
            print(f"   ✔ Extracted {len(triples)} triples")

            # Print a few sample triples
            for s, p, o in triples[:3]:
                print(f"     ({s}) --[{p}]--> ({o})")

        self.triples = all_triples
        return all_triples

    def build_graph(self, triples: List[Tuple[str, str, str]]) -> nx.DiGraph:
        """Build a single connected knowledge graph from all triples."""
        for s, p, o in triples:
            self.graph.add_node(s, label=s)
            self.graph.add_node(o, label=o)
            self.graph.add_edge(s, o, label=p)

        return self.graph

    def search(self, query: str) -> List[Tuple[str, str, str]]:
        """Search triples by keyword matching on subject, predicate, or object."""
        keyword = query.lower()
        matches = [
            t for t in self.triples
            if keyword in t[0].lower() or keyword in t[1].lower() or keyword in t[2].lower()
        ]
        return matches

    def to_prompt_text(self, triples: List[Tuple[str, str, str]]) -> str:
        """Convert triples into readable text for LLM prompts."""
        lines = [f"{i+1}. {s} → {p} → {o}" for i, (s, p, o) in enumerate(triples)]
        return "Knowledge Graph Facts:\n" + "\n".join(lines)

    def save(self, triples_path: str, graph_path: str):
        """Persist triples as JSON and graph as GraphML."""
        os.makedirs(os.path.dirname(triples_path), exist_ok=True)

        # Save triples
        with open(triples_path, "w", encoding="utf-8") as f:
            json.dump(self.triples, f, indent=2, ensure_ascii=False)
        print(f"💾 Triples saved to {triples_path}")

        # Save graph
        nx.write_graphml(self.graph, graph_path)
        print(f"💾 Graph saved to {graph_path}")

    def load(self, triples_path: str, graph_path: str) -> bool:
        """Load triples and graph from disk. Returns True if successful."""
        if not os.path.exists(triples_path) or not os.path.exists(graph_path):
            return False

        try:
            with open(triples_path, "r", encoding="utf-8") as f:
                self.triples = [tuple(t) for t in json.load(f)]

            self.graph = nx.read_graphml(graph_path)
            print(f"📂 Loaded {len(self.triples)} triples from cache")
            return True
        except Exception as e:
            print(f"⚠ Failed to load cache: {e}")
            return False
