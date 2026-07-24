"""
ENTERPRISE BUSINESS RANKING & CRYPTO KARMA SCORER
Massive professional structured enterprise projects affecting
positive crypto karma scoring with corporate ranking system.

Enterprise Categories:
  FINTECH, HEALTHTECH, EDTECH, GREENTECH, SAFETECH, BLOCKCHAIN,
  AI_ML, CYBERSECURITY, CLOUD, ECOMMERCE, LEGALTECH, INSURTECH,
  PROPTech, HRTech, SUPPLYCHAIN, AGRITECH, GOVTECH, BIOTECH

Scoring Dimensions:
  REVENUE_IMPACT, JOB_CREATION, INNOVATION_INDEX, ESG_SCORE,
  COMPLIANCE_RATING, SECURITY_AUDIT, CUSTOMER_SATISFACTION,
  MARKET_DISRUPTION, SUSTAINABILITY_IMPACT, SOCIAL_RESPONSIBILITY

Crypto Karma Multipliers:
  Enterprise projects get multiplied karma based on
  revenue impact, job creation, and ESG score.
"""

import os
import json
import time
from datetime import datetime

DATA_DIR = os.path.join(os.getcwd(), "data", "enterprise")
os.makedirs(DATA_DIR, exist_ok=True)

ENTERPRISE_FILE = os.path.join(DATA_DIR, "enterprises.json")
RANKING_FILE = os.path.join(DATA_DIR, "rankings.json")

# ============================================================
#  ENTERPRISE CATEGORIES
# ============================================================

