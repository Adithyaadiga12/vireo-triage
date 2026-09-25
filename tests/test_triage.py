"""Tests that run with no API key and no network.

The Gemini path is exercised with a fake client that returns canned JSON, so the
batching, parsing, caching and cost-counting logic is covered.
"""
import json
from types import SimpleNamespace

import pandas as pd
import pytest

from triage import config
from triage.classify_llm import GeminiClassifier, build_prompt, parse_response
from triage.classify_rules import classify_text
from triage.data import load_tickets


# ---------------------------------------------------------------- data cleaning
@pytest.fixture(scope="module")
def tickets():
    frame, _ = load_tickets()
    return frame


def test_no_ticket_resolves_before_it_was_created(tickets):
    assert (tickets["resolution_hours"].dropna() >= 0).all()


def test_only_reporting_window_kept(tickets):
    assert tickets["created_at"].min() >= pd.Timestamp(config.WINDOW_START)
    assert tickets["created_at"].max() < pd.Timestamp(config.WINDOW_END)


def test_every_ticket_has_a_resolving_team(tickets):
    assert tickets["resolving_team"].notna().all()


# ---------------------------------------------------------------- keyword rules
@pytest.mark.parametrize("message, expected", [
    ("paid but package not delivered even after 11 days", "Delivery & Shipping"),
    ("amount deducted, no order confirmation", "Billing & Payments"),
    ("you picked up the item 19 days ago and my money hasn't come back", "Returns & Refunds"),
    ("left bud won't pair with my phone. i want my money back", "Connectivity"),
])
def test_keyword_rules(message, expected):
    assert classify_text(message) == expected


# ---------------------------------------------------------------- LLM parsing
def test_parse_response_handles_fences_and_bad_categories():
    raw = '```json\n[{"id": "T1", "category": "Delivery & Shipping", "confidence": "high"},' \
          ' {"id": "T2", "category": "Made Up"}]\n```'
    answers, invalid = parse_response(raw, expected_ids=["T1", "T2", "T3"])
    assert answers["T1"]["category"] == "Delivery & Shipping"
    assert answers["T2"]["category"] == "Other"  # invalid name -> Other
    assert invalid == 2  # one invalid name + one missing ticket


def test_prompt_contains_every_ticket():
    batch = [{"id": "T1", "text": "hello"}, {"id": "T2", "text": "world"}]
    for version in ["v1", "v2"]:
        prompt = build_prompt(version, batch)
        assert '"T1"' in prompt and '"T2"' in prompt


# ---------------------------------------------------------------- fake Gemini
class FakeModels:
    def __init__(self):
        self.calls = 0

    def generate_content(self, model, contents, config):
        self.calls += 1
        ids = [item["id"] for item in json.loads(contents.split("Tickets:")[-1])]
        answer = [{"id": i, "category": "Delivery & Shipping", "confidence": "high"} for i in ids]
        usage = SimpleNamespace(prompt_token_count=1000, candidates_token_count=100,
                                thoughts_token_count=0)
        return SimpleNamespace(text=json.dumps(answer), usage_metadata=usage)


def test_classifier_batches_caches_and_counts_cost(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    fake = SimpleNamespace(models=FakeModels())
    sample = pd.DataFrame({"ticket_id": [f"T{i}" for i in range(45)],
                           "channel": "chat", "customer_message": "where is my parcel",
                           "agent_notes": ""})

    first = GeminiClassifier(prompt_version="v2", mode="intake", model="fake", client=fake)
    labels = first.classify(sample)
    assert len(labels) == 45
    assert fake.models.calls == 3  # 45 tickets / 20 per call
    assert first.usage.cost_usd() > 0

    second = GeminiClassifier(prompt_version="v2", mode="intake", model="fake", client=fake)
    second.classify(sample)
    assert fake.models.calls == 3  # everything came from cache; no new calls
