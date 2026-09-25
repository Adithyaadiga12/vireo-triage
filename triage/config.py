"""All tunable numbers and paths live here, so nothing is hard-coded elsewhere.

Every rupee figure comes from support-policy.pdf (v3.2) or the email thread.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
PROMPT_DIR = ROOT / "prompts"

# Reporting window stated in the brief. Rows outside it are dropped (and counted).
WINDOW_START = "2025-01-01"
WINDOW_END = "2026-07-01"  # exclusive

# Policy §9: legacy (Freshdesk) resolution times were rebuilt from a UTC event log.
# Everything else is displayed in IST, so legacy resolved_at is shifted by +5:30.
LEGACY_SYSTEM = "legacy_fd"
UTC_TO_IST = "5h30m"

# Policy §3: first-response targets (hours) and the credit paid on a breach.
FIRST_RESPONSE_TARGET_HOURS = {"chat": 0.25, "voice": 2, "social": 4, "email": 8}
BREACH_CREDIT_INR = 350

# Policy §4: cost standards.
TRANSFER_COST_INR = 305
CONTACT_COST_INR = {"chat": 210, "email": 260, "voice": 520, "social": 240}
AGENT_HOUR_COST_INR = 165

# Email thread (Arjun Mehta): two hires ~ Rs 9 lakh a year.
TWO_HIRES_COST_INR_PER_YEAR = 900_000

# Submission form: Vireo handles roughly 650 tickets a week.
STATED_TICKETS_PER_WEEK = 650

# Gemini defaults (override in .env). Prices are USD per 1M tokens, paid tier,
# from ai.google.dev/gemini-api/docs/pricing, checked 24 Sep 2026.
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_PRICE_USD_PER_M = {"input": 0.30, "output": 2.50}
USD_TO_INR = 88.0  # approximate; only used for the cost estimate
TICKETS_PER_LLM_CALL = 20