ENTERPRISE_CATEGORIES = {
    "FINTECH": {
        "name": "Financial Technology",
        "color": "bright_green",
        "icon": "FN",
        "base_multiplier": 2.5,
        "keywords": ["banking", "payment", "lending", "insurance", "trading", "wallet", "defi", "crypto", "blockchain", "fintech"],
        "compliance_required": ["PCI_DSS", "AML", "KYC", "SOC2"],
        "description": "Financial services, payments, lending, trading, DeFi",
    },
    "HEALTHTECH": {
        "name": "Healthcare Technology",
        "color": "bright_cyan",
        "icon": "HT",
        "base_multiplier": 3.0,
        "keywords": ["health", "medical", "telemedicine", "diagnosis", "patient", "clinical", "pharma", "biotech"],
        "compliance_required": ["HIPAA", "FDA", "GDPR", "SOC2"],
        "description": "Healthcare, medical devices, telemedicine, pharma",
    },
    "EDTECH": {
        "name": "Education Technology",
        "color": "bright_yellow",
        "icon": "ET",
        "base_multiplier": 2.8,
        "keywords": ["education", "learning", "school", "university", "course", "tutorial", "training", "mentor"],
        "compliance_required": ["FERPA", "COPPA", "GDPR"],
        "description": "Education platforms, e-learning, training, mentorship",
    },
    "GREENTECH": {
        "name": "Green Technology",
        "color": "bright_green",
        "icon": "GT",
        "base_multiplier": 3.5,
        "keywords": ["green", "solar", "wind", "carbon", "renewable", "sustainable", "eco", "climate", "environment"],
        "compliance_required": ["ISO14001", "EU_ETS", "CDP"],
        "description": "Renewable energy, carbon tracking, sustainability",
    },
    "SAFETECH": {
        "name": "Safety Technology",
        "color": "bright_red",
        "icon": "ST",
        "base_multiplier": 2.7,
        "keywords": ["safety", "security", "protection", "emergency", "disaster", "fire", "police"],
        "compliance_required": ["ISO27001", "NFPA", "OSHA"],
        "description": "Public safety, emergency response, disaster recovery",
    },
    "BLOCKCHAIN": {
        "name": "Blockchain & Web3",
        "color": "bright_magenta",
        "icon": "BC",
        "base_multiplier": 2.2,
        "keywords": ["blockchain", "web3", "nft", "dao", "token", "smart contract", "defi", "l2", "rollup"],
        "compliance_required": ["AML", "KYC", "SOC2"],
        "description": "Blockchain infrastructure, DeFi protocols, Web3 apps",
    },
    "AI_ML": {
        "name": "AI & Machine Learning",
        "color": "bright_blue",
        "icon": "AI",
        "base_multiplier": 3.2,
        "keywords": ["ai", "machine learning", "deep learning", "neural", "llm", "gpt", "model", "inference"],
        "compliance_required": ["SOC2", "GDPR", "EU_AI_ACT"],
        "description": "AI/ML platforms, LLMs, computer vision, NLP",
    },
    "CYBERSECURITY": {
        "name": "Cybersecurity",
        "color": "bright_red",
        "icon": "CS",
        "base_multiplier": 2.9,
        "keywords": ["security", "cyber", "firewall", "encryption", "threat", "vulnerability", "pentest"],
        "compliance_required": ["SOC2", "ISO27001", "NIST", "PCI_DSS"],
        "description": "Cybersecurity, threat detection, encryption",
    },
    "CLOUD": {
        "name": "Cloud Infrastructure",
        "color": "bright_cyan",
        "icon": "CL",
        "base_multiplier": 2.0,
        "keywords": ["cloud", "aws", "azure", "gcp", "serverless", "kubernetes", "docker", "saas"],
        "compliance_required": ["SOC2", "ISO27001", "FedRAMP"],
        "description": "Cloud platforms, SaaS, infrastructure",
    },
    "ECOMMERCE": {
        "name": "E-Commerce",
        "color": "bright_yellow",
        "icon": "EC",
        "base_multiplier": 1.8,
        "keywords": ["shop", "store", "marketplace", "checkout", "cart", "product", "order", "shipping"],
        "compliance_required": ["PCI_DSS", "GDPR", "CCPA"],
        "description": "E-commerce platforms, marketplaces, retail tech",
    },
    "LEGALTECH": {
        "name": "Legal Technology",
        "color": "bright_white",
        "icon": "LT",
        "base_multiplier": 2.3,
        "keywords": ["legal", "law", "compliance", "regulation", "contract", "audit", "governance"],
        "compliance_required": ["SOC2", "GDPR", "ISO27001"],
        "description": "Legal tech, compliance automation, governance",
    },
    "INSURTECH": {
        "name": "Insurance Technology",
        "color": "bright_cyan",
        "icon": "IT",
        "base_multiplier": 2.1,
        "keywords": ["insurance", "claim", "underwriting", "risk", "actuarial", "policy"],
        "compliance_required": ["SOC2", "GDPR", "HIPAA"],
        "description": "Insurance platforms, claims, underwriting",
    },
    "HRTech": {
        "name": "Human Resources Tech",
        "color": "bright_magenta",
        "icon": "HR",
        "base_multiplier": 1.9,
        "keywords": ["hr", "recruit", "talent", "payroll", "benefits", "employee", "workforce"],
        "compliance_required": ["SOC2", "GDPR", "EEOC"],
        "description": "HR platforms, recruitment, payroll",
    },
    "SUPPLYCHAIN": {
        "name": "Supply Chain Technology",
        "color": "bright_green",
        "icon": "SC",
        "base_multiplier": 2.0,
        "keywords": ["supply chain", "logistics", "warehouse", "inventory", "shipping", "tracking"],
        "compliance_required": ["SOC2", "ISO9001"],
        "description": "Supply chain, logistics, warehouse management",
    },
    "AGRITECH": {
        "name": "Agriculture Technology",
        "color": "bright_green",
        "icon": "AT",
        "base_multiplier": 3.0,
        "keywords": ["agriculture", "farming", "crop", "food", "precision", "iot", "drone"],
        "compliance_required": ["FDA", "USDA", "ISO22000"],
        "description": "AgTech, precision farming, food safety",
    },
    "GOVTECH": {
        "name": "Government Technology",
        "color": "bright_blue",
        "icon": "GV",
        "base_multiplier": 2.6,
        "keywords": ["government", "public sector", "municipal", "federal", "civic", "citizen"],
        "compliance_required": ["FedRAMP", "FISMA", "SOC2"],
        "description": "GovTech, civic tech, public sector platforms",
    },
    "BIOTECH": {
        "name": "Biotechnology",
        "color": "bright_cyan",
        "icon": "BT",
        "base_multiplier": 3.3,
        "keywords": ["biotech", "genomics", "dna", "crispr", "drug discovery", "clinical trial"],
        "compliance_required": ["FDA", "HIPAA", "ISO13485"],
        "description": "Biotech, genomics, drug discovery",
    },
    "PROPTech": {
        "name": "Property Technology",
        "color": "bright_yellow",
        "icon": "PT",
        "base_multiplier": 1.7,
        "keywords": ["real estate", "property", "rent", "mortgage", "building", "facility"],
        "compliance_required": ["SOC2", "GDPR"],
        "description": "PropTech, real estate platforms, facility management",
    },
}

