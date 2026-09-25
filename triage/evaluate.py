"""How we know the classifier works, and how often it doesn't.

Two yardsticks, because neither is perfect alone:

1. Resolving team (automatic, every ticket). The team whose agent actually closed
   the ticket is a strong, human-made signal of who owned the problem. Weakness:
   legitimate escalations (Frontline -> Warranty) look like "wrong" answers.
2. Hand labels (manual, 100 tickets). You read the ticket and write the category.
   Slower, but it is the real ground truth. `make-labelling-sheet` creates the file;
   it deliberately hides every prediction so you are not nudged.

Everything is compared on the SAME fixed random sample, so the bot tag, the keyword
baseline and each Gemini prompt version are scored side by side.
"""
import pandas as pd

from . import config
from .taxonomy import BILLING, OWNER_GROUPS, owner_group

SAMPLE_SEED = 42
HAND_LABEL_FILE = config.OUTPUT_DIR / "hand_labels.csv"


def eval_sample(tickets: pd.DataFrame, size: int = 300) -> pd.DataFrame:
    """Fixed random sample (same seed every time) so results are comparable."""
    return tickets.sample(n=min(size, len(tickets)), random_state=SAMPLE_SEED)


def group_accuracy(predicted_groups: pd.Series, true_groups: pd.Series) -> dict:
    correct = predicted_groups.values == true_groups.values
    return {"n": len(correct), "accuracy": round(correct.mean(), 3),
            "errors": int((~correct).sum())}


def per_group_recall(predicted: pd.Series, truth: pd.Series) -> pd.Series:
    """For tickets that truly belong to each team, how many did we send there?"""
    frame = pd.DataFrame({"pred": predicted.values, "truth": truth.values})
    return (frame.assign(ok=frame["pred"] == frame["truth"])
                 .groupby("truth")["ok"].mean().reindex(OWNER_GROUPS).round(3))


def confusion(predicted: pd.Series, truth: pd.Series) -> pd.DataFrame:
    return pd.crosstab(pd.Series(truth.values, name="actual (resolving team)"),
                       pd.Series(predicted.values, name="predicted"))


def scorecard(sample: pd.DataFrame, predictions: dict[str, pd.Series]) -> pd.DataFrame:
    """One row per method: overall accuracy and recall per owner group.

    `predictions` maps a method name to predicted owner groups aligned to `sample`.
    """
    truth = sample["resolving_group"]
    rows = {}
    for name, predicted in predictions.items():
        row = group_accuracy(predicted, truth)
        row.update({f"recall_{g}": v for g, v in per_group_recall(predicted, truth).items()})
        # The number that matters for headcount: of tickets sent to Billing,
        # how many really were Billing's?
        sent_to_billing = predicted.values == BILLING
        row["billing_queue_precision"] = round(
            (truth.values[sent_to_billing] == BILLING).mean(), 3) if sent_to_billing.any() else None
        rows[name] = row
    return pd.DataFrame(rows).T


def write_labelling_sheet(sample: pd.DataFrame, size: int = 100) -> None:
    """A CSV for hand labelling. No predictions shown, to avoid anchoring."""
    if HAND_LABEL_FILE.exists():
        print(f"{HAND_LABEL_FILE} already exists; not overwriting your labels.")
        return
    sheet = sample.head(size)[["ticket_id", "channel", "customer_message", "agent_notes"]].copy()
    sheet["human_category"] = ""
    sheet["comment"] = ""
    HAND_LABEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    sheet.to_csv(HAND_LABEL_FILE, index=False)
    print(f"Wrote {len(sheet)} tickets to {HAND_LABEL_FILE}. Fill in 'human_category' "
          f"with one of the category names in triage/taxonomy.py.")


def score_against_hand_labels(predictions: dict[str, pd.DataFrame]) -> pd.DataFrame | None:
    """Category-level and team-level accuracy against your hand labels.

    `predictions` maps method name -> DataFrame(ticket_id, category).
    """
    if not HAND_LABEL_FILE.exists():
        return None
    labels = pd.read_csv(HAND_LABEL_FILE).dropna(subset=["human_category"])
    labels = labels[labels["human_category"].str.strip() != ""]
    if labels.empty:
        return None
    rows = {}
    for name, pred in predictions.items():
        joined = labels.merge(pred[["ticket_id", "category"]], on="ticket_id")
        if joined.empty:
            continue
        same_category = joined["category"] == joined["human_category"].str.strip()
        same_group = joined["category"].map(owner_group) == joined["human_category"].map(owner_group)
        rows[name] = {"n": len(joined), "category_accuracy": round(same_category.mean(), 3),
                      "team_accuracy": round(same_group.mean(), 3)}
    return pd.DataFrame(rows).T
