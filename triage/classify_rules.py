"""Keyword baseline classifier. No API key, no cost, runs anywhere.

It exists for two reasons:
1. The tool still produces a result on a machine with no Gemini key.
2. It is the bar the LLM has to beat; if Gemini can't beat keywords, don't pay for it.

Rules are checked in order and the first match wins. Order matters: delivery is
checked before billing, because "I paid but it never arrived" is a delivery problem.
That single ordering choice is the fix for the bot's main mistake.
"""
import re

RULES: list[tuple[str, list[str]]] = [
    # Returns first: "you picked up the item and my money hasn't come back" is a
    # returns refund, not a delivery or billing problem.
    ("Returns & Refunds", [
        r"\breturn", r"cancel", r"exchange", r"pick ?up", r"picked up", r"reverse",
        r"refund (was )?promised", r"refund not", r"refnd", r"still waiting for my refund",
        r"ordered by mistake", r"don'?t ship", r"stop (the|teh) shipment", r"packed the box",
    ]),
    # Delivery before billing: "I paid but it never arrived" is a delivery problem.
    ("Delivery & Shipping", [
        r"not (been |bene )?deliver", r"never (arrived|came|received)", r"nothing in hand",
        r"haven'?t received", r"not received", r"didn'?t (get|receive)", r"track(ing)?",
        r"courier", r"shipment", r"shipped", r"marked (as )?delivered", r"\bawb\b",
        r"out for delivery", r"wrong (item|address)", r"got something else", r"parcel",
        r"package", r"doorstep", r"still waiting for", r"arrived damaged", r"box was crushed",
        r"received damaged", r"processing",
    ]),
    ("Warranty & Repair", [
        r"warranty", r"repair", r"\brma", r"sent the unit", r"service cent",
        r"stopped working", r"not (turning|switching) on", r"water", r"cracked", r"\bdoa\b",
        r"does not wake", r"went dark", r"dead",
    ]),
    # "I want my money back" is tacked onto many complaints, so generic money words
    # are NOT billing signals. Only payment-mechanics words are.
    ("Billing & Payments", [
        r"deduct", r"debited", r"charged", r"char?ged two", r"twice", r"double", r"payment",
        r"\bupi\b", r"invoice", r"\bbill\b", r"\bgst", r"\bemi\b", r"coupon", r"price",
        r"no order (id|confirmation)", r"order id", r"txn", r"transaction",
    ]),
    ("Charging & Battery", [r"charg", r"battery", r"drain", r"percent", r"power"]),
    ("Connectivity", [r"pair", r"bluetooth", r"connect", r"disconnect", r"cutting out", r"wi-?fi"]),
    ("Audio Quality", [r"sound", r"audio", r"\bmic", r"noise", r"crackl", r"volume", r"\banc\b",
                       r"meetings", r"muffled"]),
    ("App & Firmware", [r"\bapp\b", r"firmware", r"update", r"white screen", r"crash"]),
    ("Account & Login", [r"login", r"log in", r"\botp\b", r"password", r"account"]),
    ("Product Enquiry", [r"compatib", r"does it", r"will it", r"can i", r"feature", r"stock",
                         r"how (do|to)"]),
]

_COMPILED = [(category, [re.compile(p) for p in patterns]) for category, patterns in RULES]


def classify_text(text: str) -> str:
    text = (text or "").lower()
    for category, patterns in _COMPILED:
        if any(p.search(text) for p in patterns):
            return category
    return "Other"


def classify_messages(messages: list[str]) -> list[str]:
    return [classify_text(m) for m in messages]