# ============================================================
#  SCORING DIMENSIONS
# ============================================================

SCORING_DIMENSIONS = {
    "REVENUE_IMPACT": {
        "weight": 1.5,
        "icon": "RV",
        "desc": "Revenue Generation & Financial Impact",
        "thresholds": {1000000: 100, 500000: 80, 100000: 60, 50000: 40, 10000: 20, 0: 5},
    },
    "JOB_CREATION": {
        "weight": 1.8,
        "icon": "JB",
        "desc": "Employment & Workforce Impact",
        "thresholds": {1000: 100, 500: 80, 100: 60, 50: 40, 10: 20, 0: 5},
    },
    "INNOVATION_INDEX": {
        "weight": 2.0,
        "icon": "IN",
        "desc": "Innovation & Technology Advancement",
        "thresholds": {100: 100, 80: 85, 60: 70, 40: 55, 20: 35, 0: 10},
    },
    "ESG_SCORE": {
        "weight": 2.5,
        "icon": "ES",
        "desc": "Environmental, Social & Governance",
        "thresholds": {100: 100, 80: 85, 60: 70, 40: 50, 20: 30, 0: 5},
    },
    "COMPLIANCE_RATING": {
        "weight": 1.3,
        "icon": "CR",
        "desc": "Regulatory Compliance & Governance",
        "thresholds": {100: 100, 80: 80, 60: 60, 40: 40, 20: 20, 0: 0},
    },
    "SECURITY_AUDIT": {
        "weight": 1.4,
        "icon": "SA",
        "desc": "Security Posture & Audit Score",
        "thresholds": {100: 100, 80: 80, 60: 60, 40: 40, 20: 20, 0: 0},
    },
    "CUSTOMER_SATISFACTION": {
        "weight": 1.2,
        "icon": "CS",
        "desc": "Customer Satisfaction & NPS",
        "thresholds": {100: 100, 80: 80, 60: 60, 40: 40, 20: 20, 0: 5},
    },
    "MARKET_DISRUPTION": {
        "weight": 1.6,
        "icon": "MD",
        "desc": "Market Disruption & Competitive Edge",
        "thresholds": {100: 100, 80: 85, 60: 70, 40: 50, 20: 30, 0: 5},
    },
    "SUSTAINABILITY_IMPACT": {
        "weight": 2.2,
        "icon": "SU",
        "desc": "Environmental Sustainability & Carbon Reduction",
        "thresholds": {100: 100, 80: 85, 60: 70, 40: 50, 20: 30, 0: 5},
    },
    "SOCIAL_RESPONSIBILITY": {
        "weight": 1.7,
        "icon": "SR",
        "desc": "Corporate Social Responsibility & Community Impact",
        "thresholds": {100: 100, 80: 80, 60: 65, 40: 45, 20: 25, 0: 5},
    },
}

