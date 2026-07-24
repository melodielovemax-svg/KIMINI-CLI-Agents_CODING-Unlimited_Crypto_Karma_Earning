"""
DEEP REASONING GODLIKE IMPACT SCORE
Analyzes every interaction for reasoning depth, impact, and builds knowledge.
"""

import hashlib
import time
import math

CONCEPT_KEYWORDS = {
    "code": ["code", "function", "class", "variable", "debug", "error", "api", "method", "loop", "array"],
    "ai": ["ai", "model", "neural", "train", "deep", "machine", "learning", "network", "transformer"],
    "finance": ["money", "crypto", "token", "karma", "wallet", "stake", "mine", "revenue", "payment"],
    "security": ["security", "encrypt", "hash", "vault", "auth", "token", "protect", "secure"],
    "data": ["data", "database", "query", "sql", "json", "schema", "table", "index"],
    "web": ["web", "http", "api", "rest", "graphql", "server", "client", "frontend"],
    "devops": ["docker", "deploy", "ci", "cd", "pipeline", "build", "test", "monitor"],
    "design": ["ui", "ux", "design", "layout", "color", "font", "css", "style"],
    "math": ["math", "calculate", "formula", "equation", "statistics", "probability"],
    "logic": ["logic", "algorithm", "optimization", "pattern", "strategy", "reasoning"],
}

IMPACT_DIMENSIONS = {
    "complexity": {"weight": 0.20, "desc": "Question complexity"},
    "specificity": {"weight": 0.15, "desc": "Specificity of request"},
    "creativity": {"weight": 0.15, "desc": "Creative thinking required"},
    "technical": {"weight": 0.20, "desc": "Technical depth"},
    "practical": {"weight": 0.15, "desc": "Practical applicability"},
    "reasoning": {"weight": 0.15, "desc": "Reasoning chain length"},
}


