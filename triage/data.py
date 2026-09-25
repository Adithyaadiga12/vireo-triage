"""Load the data pack and fix the known problems in it, in one place.

Each fix is a small named function so it can be read, tested and switched off.
`load_tickets()` returns one clean DataFrame plus a log of what was changed.
"""
from dataclasses import dataclass, field

import pandas as pd

from . import config
from .taxonomy import TEAM_TO_GROUP


@dataclass
class CleaningLog:
    """Human-readable record of every change made to the raw export."""
    notes: list[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        self.notes.append(message)

    def __str__(self) -> str:
        return "\n".join(f"- {n}" for n in self.notes)


def read_raw_tickets() -> pd.DataFrame:
    tickets = pd.read_csv(config.DATA_DIR / "tickets.csv")
    for column in ["created_at", "first_response_at", "resolved_at"]:
        tickets[column] = pd.to_datetime(tickets[column])
    return tickets


def read_agents() -> pd.DataFrame:
    agents = pd.read_csv(config.DATA_DIR / "agents.csv", parse_dates=["from_date", "to_date"])
    return agents


def fix_legacy_timezone(tickets: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    """Policy §9: legacy resolved_at is UTC; shift it to IST like every other timestamp."""
    legacy = tickets["source_system"] == config.LEGACY_SYSTEM
    before = (tickets["resolved_at"] < tickets["created_at"]).sum()
    tickets.loc[legacy, "resolved_at"] += pd.Timedelta(config.UTC_TO_IST)
    after = (tickets["resolved_at"] < tickets["created_at"]).sum()
    log.add(f"Shifted legacy resolved_at by +5:30 (UTC->IST). Tickets resolved before "
            f"they were created: {before} -> {after}.")
    return tickets


def keep_reporting_window(tickets: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    in_window = tickets["created_at"].between(config.WINDOW_START, config.WINDOW_END,
                                              inclusive="left")
    log.add(f"Dropped {(~in_window).sum()} tickets created outside "
            f"{config.WINDOW_START} to {config.WINDOW_END} (brief says Jan 2025-Jun 2026).")
    return tickets[in_window].copy()


def attach_resolving_team(tickets: pd.DataFrame, agents: pd.DataFrame,
                          log: CleaningLog) -> pd.DataFrame:
    """Team of the agent who resolved the ticket, on the ticket's creation date.

    The roster is one row per assignment (policy §7), so we match on date range,
    not just agent_id. Joined on agent_id because two agents share a name.
    """
    merged = tickets.merge(agents[["agent_id", "team", "from_date", "to_date"]],
                           on="agent_id", how="left")
    active = (merged["created_at"] >= merged["from_date"]) & (
        merged["to_date"].isna() | (merged["created_at"] <= merged["to_date"]))
    # If an agent has no roster row covering the date, keep their nearest row
    # rather than drop the ticket; count how often that happens.
    merged["_active"] = active
    merged = (merged.sort_values("_active", ascending=False)
                    .drop_duplicates("ticket_id")
                    .sort_values("created_at"))
    log.add(f"Resolving team taken from roster by agent_id and date. "
            f"{(~merged['_active']).sum()} tickets had no roster row covering their date "
            f"(nearest row used). Roster rows per agent: max "
            f"{agents['agent_id'].value_counts().max()}.")
    merged = merged.rename(columns={"team": "resolving_team"})
    return merged.drop(columns=["from_date", "to_date", "_active"])


def add_derived_columns(tickets: pd.DataFrame) -> pd.DataFrame:
    t = tickets
    t["month"] = t["created_at"].dt.to_period("M").astype(str)
    t["assigned_group"] = t["assigned_team"].map(TEAM_TO_GROUP)
    t["resolving_group"] = t["resolving_team"].map(TEAM_TO_GROUP)
    # A misroute = first routed to one owner group, resolved by another.
    t["misrouted"] = t["assigned_group"] != t["resolving_group"]
    first_response_hours = (t["first_response_at"] - t["created_at"]).dt.total_seconds() / 3600
    t["resolution_hours"] = (t["resolved_at"] - t["created_at"]).dt.total_seconds() / 3600
    target = t["channel"].map(config.FIRST_RESPONSE_TARGET_HOURS)
    t["sla_breach"] = first_response_hours > target
    return t


def load_tickets(verbose: bool = False) -> tuple[pd.DataFrame, CleaningLog]:
    """The single entry point everything else uses."""
    log = CleaningLog()
    tickets = read_raw_tickets()
    log.add(f"Read {len(tickets)} tickets.")
    tickets = fix_legacy_timezone(tickets, log)
    tickets = keep_reporting_window(tickets, log)
    tickets = attach_resolving_team(tickets, read_agents(), log)
    tickets = add_derived_columns(tickets)
    log.add("transfers is blank (not zero) on legacy rows, so routing is judged by "
            "assigned team vs resolving team instead.")
    if verbose:
        print(log)
    return tickets.reset_index(drop=True), log