# ============================================================
#  ENTERPRISE RANKS
# ============================================================

ENTERPRISE_RANKS = [
    {"name": "Startup",             "min_score": 0,      "color": "dim",           "icon": "--", "tier": 1},
    {"name": "Small Business",      "min_score": 50,     "color": "bright_white",  "icon": ">>", "tier": 2},
    {"name": "Mid-Market",          "min_score": 200,    "color": "bright_cyan",   "icon": "**", "tier": 3},
    {"name": "Scale-Up",            "min_score": 500,    "color": "bright_green",  "icon": "##", "tier": 4},
    {"name": "Established",         "min_score": 1000,   "color": "bright_blue",   "icon": "@@", "tier": 5},
    {"name": "Market Leader",       "min_score": 2500,   "color": "bright_yellow", "icon": "$$", "tier": 6},
    {"name": "Industry Giant",      "min_score": 5000,   "color": "bright_magenta","icon": "%%", "tier": 7},
    {"name": "Global Powerhouse",   "min_score": 10000,  "color": "bright_red",    "icon": "^^", "tier": 8},
    {"name": "Fortune 500",         "min_score": 25000,  "color": "bright_yellow", "icon": "!!", "tier": 9},
    {"name": "Trillion Dollar Club","min_score": 50000,  "color": "bright_cyan",   "icon": "$$", "tier": 10},
]

# ============================================================
#  ENTERPRISE PROJECT TEMPLATES (Massive Structured)
# ============================================================

