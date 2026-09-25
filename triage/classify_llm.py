"""Gemini classifier: sends tickets in batches, caches every answer, logs token cost.

Design choices, in plain words:
- Batches of ~20 tickets per call: the instructions are sent once per batch
  instead of once per ticket, which cuts cost and keeps us under free-tier limits.
- Every answer is cached in outputs/cache/. Re-running never pays twice, and an
  interrupted run resumes where it stopped.
- Two modes. "intake" uses only the customer's opening message, i.e. exactly what
  the chat bot sees, so it tests whether routing at intake can be fixed.
  "full" also reads the agent's closing note, for the most accurate history.
- Any answer that is not a valid category becomes "Other" and is counted.
"""
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import config
from .taxonomy import CATEGORIES, CATEGORY_NAMES

MODES = ("intake", "full")


@dataclass
class UsageTotals:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    invalid_answers: int = 0

    def cost_usd(self) -> float:
        price = config.GEMINI_PRICE_USD_PER_M
        return (self.input_tokens * price["input"] + self.output_tokens * price["output"]) / 1e6


def ticket_text(row: pd.Series, mode: str) -> str:
    text = f"Channel: {row['channel']}. Customer: {row['customer_message']}"
    if mode == "full" and isinstance(row.get("agent_notes"), str):
        text += f"\nAgent closing note: {row['agent_notes']}"
    return text


def build_prompt(prompt_version: str, batch: list[dict]) -> str:
    template = (config.PROMPT_DIR / f"classify_{prompt_version}.txt").read_text()
    return template.format(
        category_list="\n".join(f"- {name}" for name in CATEGORY_NAMES),
        category_definitions="\n".join(f"- {name}: {desc}" for name, (_, desc) in CATEGORIES.items()),
        tickets_json=json.dumps(batch, ensure_ascii=False, indent=1),
    )


def parse_response(text: str, expected_ids: list[str]) -> tuple[dict[str, dict], int]:
    """Turn the model's JSON into {ticket_id: {category, confidence}}.

    Returns the answers plus how many were invalid (unknown category or missing).
    Tolerates a ```json fence and a {"tickets": [...]} wrapper.
    """
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    data = json.loads(text)
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), [])
    answers, invalid = {}, 0
    for item in data:
        ticket_id = str(item.get("id"))
        category = item.get("category")
        if ticket_id not in expected_ids:
            continue
        if category not in CATEGORIES:
            invalid += 1
            category = "Other"
        answers[ticket_id] = {"category": category, "confidence": item.get("confidence", "")}
    invalid += len(set(expected_ids) - set(answers))
    return answers, invalid


class GeminiClassifier:
    def __init__(self, prompt_version: str = "v2", mode: str = "intake",
                 model: str | None = None, client=None):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        self.prompt_version = prompt_version
        self.mode = mode
        self.model = model or os.getenv("GEMINI_MODEL", config.DEFAULT_GEMINI_MODEL)
        self.client = client or self._make_client()
        self.usage = UsageTotals()
        cache_name = f"{self.model}_{prompt_version}_{mode}.jsonl".replace("/", "-")
        self.cache_path = config.OUTPUT_DIR / "cache" / cache_name

    @staticmethod
    def _make_client():
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit("GEMINI_API_KEY is not set. Copy .env.example to .env and add "
                             "your key, or use --engine rules.")
        from google import genai
        return genai.Client(api_key=api_key)

    # ---- cache -----------------------------------------------------------
    def _load_cache(self) -> dict[str, dict]:
        if not self.cache_path.exists():
            return {}
        cached = {}
        for line in self.cache_path.read_text().splitlines():
            record = json.loads(line)
            cached[record["ticket_id"]] = record
        return cached

    def _append_cache(self, answers: dict[str, dict]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_path.open("a") as f:
            for ticket_id, answer in answers.items():
                f.write(json.dumps({"ticket_id": ticket_id, **answer}) + "\n")

    # ---- API -------------------------------------------------------------
    def _call(self, prompt: str, retries: int = 5) -> str:
        from google.genai import errors, types
        settings = types.GenerateContentConfig(temperature=0,
                                               response_mime_type="application/json")
        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt, config=settings)
                self._record_usage(response)
                return response.text
            except errors.APIError as error:
                retryable = error.code in (429, 500, 503)
                if not retryable or attempt == retries - 1:
                    raise
                wait = 2 ** attempt * 5
                print(f"  Gemini returned {error.code}; waiting {wait}s and retrying...")
                time.sleep(wait)
        raise RuntimeError("unreachable")

    def _record_usage(self, response) -> None:
        meta = response.usage_metadata
        self.usage.calls += 1
        self.usage.input_tokens += meta.prompt_token_count or 0
        # Thinking tokens are billed as output, so count them.
        self.usage.output_tokens += (meta.candidates_token_count or 0) + (
            getattr(meta, "thoughts_token_count", 0) or 0)

    # ---- public ----------------------------------------------------------
    def classify(self, tickets: pd.DataFrame) -> pd.DataFrame:
        """Return a DataFrame: ticket_id, category, confidence (cached where possible)."""
        cached = self._load_cache()
        todo = tickets[~tickets["ticket_id"].isin(cached)]
        batch_size = config.TICKETS_PER_LLM_CALL
        n_batches = -(-len(todo) // batch_size)
        print(f"{len(tickets) - len(todo)} tickets already cached; "
              f"{len(todo)} to classify in {n_batches} calls with {self.model}.")

        for i, start in enumerate(range(0, len(todo), batch_size), 1):
            rows = todo.iloc[start:start + batch_size]
            batch = [{"id": row["ticket_id"], "text": ticket_text(row, self.mode)}
                     for _, row in rows.iterrows()]
            answers, invalid = parse_response(
                self._call(build_prompt(self.prompt_version, batch)),
                expected_ids=[b["id"] for b in batch])
            self.usage.invalid_answers += invalid
            self._append_cache(answers)
            cached.update({k: {"ticket_id": k, **v} for k, v in answers.items()})
            print(f"  batch {i}/{n_batches} done "
                  f"(running cost ${self.usage.cost_usd():.4f})")

        result = pd.DataFrame([cached[t] for t in tickets["ticket_id"] if t in cached])
        return result
