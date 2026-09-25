"""The numbers behind the memo. Pure pandas, no API calls.

Every function takes the cleaned tickets from data.load_tickets() and returns a
small DataFrame or dict, so results are easy to print, test and chart.
"""
import pandas as pd

from . import config
from .taxonomy import BILLING, LOGISTICS, OWNER_GROUPS, TEAM_TO_GROUP

# Costs are annualised over the most recent 12 months in the data.
LAST_12_MONTHS_START = "2025-07-01"


def last_12_months(tickets: pd.DataFrame) -> pd.DataFrame:
    return tickets[tickets["created_at"] >= LAST_12_MONTHS_START]


def team_share(tickets: pd.DataFrame) -> pd.DataFrame:
    """Share of tickets per owner group: by the bot's routing vs by who did the work."""
    by_tag = tickets["assigned_group"].value_counts(normalize=True)
    by_work = tickets["resolving_group"].value_counts(normalize=True)
    table = pd.DataFrame({"share_by_bot_tag": by_tag, "share_by_resolving_team": by_work})
    return table.reindex(OWNER_GROUPS).round(3)


def workload_per_agent(tickets: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    """Tickets resolved per agent per month, last 6 months, by helpdesk team.

    Policy §6: Tier 2 (Escalations & Warranty) is measured in days to resolve,
    not volume, so its row is shown but should not be compared on this metric.
    """
    recent = tickets[tickets["created_at"] >= "2026-01-01"]
    months = recent["month"].nunique()
    resolved = recent["resolving_team"].value_counts()
    headcount = agents.groupby("team")["agent_id"].nunique()
    table = pd.DataFrame({"agents": headcount, "tickets_per_month": resolved / months})
    table["tickets_per_agent_per_month"] = table["tickets_per_month"] / table["agents"]
    table["tier2_do_not_compare"] = table.index == "Escalations & Warranty"
    return table.sort_values("tickets_per_agent_per_month", ascending=False).round(1)


def billing_to_logistics_cost(tickets: pd.DataFrame) -> dict:
    """What the bot's main mistake costs a year: delivery tickets routed to Billing.

    Cost = one transfer per misroute (Rs 305, policy §4)
         + extra first-response breach credits (Rs 350, policy §3) above the breach
           rate of delivery tickets that went straight to Logistics.
    Agent time and customer churn are NOT counted, so this is a floor.
    """
    year = last_12_months(tickets)
    billing_queue = year[year["assigned_group"] == BILLING]
    misrouted = billing_queue[billing_queue["resolving_group"] == LOGISTICS]
    direct = year[(year["assigned_group"] == LOGISTICS) & (year["resolving_group"] == LOGISTICS)]

    transfer_cost = len(misrouted) * config.TRANSFER_COST_INR
    extra_breach_rate = misrouted["sla_breach"].mean() - direct["sla_breach"].mean()
    breach_cost = max(extra_breach_rate, 0) * len(misrouted) * config.BREACH_CREDIT_INR
    return {
        "billing_queue_tickets": len(billing_queue),
        "misrouted_to_logistics": len(misrouted),
        "misroute_rate": round(len(misrouted) / len(billing_queue), 3),
        "breach_rate_misrouted": round(misrouted["sla_breach"].mean(), 3),
        "breach_rate_direct_logistics": round(direct["sla_breach"].mean(), 3),
        "transfer_cost_inr": round(transfer_cost),
        "extra_breach_credit_inr": round(breach_cost),
        "total_inr_per_year": round(transfer_cost + breach_cost),
    }


def cross_team_handoffs(tickets: pd.DataFrame) -> dict:
    """Every ticket resolved by a different owner group than it was routed to,
    last 12 months, costed at one transfer each.

    This includes legitimate escalations (e.g. Frontline -> Warranty), so it is an
    upper bound on waste, not all of it avoidable. The headline uses only
    billing_to_logistics_cost(), which is unambiguous misrouting.
    """
    year = last_12_months(tickets)
    moved = year[year["misrouted"]]
    return {"handoff_tickets": len(moved),
            "handoff_rate": round(len(moved) / len(year), 3),
            "transfer_cost_inr_per_year": len(moved) * config.TRANSFER_COST_INR}


def scale_to_stated_volume(tickets: pd.DataFrame, rupees: float) -> dict:
    """The export averages far fewer tickets than the ~650/week quoted for Vireo.
    If the export is a sample, rupee figures scale up by the same ratio."""
    year = last_12_months(tickets)
    weekly_in_export = len(year) / 52
    ratio = config.STATED_TICKETS_PER_WEEK / weekly_in_export
    return {"tickets_per_week_in_export": round(weekly_in_export),
            "stated_tickets_per_week": config.STATED_TICKETS_PER_WEEK,
            "scale_ratio": round(ratio, 2),
            "scaled_inr_per_year": round(rupees * ratio)}


def misroute_impact(tickets: pd.DataFrame) -> pd.DataFrame:
    """How a misroute changes the customer's experience (helpdesk era only,
    where resolution times are native IST and not reconstructed)."""
    helpdesk = tickets[tickets["source_system"] == "helpdesk"]
    return helpdesk.groupby("misrouted").agg(
        tickets=("ticket_id", "size"),
        median_resolution_hours=("resolution_hours", "median"),
        breach_rate=("sla_breach", "mean"),
        avg_csat=("csat_score", "mean"),  # blanks are excluded, per policy §8
    ).round(2)


def misroute_rate_by_quarter(tickets: pd.DataFrame) -> pd.Series:
    billing = tickets[tickets["assigned_group"] == BILLING]
    quarter = billing["created_at"].dt.to_period("Q").astype(str)
    return (billing["resolving_group"] == LOGISTICS).groupby(quarter).mean().round(3)


def monthly_counts(tickets: pd.DataFrame, column: str) -> pd.DataFrame:
    """Month x value table of ticket counts, for charts and CSV export."""
    return pd.crosstab(tickets["month"], tickets[column])


def agents_table() -> pd.DataFrame:
    return pd.read_csv(config.DATA_DIR / "agents.csv")


__all__ = ["team_share", "workload_per_agent", "billing_to_logistics_cost",
           "cross_team_handoffs", "scale_to_stated_volume", "misroute_impact", "misroute_rate_by_quarter",
           "monthly_counts", "agents_table", "TEAM_TO_GROUP"]