ENTERPRISE_PROJECT_TEMPLATES = [
    {
        "id": "global-banking-platform",
        "name": "Global Digital Banking Platform",
        "category": "FINTECH",
        "description": "Enterprise-grade digital banking platform serving 10M+ users across 50 countries",
        "dimensions": {"REVENUE_IMPACT": 95, "JOB_CREATION": 85, "INNOVATION_INDEX": 80, "ESG_SCORE": 75, "COMPLIANCE_RATING": 90, "SECURITY_AUDIT": 95, "CUSTOMER_SATISFACTION": 82, "MARKET_DISRUPTION": 78, "SUSTAINABILITY_IMPACT": 60, "SOCIAL_RESPONSIBILITY": 70},
        "crypto_karma_bonus": 500,
        "revenue_range": "$100M-$500M",
        "employees": "2000+",
        "compliance": ["PCI_DSS", "AML", "KYC", "SOC2", "GDPR"],
    },
    {
        "id": "ai-healthcare-diagnostics",
        "name": "AI-Powered Healthcare Diagnostics",
        "category": "HEALTHTECH",
        "description": "AI system that diagnoses diseases from medical imaging with 99.2% accuracy",
        "dimensions": {"REVENUE_IMPACT": 70, "JOB_CREATION": 60, "INNOVATION_INDEX": 98, "ESG_SCORE": 95, "COMPLIANCE_RATING": 85, "SECURITY_AUDIT": 90, "CUSTOMER_SATISFACTION": 88, "MARKET_DISRUPTION": 95, "SUSTAINABILITY_IMPACT": 80, "SOCIAL_RESPONSIBILITY": 95},
        "crypto_karma_bonus": 800,
        "revenue_range": "$50M-$200M",
        "employees": "500+",
        "compliance": ["HIPAA", "FDA", "GDPR", "SOC2"],
    },
    {
        "id": "global-edu-platform",
        "name": "Global Education Platform for Underserved",
        "category": "EDTECH",
        "description": "Free education platform providing quality courses to 50M+ students globally",
        "dimensions": {"REVENUE_IMPACT": 40, "JOB_CREATION": 50, "INNOVATION_INDEX": 75, "ESG_SCORE": 98, "COMPLIANCE_RATING": 70, "SECURITY_AUDIT": 75, "CUSTOMER_SATISFACTION": 92, "MARKET_DISRUPTION": 80, "SUSTAINABILITY_IMPACT": 85, "SOCIAL_RESPONSIBILITY": 99},
        "crypto_karma_bonus": 1000,
        "revenue_range": "$10M-$50M",
        "employees": "300+",
        "compliance": ["FERPA", "COPPA", "GDPR"],
    },
    {
        "id": "carbon-neutral-cloud",
        "name": "Carbon-Neutral Cloud Infrastructure",
        "category": "GREENTECH",
        "description": "100% renewable energy cloud computing platform offsetting 1M tons CO2",
        "dimensions": {"REVENUE_IMPACT": 85, "JOB_CREATION": 70, "INNOVATION_INDEX": 88, "ESG_SCORE": 99, "COMPLIANCE_RATING": 80, "SECURITY_AUDIT": 85, "CUSTOMER_SATISFACTION": 85, "MARKET_DISRUPTION": 82, "SUSTAINABILITY_IMPACT": 100, "SOCIAL_RESPONSIBILITY": 90},
        "crypto_karma_bonus": 750,
        "revenue_range": "$200M-$1B",
        "employees": "5000+",
        "compliance": ["ISO14001", "SOC2", "ISO27001"],
    },
    {
        "id": "defi-savings-protocol",
        "name": "DeFi Savings Protocol for Unbanked",
        "category": "BLOCKCHAIN",
        "description": "Decentralized savings protocol providing 8% APY to 2M unbanked users",
        "dimensions": {"REVENUE_IMPACT": 65, "JOB_CREATION": 45, "INNOVATION_INDEX": 92, "ESG_SCORE": 88, "COMPLIANCE_RATING": 72, "SECURITY_AUDIT": 88, "CUSTOMER_SATISFACTION": 80, "MARKET_DISRUPTION": 90, "SUSTAINABILITY_IMPACT": 70, "SOCIAL_RESPONSIBILITY": 85},
        "crypto_karma_bonus": 600,
        "revenue_range": "$20M-$100M",
        "employees": "150+",
        "compliance": ["AML", "KYC", "SOC2"],
    },
    {
        "id": "ai-cyberdefense",
        "name": "AI Cybersecurity Defense Grid",
        "category": "CYBERSECURITY",
        "description": "AI-powered threat detection protecting 100K+ enterprises from attacks",
        "dimensions": {"REVENUE_IMPACT": 80, "JOB_CREATION": 65, "INNOVATION_INDEX": 90, "ESG_SCORE": 82, "COMPLIANCE_RATING": 95, "SECURITY_AUDIT": 99, "CUSTOMER_SATISFACTION": 85, "MARKET_DISRUPTION": 85, "SUSTAINABILITY_IMPACT": 65, "SOCIAL_RESPONSIBILITY": 75},
        "crypto_karma_bonus": 550,
        "revenue_range": "$100M-$500M",
        "employees": "3000+",
        "compliance": ["SOC2", "ISO27001", "NIST", "PCI_DSS"],
    },
    {
        "id": "global-health-network",
        "name": "Global Healthcare Access Network",
        "category": "HEALTHTECH",
        "description": "Telemedicine platform connecting doctors to 100M patients in rural areas",
        "dimensions": {"REVENUE_IMPACT": 55, "JOB_CREATION": 75, "INNOVATION_INDEX": 82, "ESG_SCORE": 96, "COMPLIANCE_RATING": 80, "SECURITY_AUDIT": 85, "CUSTOMER_SATISFACTION": 90, "MARKET_DISRUPTION": 78, "SUSTAINABILITY_IMPACT": 75, "SOCIAL_RESPONSIBILITY": 98},
        "crypto_karma_bonus": 900,
        "revenue_range": "$30M-$150M",
        "employees": "800+",
        "compliance": ["HIPAA", "FDA", "GDPR"],
    },
    {
        "id": "quantum-computing-platform",
        "name": "Quantum Computing Cloud Platform",
        "category": "AI_ML",
        "description": "Cloud quantum computing accessible to researchers worldwide",
        "dimensions": {"REVENUE_IMPACT": 60, "JOB_CREATION": 55, "INNOVATION_INDEX": 100, "ESG_SCORE": 78, "COMPLIANCE_RATING": 75, "SECURITY_AUDIT": 82, "CUSTOMER_SATISFACTION": 78, "MARKET_DISRUPTION": 98, "SUSTAINABILITY_IMPACT": 70, "SOCIAL_RESPONSIBILITY": 80},
        "crypto_karma_bonus": 700,
        "revenue_range": "$50M-$250M",
        "employees": "1000+",
        "compliance": ["SOC2", "GDPR", "ISO27001"],
    },
    {
        "id": "legal-ai-assistant",
        "name": "AI Legal Assistant for Small Businesses",
        "category": "LEGALTECH",
        "description": "AI that helps small businesses navigate legal compliance at 1/10th cost",
        "dimensions": {"REVENUE_IMPACT": 50, "JOB_CREATION": 40, "INNOVATION_INDEX": 85, "ESG_SCORE": 80, "COMPLIANCE_RATING": 90, "SECURITY_AUDIT": 85, "CUSTOMER_SATISFACTION": 88, "MARKET_DISRUPTION": 82, "SUSTAINABILITY_IMPACT": 65, "SOCIAL_RESPONSIBILITY": 82},
        "crypto_karma_bonus": 400,
        "revenue_range": "$10M-$50M",
        "employees": "200+",
        "compliance": ["SOC2", "GDPR", "ISO27001"],
    },
    {
        "id": "agritech-precision-farming",
        "name": "AI Precision Farming Platform",
        "category": "AGRITECH",
        "description": "AI-powered precision farming reducing water usage 40% for 1M farmers",
        "dimensions": {"REVENUE_IMPACT": 45, "JOB_CREATION": 60, "INNOVATION_INDEX": 88, "ESG_SCORE": 95, "COMPLIANCE_RATING": 70, "SECURITY_AUDIT": 72, "CUSTOMER_SATISFACTION": 85, "MARKET_DISRUPTION": 80, "SUSTAINABILITY_IMPACT": 98, "SOCIAL_RESPONSIBILITY": 95},
        "crypto_karma_bonus": 650,
        "revenue_range": "$5M-$30M",
        "employees": "100+",
        "compliance": ["FDA", "USDA", "ISO22000"],
    },
]


