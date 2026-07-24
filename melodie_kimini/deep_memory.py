"""
DEEP MEMORY CONSTRUCTION ENGINE
Persistent memory system that builds knowledge over time.
Every prompt/response is remembered and used to enhance future interactions.
"""

import os
import json
import hashlib
import time
from collections import defaultdict

DATA_DIR = os.path.join(os.getcwd(), "data", "deep_memory")
os.makedirs(DATA_DIR, exist_ok=True)

MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
CONCEPTS_FILE = os.path.join(DATA_DIR, "concepts.json")
RELATIONS_FILE = os.path.join(DATA_DIR, "relations.json")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")


def _load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


class DeepMemoryEngine:
    """Persistent memory that remembers everything and builds knowledge."""

    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.memory = _load_json(MEMORY_FILE, {
            "sessions": [],
            "total_interactions": 0,
            "total_tokens_processed": 0,
            "memory_strength": 0.0,
            "knowledge_graph": {},
            "created_at": time.time(),
        })
        self.concepts = _load_json(CONCEPTS_FILE, {
            "concepts": {},
            "concept_count": 0,
            "strongest_concepts": [],
        })
        self.relations = _load_json(RELATIONS_FILE, {
            "relations": [],
            "relation_count": 0,
        })
        self.scores = _load_json(SCORES_FILE, {
            "interactions": [],
            "avg_impact": 0.0,
            "total_impact": 0.0,
            "reasoning_depth": 0.0,
            "godlike_score": 0.0,
        })

    def _save_all(self):
        _save_json(MEMORY_FILE, self.memory)
        _save_json(CONCEPTS_FILE, self.concepts)
        _save_json(RELATIONS_FILE, self.relations)
        _save_json(SCORES_FILE, self.scores)

    def remember_interaction(self, user_prompt, model_response, model_id, impact_score, reasoning_data):
        """Store a complete interaction in deep memory."""
        entry = {
            "id": hashlib.sha256(
                (self.user_id + user_prompt + str(time.time())).encode()
            ).hexdigest()[:16],
            "timestamp": time.time(),
            "user_id": self.user_id,
            "model": model_id,
            "prompt": user_prompt,
            "response_preview": model_response[:200] if model_response else "",
            "prompt_length": len(user_prompt),
            "response_length": len(model_response) if model_response else 0,
            "impact_score": impact_score,
            "reasoning_depth": reasoning_data.get("depth", 0),
            "concepts_extracted": reasoning_data.get("concepts", []),
            "tags": reasoning_data.get("tags", []),
        }

        self.memory["sessions"].append(entry)
        if len(self.memory["sessions"]) > 1000:
            self.memory["sessions"] = self.memory["sessions"][-1000:]

        self.memory["total_interactions"] += 1
        self.memory["total_tokens_processed"] += entry["prompt_length"] + entry["response_length"]

        for concept in reasoning_data.get("concepts", []):
            self._add_concept(concept, impact_score)

        for tag in reasoning_data.get("tags", []):
            for other_tag in reasoning_data.get("tags", []):
                if tag != other_tag:
                    self._add_relation(tag, other_tag, impact_score)

        self.memory["memory_strength"] = min(100.0, self.memory["memory_strength"] + 0.1)

        self.scores["interactions"].append({
            "timestamp": time.time(),
            "impact": impact_score,
            "reasoning": reasoning_data.get("depth", 0),
            "model": model_id,
        })
        if len(self.scores["interactions"]) > 500:
            self.scores["interactions"] = self.scores["interactions"][-500:]

        impacts = [s["impact"] for s in self.scores["interactions"]]
        self.scores["avg_impact"] = sum(impacts) / len(impacts) if impacts else 0
        self.scores["total_impact"] = sum(impacts)
        depths = [s["reasoning"] for s in self.scores["interactions"]]
        self.scores["reasoning_depth"] = sum(depths) / len(depths) if depths else 0
        self.scores["godlike_score"] = round(
            (self.scores["avg_impact"] * 0.4) +
            (self.scores["reasoning_depth"] * 0.3) +
            (min(self.memory["total_interactions"], 100) * 0.3),
            2
        )

        self._save_all()
        return entry

    def _add_concept(self, concept, weight):
        """Add or strengthen a concept in memory."""
        c = concept.lower().strip()
        if c not in self.concepts["concepts"]:
            self.concepts["concepts"][c] = {
                "name": c,
                "count": 0,
                "total_weight": 0.0,
                "first_seen": time.time(),
                "last_seen": time.time(),
                "strength": 0.0,
            }
            self.concepts["concept_count"] += 1

        entry = self.concepts["concepts"][c]
        entry["count"] += 1
        entry["total_weight"] += weight
        entry["last_seen"] = time.time()
        entry["strength"] = min(100.0, entry["count"] * 2 + entry["total_weight"] * 0.1)

        sorted_concepts = sorted(
            self.concepts["concepts"].values(),
            key=lambda x: x["strength"],
            reverse=True
        )
        self.concepts["strongest_concepts"] = [c["name"] for c in sorted_concepts[:50]]

    def _add_relation(self, tag_a, tag_b, weight):
        """Add or strengthen a relation between concepts."""
        key = tuple(sorted([tag_a.lower(), tag_b.lower()]))
        found = False
        for rel in self.relations["relations"]:
            if rel["key"] == key:
                rel["weight"] += weight * 0.5
                rel["count"] += 1
                rel["last_seen"] = time.time()
                found = True
                break

        if not found:
            self.relations["relations"].append({
                "key": key,
                "from": key[0],
                "to": key[1],
                "weight": weight * 0.5,
                "count": 1,
                "first_seen": time.time(),
                "last_seen": time.time(),
            })
            self.relations["relation_count"] += 1

        if len(self.relations["relations"]) > 500:
            self.relations["relations"].sort(key=lambda x: -x["weight"])
            self.relations["relations"] = self.relations["relations"][:500]

    def recall_related(self, prompt, limit=5):
        """Recall memory entries related to a prompt."""
        prompt_lower = prompt.lower()
        prompt_words = set(prompt_lower.split())

        scored = []
        for entry in self.memory["sessions"][-200:]:
            score = 0
            entry_words = set(entry["prompt"].lower().split())
            overlap = prompt_words & entry_words
            score += len(overlap) * 10

            for tag in entry.get("tags", []):
                if tag.lower() in prompt_lower:
                    score += 15

            for concept in entry.get("concepts_extracted", []):
                if concept.lower() in prompt_lower:
                    score += 20

            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: -x[0])
        return [e for _, e in scored[:limit]]

    def get_concept_context(self, prompt):
        """Get relevant concept context for a prompt."""
        prompt_lower = prompt.lower()
        relevant = []
        for name, data in self.concepts["concepts"].items():
            if name in prompt_lower or any(w in name for w in prompt_lower.split()):
                relevant.append({
                    "concept": name,
                    "strength": data["strength"],
                    "count": data["count"],
                })
        relevant.sort(key=lambda x: -x["strength"])
        return relevant[:10]

    def get_memory_stats(self):
        """Get memory statistics."""
        return {
            "total_interactions": self.memory["total_interactions"],
            "total_tokens": self.memory["total_tokens_processed"],
            "memory_strength": round(self.memory["memory_strength"], 1),
            "concept_count": self.concepts["concept_count"],
            "relation_count": self.relations["relation_count"],
            "avg_impact": round(self.scores["avg_impact"], 2),
            "total_impact": round(self.scores["total_impact"], 2),
            "reasoning_depth": round(self.scores["reasoning_depth"], 2),
            "godlike_score": round(self.scores["godlike_score"], 2),
            "strongest_concepts": self.concepts["strongest_concepts"][:10],
            "recent_interactions": len(self.memory["sessions"]),
        }

    def get_memory_strength_bar(self):
        """Visual bar for memory strength."""
        strength = self.memory["memory_strength"]
        filled = int(strength / 10)
        return "#" * filled + "." * (10 - filled)

    def get_godlike_bar(self):
        """Visual bar for godlike score."""
        score = min(100, self.scores["godlike_score"])
        filled = int(score / 10)
        return "@" * filled + "." * (10 - filled)

    def get_knowledge_graph_summary(self):
        """Get top concepts and their connections."""
        top_concepts = self.concepts["strongest_concepts"][:15]
        top_relations = sorted(
            self.relations["relations"],
            key=lambda x: -x["weight"]
        )[:15]
        return {
            "top_concepts": top_concepts,
            "top_relations": [{"from": r["from"], "to": r["to"], "weight": round(r["weight"], 1)} for r in top_relations],
        }
