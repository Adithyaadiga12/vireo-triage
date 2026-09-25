"""Static PNG charts for the memo. matplotlib only, no styling dependencies.

Colours follow one rule: Billing is blue and Logistics is orange everywhere,
every other team is grey, because the memo is about those two.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt
import pandas as pd

from .taxonomy import BILLING, CATEGORY_NAMES, LOGISTICS, OWNER_GROUPS

BLUE, ORANGE, GREY, INK, MUTED = "#2a78d6", "#eb6834", "#b5b3ad", "#0b0b0b", "#52514e"
TEAM_COLOURS = {BILLING: BLUE, LOGISTICS: ORANGE}


def _style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GREY)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)


def _spread(values: dict[str, float], min_gap: float) -> dict[str, float]:
    """Nudge end-of-line labels apart so they don't overlap."""
    placed, last = {}, None
    for name, value in sorted(values.items(), key=lambda kv: kv[1]):
        value = value if last is None else max(value, last + min_gap)
        placed[name], last = value, value
    return placed


def team_share_chart(share: pd.DataFrame, path: Path) -> None:
    """Share of tickets per team: what the bot's tags say vs who did the work."""
    fig, ax = plt.subplots(figsize=(8, 4.2))
    groups = share.index.tolist()
    y = range(len(groups))
    ax.barh([i + 0.2 for i in y], share["share_by_bot_tag"] * 100, height=0.38,
            color=GREY, label="By bot tag (what Priya's 22% is based on)")
    ax.barh([i - 0.2 for i in y], share["share_by_resolving_team"] * 100, height=0.38,
            color=[TEAM_COLOURS.get(g, MUTED) for g in groups],
            label="By team that actually resolved it")
    for i, g in enumerate(groups):
        ax.text(share.loc[g, "share_by_bot_tag"] * 100 + 0.5, i + 0.2,
                f"{share.loc[g, 'share_by_bot_tag']:.0%}", va="center", fontsize=9, color=MUTED)
        ax.text(share.loc[g, "share_by_resolving_team"] * 100 + 0.5, i - 0.2,
                f"{share.loc[g, 'share_by_resolving_team']:.0%}", va="center", fontsize=9,
                color=INK, fontweight="bold")
    ax.set_yticks(list(y), groups)
    ax.invert_yaxis()
    ax.set_xlabel("% of all tickets, Jan 2025 - Jun 2026", color=MUTED)
    ax.set_title("Logistics, not Billing, does the most work", loc="left",
                 fontsize=13, color=INK, fontweight="bold")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#e6e5e0", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def monthly_by_team_chart(by_tag: pd.DataFrame, by_work: pd.DataFrame, path: Path) -> None:
    """Two panels with the same y-axis: monthly tickets by bot routing vs by resolver."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    panels = [(axes[0], by_tag, "Routed by the bot"), (axes[1], by_work, "Resolved by")]
    for ax, table, title in panels:
        table = table.reindex(columns=OWNER_GROUPS, fill_value=0)
        months = table.index.tolist()
        label_y = _spread({g: table[g].iloc[-1] for g in OWNER_GROUPS},
                          min_gap=table.values.max() * 0.05)
        for group in OWNER_GROUPS:
            highlighted = group in TEAM_COLOURS
            ax.plot(months, table[group], color=TEAM_COLOURS.get(group, GREY),
                    linewidth=2.2 if highlighted else 1.2, zorder=3 if highlighted else 2)
            ax.text(len(months) - 0.6, label_y[group], group, fontsize=8,
                    va="center", color=TEAM_COLOURS.get(group, MUTED))
        ax.set_title(title, loc="left", fontsize=11, color=INK)
        ax.set_xticks(range(0, len(months), 3), [months[i] for i in range(0, len(months), 3)],
                      rotation=0)
        ax.set_xlim(-0.5, len(months) + 3)
        _style(ax)
    axes[0].set_ylabel("Tickets per month", color=MUTED)
    fig.suptitle("Monthly tickets by team: the bot's view vs the real workload",
                 x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def monthly_by_category_chart(by_tag: pd.DataFrame, by_model: pd.DataFrame,
                              model_name: str, path: Path) -> None:
    """Small multiples, one per category: bot tag (grey) vs re-categorised (blue).

    11 categories are too many colours for one chart, so each gets its own panel.
    """
    fig, axes = plt.subplots(3, 4, figsize=(14, 8), sharex=True)
    months = sorted(set(by_tag.index) | set(by_model.index))
    by_tag = by_tag.reindex(index=months, columns=CATEGORY_NAMES, fill_value=0)
    by_model = by_model.reindex(index=months, columns=CATEGORY_NAMES, fill_value=0)
    top = max(by_tag.values.max(), by_model.values.max()) * 1.1
    for ax, category in zip(axes.flat, CATEGORY_NAMES):
        ax.plot(range(len(months)), by_tag[category], color=GREY, linewidth=1.5, label="Bot tag")
        ax.plot(range(len(months)), by_model[category], color=BLUE, linewidth=2,
                label=model_name)
        ax.set_title(category, loc="left", fontsize=10, color=INK)
        ax.set_ylim(0, top)
        ax.set_xticks([0, len(months) - 1], [months[0], months[-1]])
        _style(ax)
    axes.flat[-1].axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    axes.flat[-1].legend(handles, labels, frameon=False, loc="center", fontsize=11)
    fig.suptitle("Monthly tickets by category (same y-axis in every panel)", x=0.01,
                 ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