def _load_enterprises():
    if os.path.exists(ENTERPRISE_FILE):
        with open(ENTERPRISE_FILE, "r") as f:
            return json.load(f)
    return {"enterprises": {}, "history": []}


def _save_enterprises(data):
    with open(ENTERPRISE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _load_rankings():
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, "r") as f:
            return json.load(f)
    return {"global_rankings": [], "category_rankings": {}, "crypto_karma_total": 0}


def _save_rankings(data):
    with open(RANKING_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
#  ENTERPRISE SCORING ENGINE
# ============================================================

class EnterpriseScorer:
    """Scores enterprise projects for positive/negative crypto karma impact."""

    def __init__(self):
        self.data = _load_enterprises()
        self.rankings = _load_rankings()

    def score_enterprise(self, enterprise_id, name, category, dimensions, user_id="default"):
        if category not in ENTERPRISE_CATEGORIES:
            return {"error": "Unknown category: " + category}

        cat = ENTERPRISE_CATEGORIES[category]
        total_score = 0
        dimension_scores = {}

        for dim_key, dim_config in SCORING_DIMENSIONS.items():
            raw_value = dimensions.get(dim_key, 0)
            score = 0
            for threshold in sorted(dim_config["thresholds"].keys(), reverse=True):
                if raw_value >= threshold:
                    score = dim_config["thresholds"][threshold]
                    break
            weighted = round(score * dim_config["weight"], 2)
            dimension_scores[dim_key] = {"raw": raw_value, "score": score, "weighted": weighted}
            total_score += weighted

        base_karma = round(total_score * cat["base_multiplier"], 2)

        is_positive = base_karma > 0
        esg = dimensions.get("ESG_SCORE", 0)
        compliance = dimensions.get("COMPLIANCE_RATING", 0)
        security = dimensions.get("SECURITY_AUDIT", 0)

        esg_bonus = esg * 2.5 if esg >= 80 else esg * 1.5 if esg >= 50 else 0
        compliance_bonus = compliance * 1.2 if compliance >= 70 else 0
        security_bonus = security * 1.3 if security >= 75 else 0

        crypto_karma = round(base_karma + esg_bonus + compliance_bonus + security_bonus, 2)
        crypto_karma = round(crypto_karma * 10, 2)

        negative_flags = []
        if compliance < 30:
            negative_flags.append("LOW_COMPLIANCE")
            crypto_karma *= 0.5
        if security < 25:
            negative_flags.append("SECURITY_RISK")
            crypto_karma *= 0.6
        if esg < 20:
            negative_flags.append("ESG_FAILURE")
            crypto_karma *= 0.7

        crypto_karma = round(max(crypto_karma, -1000), 2)

        rank = self._get_rank(crypto_karma)

        result = {
            "enterprise_id": enterprise_id,
            "name": name,
            "category": category,
            "user_id": user_id,
            "dimension_scores": dimension_scores,
            "base_karma": base_karma,
            "crypto_karma": crypto_karma,
            "rank": rank["name"],
            "rank_tier": rank["tier"],
            "negative_flags": negative_flags,
            "is_positive": is_positive,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._record_enterprise(result)
        return result

    def _get_rank(self, score):
        score = abs(score)
        rank = ENTERPRISE_RANKS[0]
        for r in ENTERPRISE_RANKS:
            if score >= r["min_score"]:
                rank = r
        return rank

    def _record_enterprise(self, result):
        eid = result["enterprise_id"]
        self.data["enterprises"][eid] = result
        self.data["history"].append(result)
        if len(self.data["history"]) > 200:
            self.data["history"] = self.data["history"][-200:]

        self.rankings["crypto_karma_total"] = round(
            self.rankings.get("crypto_karma_total", 0) + abs(result["crypto_karma"]), 2
        )

        cat = result["category"]
        if cat not in self.rankings["category_rankings"]:
            self.rankings["category_rankings"][cat] = []
        self.rankings["category_rankings"][cat].append({
            "id": eid,
            "name": result["name"],
            "crypto_karma": result["crypto_karma"],
            "rank": result["rank"],
        })
        self.rankings["category_rankings"][cat].sort(key=lambda x: -x["crypto_karma"])

        all_entries = []
        for entries in self.rankings["category_rankings"].values():
            all_entries.extend(entries)
        all_entries.sort(key=lambda x: -x["crypto_karma"])
        self.rankings["global_rankings"] = all_entries[:50]

        _save_enterprises(self.data)
        _save_rankings(self.rankings)

    def get_global_rankings(self, limit=30):
        return self.rankings.get("global_rankings", [])[:limit]

    def get_category_rankings(self, category, limit=20):
        return self.rankings.get("category_rankings", {}).get(category, [])[:limit]

    def get_crypto_karma_total(self):
        return self.rankings.get("crypto_karma_total", 0)

    def get_enterprise(self, enterprise_id):
        return self.data["enterprises"].get(enterprise_id)

    def get_all_enterprises(self):
        return self.data["enterprises"]

    def get_templates(self):
        return ENTERPRISE_PROJECT_TEMPLATES

    def get_categories(self):
        return ENTERPRISE_CATEGORIES

    def get_ranks(self):
        return ENTERPRISE_RANKS

    def get_dimensions(self):
        return SCORING_DIMENSIONS