class DeepReasoningEngine:
    """Godlike impact scoring for every interaction."""

    def __init__(self):
        self.session_scores = []
        self.total_analyzed = 0

    def analyze_interaction(self, prompt, model_id, response_length=0):
        """Full analysis of an interaction - returns impact score + reasoning data."""
        prompt_lower = prompt.lower()
        words = prompt_lower.split()
        word_count = len(words)

        concepts = self._extract_concepts(prompt_lower, words)
        tags = self._extract_tags(prompt_lower, words)
        dimensions = self._score_dimensions(prompt, words, concepts, response_length)
        reasoning_depth = self._calculate_reasoning_depth(prompt, words, concepts)
        impact_score = self._calculate_impact(dimensions, reasoning_depth, word_count)

        godlike_tier = self._get_godlike_tier(impact_score)

        self.total_analyzed += 1
        self.session_scores.append(impact_score)

        return {
            "impact_score": round(impact_score, 2),
            "reasoning_depth": round(reasoning_depth, 2),
            "concepts": concepts,
            "tags": tags,
            "dimensions": dimensions,
            "godlike_tier": godlike_tier,
            "word_count": word_count,
            "complexity": dimensions.get("complexity", {}).get("score", 0),
            "timestamp": time.time(),
            "model": model_id,
            "response_length": response_length,
        }

    def _extract_concepts(self, prompt_lower, words):
        """Extract concept categories from prompt."""
        concepts = []
        for category, keywords in CONCEPT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in prompt_lower)
            if matches > 0:
                concepts.append(category)
        if not concepts:
            concepts = ["general"]
        return concepts

    def _extract_tags(self, prompt_lower, words):
        """Extract meaningful tags from prompt."""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "need", "dare", "ought",
            "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above", "below",
            "between", "out", "off", "over", "under", "again", "further", "then",
            "once", "here", "there", "when", "where", "why", "how", "all", "both",
            "each", "few", "more", "most", "other", "some", "such", "no", "nor",
            "not", "only", "own", "same", "so", "than", "too", "very", "just",
            "don", "now", "and", "but", "or", "if", "while", "that", "this",
            "it", "its", "i", "me", "my", "we", "our", "you", "your", "he",
            "him", "his", "she", "her", "they", "them", "their", "what", "which",
            "who", "whom", "these", "those", "am", "about", "up", "down",
        }
        tags = []
        seen = set()
        for w in words:
            clean = w.strip(".,!?;:\"'()[]{}")
            if len(clean) > 2 and clean not in stop_words and clean not in seen:
                tags.append(clean)
                seen.add(clean)
        return tags[:20]

    def _score_dimensions(self, prompt, words, concepts, response_length):
        """Score each impact dimension."""
        dimensions = {}
        word_count = len(words)
        unique_words = len(set(words))

        complexity_score = min(100, (word_count * 2) + (len(concepts) * 15) + (unique_words * 1))
        dimensions["complexity"] = {
            "score": round(complexity_score, 1),
            "desc": IMPACT_DIMENSIONS["complexity"]["desc"],
        }

        specificity_score = min(100, (unique_words * 5) + (len([w for w in words if w.isupper()]) * 10))
        if "?" in prompt:
            specificity_score += 10
        dimensions["specificity"] = {
            "score": round(specificity_score, 1),
            "desc": IMPACT_DIMENSIONS["specificity"]["desc"],
        }

        creative_words = ["create", "design", "build", "imagine", "innovate", "novel", "unique", "artistic"]
        creativity_hits = sum(1 for w in words if w in creative_words)
        creativity_score = min(100, creativity_hits * 20 + len(concepts) * 5)
        dimensions["creativity"] = {
            "score": round(creativity_score, 1),
            "desc": IMPACT_DIMENSIONS["creativity"]["desc"],
        }

        tech_words = ["code", "api", "database", "server", "algorithm", "function", "class", "debug", "deploy"]
        tech_hits = sum(1 for w in words if w in tech_words)
        technical_score = min(100, tech_hits * 15 + word_count * 2)
        dimensions["technical"] = {
            "score": round(technical_score, 1),
            "desc": IMPACT_DIMENSIONS["technical"]["desc"],
        }

        practical_words = ["use", "apply", "implement", "fix", "solve", "optimize", "improve", "setup"]
        practical_hits = sum(1 for w in words if w in practical_words)
        practical_score = min(100, practical_hits * 20 + (100 if response_length > 500 else 0))
        dimensions["practical"] = {
            "score": round(practical_score, 1),
            "desc": IMPACT_DIMENSIONS["practical"]["desc"],
        }

        reasoning_score = min(100, word_count * 3 + len(concepts) * 10)
        if any(w in prompt.lower() for w in ["why", "how", "explain", "reason"]):
            reasoning_score += 25
        if any(w in prompt.lower() for w in ["compare", "analyze", "evaluate", "assess"]):
            reasoning_score += 20
        dimensions["reasoning"] = {
            "score": round(reasoning_score, 1),
            "desc": IMPACT_DIMENSIONS["reasoning"]["desc"],
        }

        return dimensions

    def _calculate_reasoning_depth(self, prompt, words, concepts):
        """Calculate how deep the reasoning chain is."""
        depth = 0
        depth += min(30, len(words) * 1.5)
        depth += min(20, len(concepts) * 8)

        if any(w in prompt.lower() for w in ["why", "because", "reason"]):
            depth += 15
        if any(w in prompt.lower() for w in ["how", "process", "step"]):
            depth += 12
        if any(w in prompt.lower() for w in ["if", "then", "else", "condition"]):
            depth += 10
        if any(w in prompt.lower() for w in ["compare", "versus", "difference"]):
            depth += 8
        if any(w in prompt.lower() for w in ["optimize", "improve", "better"]):
            depth += 7
        if any(w in prompt.lower() for w in ["error", "bug", "fix", "debug"]):
            depth += 10

        return min(100, depth)

    def _calculate_impact(self, dimensions, reasoning_depth, word_count):
        """Calculate final impact score."""
        weighted_sum = 0
        for dim_name, dim_data in dimensions.items():
            weight = IMPACT_DIMENSIONS.get(dim_name, {}).get("weight", 0.1)
            weighted_sum += dim_data["score"] * weight

        reasoning_bonus = reasoning_depth * 0.3
        length_bonus = min(15, word_count * 0.5)

        total = weighted_sum + reasoning_bonus + length_bonus
        return min(100, max(0, total))

    def _get_godlike_tier(self, score):
        """Get godlike tier based on impact score."""
        if score >= 90:
            return "DIVINE"
        elif score >= 75:
            return "LEGENDARY"
        elif score >= 60:
            return "EPIC"
        elif score >= 45:
            return "RARE"
        elif score >= 30:
            return "UNCOMMON"
        else:
            return "COMMON"

    def get_session_stats(self):
        """Get session statistics."""
        if not self.session_scores:
            return {
                "count": 0, "avg": 0, "max": 0, "min": 0,
                "total": 0, "godlike_avg": 0,
            }
        return {
            "count": len(self.session_scores),
            "avg": round(sum(self.session_scores) / len(self.session_scores), 2),
            "max": round(max(self.session_scores), 2),
            "min": round(min(self.session_scores), 2),
            "total": round(sum(self.session_scores), 2),
            "godlike_avg": round(sum(self.session_scores) / len(self.session_scores) * 10, 1),
        }

    def get_impact_bar(self, score):
        """Visual bar for impact score."""
        filled = int(score / 10)
        return "@" * filled + "." * (10 - filled)

    def get_tier_color(self, tier):
        """Color for godlike tier."""
        colors = {
            "DIVINE": "bright_yellow",
            "LEGENDARY": "bright_magenta",
            "EPIC": "bright_cyan",
            "RARE": "bright_blue",
            "UNCOMMON": "bright_green",
            "COMMON": "bright_white",
        }
        return colors.get(tier, "bright_white")
