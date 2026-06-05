from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "design_strategies"
OUT.mkdir(parents=True, exist_ok=True)

RAW_LOG = ROOT / "data" / "aladdin_all_projects_design - Cleaned+Added_projects_with_name_class.csv"
ITER = ROOT / "outputs" / "rq2_profiles_no_colonial" / "iteration_level_human_ai_reasoning_codes_no_colonial.csv"
PROFILES = ROOT / "outputs" / "rq2_profiles_no_colonial" / "student_level_profile_features_no_colonial_renamed.csv"
ENA = ROOT / "outputs" / "rq_ena" / "ena_student_network_vectors.csv"
ASSESS = ROOT / "outputs" / "rq_ena_conceptual_understanding" / "ena_assessment_matched_students.csv"
AGENCY = ROOT / "outputs" / "rq3_agency_final" / "agency_survey_merged_with_rq2_profiles.csv"


PROFILE_ORDER = [
    "AI-guided technical optimizers",
    "Technical prompt composers with limited uptake",
    "Visual-spatial generators",
    "Off-task but technically iterative designers",
    "Off-task weak-coupling explorers",
]

STRATEGY_ORDER = [
    "Cumulative incremental",
    "Site exploration",
    "Detail-descriptive",
    "Parameter-driven",
    "Performance-oriented",
    "Off-task / imaginative exploratory",
    "Mixed / low-evidence",
]

PROMPT_STATE_ORDER = [
    "Parameter",
    "Performance",
    "Site",
    "Detail",
    "Off-task",
    "General",
]


PARAMETER_RE = re.compile(
    r"\b(r[- ]?value|u[- ]?value|shgc|cop|coefficient of performance|setpoint|thermostat|"
    r"pv model|pv|photovoltaic|eaves?|overhang|glass tint|glazing|insulation value|"
    r"heating setpoint|cooling setpoint|orientation|south[- ]?facing|north[- ]?facing)\b|#[0-9a-f]{6}",
    re.I,
)
PERFORMANCE_OUTCOME_RE = re.compile(
    r"\b(net\s*zero|net\s*0|zero\s*energy|no\s*power|remove all objects that consume energy|"
    r"make (?:it |the )?net\s*0|make (?:it |the )?zero|save energy|reduce energy|"
    r"most efficient|energy efficient|sustainable)\b",
    re.I,
)
VISUAL_DETAIL_RE = re.compile(
    r"\b(color|colour|white|brown|pink|blue|green|red|black|yellow|modern|style|big|small|"
    r"large|tiny|luxurious|cozy|window|windows|door|doors|roof|wall|walls|room|rooms|floor|"
    r"foundation|garage|porch|pool|mansion|yard|garden|tree|trees|stairs|balcony|fence)\b",
    re.I,
)
OFFTASK_RE = re.compile(
    r"\b(barbershop|castle|minecraft|mcdonald|restaurant|school|store|shop|fortnite|funny|"
    r"random|car|trailer|twin towers|epstein|temple|dih|freaky|freestyle|generic house|"
    r"luxurious house)\b|[😜]",
    re.I,
)
LOCATION_PROMPT_RE = re.compile(
    r"\b(north carolina|nc|south carolina|sc|nevada|arizona|missouri|alaska|hawaii|"
    r"california|texas|florida|new york|las vegas|charleston|scottsdale|joplin|garner|"
    r"benson|raleigh|durham|willow spring|netherlands|switzerland|germany|greenland|"
    r"africa|mexico|canada|china|japan|desert|beach|mountain|cold|hot climate|snow)\b",
    re.I,
)
TOKEN_RE = re.compile(r"[a-z0-9#]+", re.I)


def to_num(s):
    return pd.to_numeric(s, errors="coerce")


def norm_text(s: object) -> str:
    if pd.isna(s):
        return ""
    return str(s).strip().lower()


def token_set(s: str) -> set[str]:
    toks = {t.lower() for t in TOKEN_RE.findall(s)}
    stop = {
        "generate",
        "make",
        "a",
        "an",
        "the",
        "house",
        "style",
        "colonial",
        "and",
        "with",
        "in",
        "of",
        "to",
        "for",
        "it",
        "add",
    }
    return {t for t in toks if t not in stop and len(t) > 1}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def safe_json_address(raw: object) -> str:
    if pd.isna(raw) or not str(raw).strip():
        return ""
    try:
        data = json.loads(str(raw))
        return str(data.get("address", "")).strip().lower()
    except Exception:
        return ""


def load_raw_addresses() -> pd.DataFrame:
    raw = pd.read_csv(RAW_LOG)
    rows = []
    for _, r in raw.iterrows():
        for i in range(1, 20):
            prompt = r.get(f"iteration_{i}_prompt", "")
            if pd.isna(prompt) or not str(prompt).strip():
                continue
            rows.append(
                {
                    "Name": r.get("Name", ""),
                    "student_id_key": norm_text(r.get("Name", "")),
                    "iteration": i,
                    "raw_address": safe_json_address(r.get(f"iteration_{i}_raw_world", "")),
                }
            )
    return pd.DataFrame(rows)


def classify_prompt_state(row: pd.Series) -> str:
    prompt = norm_text(row["prompt"])
    if row["prompt_offtask_binary"] == 1 or OFFTASK_RE.search(prompt):
        return "Off-task"
    if PARAMETER_RE.search(prompt):
        return "Parameter"
    if PERFORMANCE_OUTCOME_RE.search(prompt):
        return "Performance"
    if LOCATION_PROMPT_RE.search(prompt) or row.get("has_site_prompt", 0) == 1:
        return "Site"
    if row["prompt_visual_spatial_binary"] == 1 or VISUAL_DETAIL_RE.search(prompt):
        return "Detail"
    return "General"


def assign_primary_strategy(r: pd.Series) -> str:
    n = r["n_prompts"]
    if r["offtask_rate"] >= 0.20 or r["offtask_count"] >= 2:
        return "Off-task / imaginative exploratory"
    if r["performance_outcome_rate"] >= 0.15 or r["performance_outcome_count"] >= 2:
        return "Performance-oriented"
    if r["parameter_specific_rate"] >= 0.20 or r["parameter_specific_count"] >= 2:
        return "Parameter-driven"
    if r["distinct_site_count"] >= 3 or r["site_shift_count"] >= 2:
        return "Site exploration"
    if n >= 3 and r["mean_prompt_jaccard"] >= 0.42 and r["mean_added_token_count"] >= 1.0:
        return "Cumulative incremental"
    if r["visual_detail_rate"] >= 0.45 and r["parameter_specific_rate"] < 0.15:
        return "Detail-descriptive"
    return "Mixed / low-evidence"


def add_bar_labels(ax, fmt="{:.0f}"):
    return None


def esc(s: object) -> str:
    text = "" if pd.isna(s) else str(s)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_svg(path: Path, width: int, height: int, body: str) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
text {{ font-family: Arial, Helvetica, sans-serif; fill: #1f2933; }}
.title {{ font-size: 18px; font-weight: 700; }}
.axis {{ font-size: 12px; fill: #36454f; }}
.small {{ font-size: 10px; fill: #4b5563; }}
.tick {{ stroke: #d0d7de; stroke-width: 1; }}
.frame {{ fill: #ffffff; stroke: #d0d7de; stroke-width: 1; }}
</style>
<rect width="100%" height="100%" fill="#ffffff"/>
{body}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def wrap_label(text: str, max_chars: int = 22) -> list[str]:
    words = str(text).split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:3]


def interp_color(t: float, c0=(247, 251, 255), c1=(8, 81, 156)) -> str:
    t = max(0, min(1, float(t)))
    rgb = tuple(round(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))
    return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"


def chi_square_basic(table: pd.DataFrame) -> tuple[float, int, float]:
    obs = table.to_numpy(dtype=float)
    n = obs.sum()
    row = obs.sum(axis=1, keepdims=True)
    col = obs.sum(axis=0, keepdims=True)
    exp = row @ col / n if n else np.zeros_like(obs)
    with np.errstate(divide="ignore", invalid="ignore"):
        chi = np.nansum((obs - exp) ** 2 / exp)
    dof = (obs.shape[0] - 1) * (obs.shape[1] - 1)
    v = math.sqrt(chi / (n * (min(obs.shape) - 1))) if n and min(obs.shape) > 1 else np.nan
    return float(chi), int(dof), float(v)


def spearman_basic(x: pd.Series, y: pd.Series) -> float:
    xr = x.rank()
    yr = y.rank()
    return float(xr.corr(yr))


def main() -> None:
    iter_df = pd.read_csv(ITER)
    profiles = pd.read_csv(PROFILES)
    addrs = load_raw_addresses()

    for c in [
        "student_id",
        "iteration",
        "prompt_words",
        "prompt_technical_binary",
        "prompt_performance_binary",
        "prompt_visual_spatial_binary",
        "prompt_offtask_binary",
    ]:
        iter_df[c] = to_num(iter_df[c]).fillna(0)
    iter_df["student_id"] = iter_df["student_id"].astype(int)
    iter_df["iteration"] = iter_df["iteration"].astype(int)
    iter_df["student_id_key"] = iter_df["Name"].map(norm_text)
    iter_df = iter_df.merge(
        addrs[["student_id_key", "iteration", "raw_address"]],
        on=["student_id_key", "iteration"],
        how="left",
    )
    iter_df["prompt_norm"] = iter_df["prompt"].map(norm_text)
    iter_df["has_parameter_specific"] = iter_df["prompt_norm"].map(lambda x: int(bool(PARAMETER_RE.search(x))))
    iter_df["has_performance_outcome"] = iter_df["prompt_norm"].map(lambda x: int(bool(PERFORMANCE_OUTCOME_RE.search(x))))
    iter_df["has_visual_detail"] = iter_df["prompt_norm"].map(lambda x: int(bool(VISUAL_DETAIL_RE.search(x))))
    iter_df["has_site_prompt"] = iter_df["prompt_norm"].map(lambda x: int(bool(LOCATION_PROMPT_RE.search(x))))
    iter_df["has_offtask_strategy"] = iter_df["prompt_norm"].map(lambda x: int(bool(OFFTASK_RE.search(x))))
    iter_df["prompt_state"] = iter_df.apply(classify_prompt_state, axis=1)

    strategy_rows = []
    transition_rows = []
    for sid, g in iter_df.sort_values(["student_id", "iteration"]).groupby("student_id"):
        g = g.copy()
        prompt_tokens = [token_set(x) for x in g["prompt_norm"]]
        jaccards = []
        added_counts = []
        for idx in range(1, len(prompt_tokens)):
            prev, cur = prompt_tokens[idx - 1], prompt_tokens[idx]
            sim = jaccard(prev, cur)
            added = len(cur - prev)
            jaccards.append(sim)
            added_counts.append(added)
            transition_rows.append(
                {
                    "student_id": sid,
                    "Name": g.iloc[idx]["Name"],
                    "transition": f"{int(g.iloc[idx-1]['iteration'])}->{int(g.iloc[idx]['iteration'])}",
                    "prompt_jaccard": sim,
                    "added_token_count": added,
                }
            )
        addresses = [
            a
            for a in g["raw_address"].dropna().map(lambda x: str(x).strip().lower())
            if a and a not in {"nan", "none"}
        ]
        distinct_addresses = sorted(set(addresses))
        site_shift_count = sum(1 for a, b in zip(addresses, addresses[1:]) if a != b)
        row = {
            "student_id": sid,
            "Name": g["Name"].iloc[0],
            "class": g["class"].iloc[0],
            "n_prompts": len(g),
            "parameter_specific_count": int(g["has_parameter_specific"].sum()),
            "parameter_specific_rate": float(g["has_parameter_specific"].mean()),
            "performance_outcome_count": int(g["has_performance_outcome"].sum()),
            "performance_outcome_rate": float(g["has_performance_outcome"].mean()),
            "visual_detail_count": int(g["has_visual_detail"].sum()),
            "visual_detail_rate": float(g["has_visual_detail"].mean()),
            "site_prompt_count": int(g["has_site_prompt"].sum()),
            "site_prompt_rate": float(g["has_site_prompt"].mean()),
            "offtask_count": int(np.maximum(g["has_offtask_strategy"], g["prompt_offtask_binary"]).sum()),
            "offtask_rate": float(np.maximum(g["has_offtask_strategy"], g["prompt_offtask_binary"]).mean()),
            "distinct_site_count": len(distinct_addresses),
            "site_shift_count": site_shift_count,
            "mean_prompt_jaccard": float(np.nanmean(jaccards)) if jaccards else 0.0,
            "mean_added_token_count": float(np.nanmean(added_counts)) if added_counts else 0.0,
            "distinct_sites": "; ".join(distinct_addresses[:10]),
        }
        strategy_rows.append(row)

    strategies = pd.DataFrame(strategy_rows)
    strategies["primary_design_strategy"] = strategies.apply(assign_primary_strategy, axis=1)

    profiles["student_id"] = profiles["student_id"].astype(int)
    merged = strategies.merge(
        profiles[
            [
                "student_id",
                "designer_profile_clean",
                "technical_parameter_density",
                "performance_goal_density",
                "AI_reasoning_uptake_rate",
                "transformative_uptake_rate",
                "off_task_ratio",
                "net_change",
                "n_iterations",
            ]
        ],
        on="student_id",
        how="left",
    ).rename(columns={"designer_profile_clean": "designer_profile"})

    # Assessment and agency joins.
    assess = pd.read_csv(ASSESS)
    assess["student_id"] = to_num(assess["student_id"]).astype("Int64")
    assess_small = assess[["student_id", "pre", "post", "gain", "ENA_dim1", "ENA_dim2"]].copy()
    for c in ["pre", "post", "gain", "ENA_dim1", "ENA_dim2"]:
        assess_small[c] = to_num(assess_small[c])
    merged = merged.merge(assess_small, on="student_id", how="left", suffixes=("", "_assess"))

    ena = pd.read_csv(ENA)
    ena["student_id"] = to_num(ena["student_id"]).astype(int)
    ena_cols = [
        "student_id",
        "ENA_dim1",
        "ENA_dim2",
        "node_GoalPrompt_rate",
        "node_TechPrompt_rate",
        "node_VisualSpatial_rate",
        "node_AIClimate_rate",
        "node_OffTask_rate",
    ]
    merged = merged.merge(ena[ena_cols], on="student_id", how="left", suffixes=("", "_full"))

    agency = pd.read_csv(AGENCY)
    agency["student_id"] = to_num(agency["profile_student_id"]).astype("Int64")
    agency_dims = [
        "self_cognition",
        "goal_setting",
        "self_adjustment",
        "self_reflection",
        "selective_action",
        "responsible_action",
        "participative_action",
        "motivation",
        "self_efficacy",
        "overall_agency",
    ]
    agency_small = agency[["student_id", "Your Name", *agency_dims]].copy()
    for c in agency_dims:
        agency_small[c] = to_num(agency_small[c])
    merged = merged.merge(agency_small, on="student_id", how="left")

    transitions = pd.DataFrame(transition_rows)
    iter_out = iter_df[
        [
            "student_id",
            "Name",
            "class",
            "iteration",
            "prompt",
            "prompt_state",
            "has_parameter_specific",
            "has_performance_outcome",
            "has_visual_detail",
            "has_site_prompt",
            "has_offtask_strategy",
            "raw_address",
        ]
    ].merge(strategies[["student_id", "primary_design_strategy"]], on="student_id", how="left")

    # Summary tables.
    strategy_summary = (
        merged.groupby("primary_design_strategy", dropna=False)
        .agg(
            n=("student_id", "count"),
            mean_prompts=("n_prompts", "mean"),
            mean_parameter_rate=("parameter_specific_rate", "mean"),
            mean_performance_rate=("performance_outcome_rate", "mean"),
            mean_site_count=("distinct_site_count", "mean"),
            mean_visual_rate=("visual_detail_rate", "mean"),
            mean_offtask_rate=("offtask_rate", "mean"),
            mean_jaccard=("mean_prompt_jaccard", "mean"),
            mean_added_tokens=("mean_added_token_count", "mean"),
            mean_uptake=("AI_reasoning_uptake_rate", "mean"),
            mean_transformative_uptake=("transformative_uptake_rate", "mean"),
            mean_net_change=("net_change", "mean"),
            mean_gain=("gain", "mean"),
            matched_gain_n=("gain", "count"),
            mean_overall_agency=("overall_agency", "mean"),
            matched_agency_n=("overall_agency", "count"),
            mean_ENA_dim1=("ENA_dim1_full", "mean"),
            mean_ENA_dim2=("ENA_dim2_full", "mean"),
        )
        .reindex(STRATEGY_ORDER)
        .dropna(how="all")
        .reset_index()
    )

    crosstab = pd.crosstab(
        pd.Categorical(merged["primary_design_strategy"], categories=STRATEGY_ORDER, ordered=True),
        pd.Categorical(merged["designer_profile"], categories=PROFILE_ORDER, ordered=True),
        dropna=False,
    )
    crosstab.index.name = "primary_design_strategy"
    crosstab.columns.name = "designer_profile"
    crosstab = crosstab.loc[(crosstab.sum(axis=1) > 0), (crosstab.sum(axis=0) > 0)]

    crosstab_pct = crosstab.div(crosstab.sum(axis=1), axis=0).fillna(0)

    stats_rows = []
    if crosstab.shape[0] > 1 and crosstab.shape[1] > 1:
        chi2, dof, cramers_v = chi_square_basic(crosstab)
        stats_rows.append(
            {
                "comparison": "design_strategy_by_designer_profile",
                "test": "Chi-square",
                "statistic": chi2,
                "df": dof,
                "p": "",
                "effect_size": cramers_v,
                "effect_size_label": "Cramer's V",
                "note": "Exploratory; p omitted because scipy is unavailable in the bundled runtime.",
            }
        )

    corr_vars = [
        "parameter_specific_rate",
        "performance_outcome_rate",
        "visual_detail_rate",
        "distinct_site_count",
        "offtask_rate",
        "mean_prompt_jaccard",
    ]
    for x in corr_vars:
        for y in ["gain", "overall_agency", "goal_setting", "self_adjustment", "ENA_dim1_full"]:
            tmp = merged[[x, y]].dropna()
            if len(tmp) >= 6 and tmp[x].nunique() > 1 and tmp[y].nunique() > 1:
                rho = spearman_basic(tmp[x], tmp[y])
                stats_rows.append(
                    {
                        "comparison": f"{x}_with_{y}",
                        "test": "Spearman",
                        "statistic": rho,
                        "df": "",
                        "p": "",
                        "effect_size": rho,
                        "effect_size_label": "rho",
                        "note": f"n={len(tmp)}; p omitted because scipy is unavailable in the bundled runtime.",
                    }
                )

    learning_summary = (
        merged.dropna(subset=["gain"])
        .groupby("primary_design_strategy")
        .agg(n=("student_id", "count"), pre_mean=("pre", "mean"), post_mean=("post", "mean"), gain_mean=("gain", "mean"), gain_sd=("gain", "std"))
        .reindex(STRATEGY_ORDER)
        .dropna(how="all")
        .reset_index()
    )
    agency_summary = (
        merged.dropna(subset=["overall_agency"])
        .groupby("primary_design_strategy")[agency_dims]
        .agg(["count", "mean", "std"])
    )
    ena_summary = (
        merged.groupby("primary_design_strategy")
        .agg(n=("student_id", "count"), ENA_dim1_mean=("ENA_dim1_full", "mean"), ENA_dim2_mean=("ENA_dim2_full", "mean"))
        .reindex(STRATEGY_ORDER)
        .dropna(how="all")
        .reset_index()
    )

    # Save tables.
    iter_out.to_csv(OUT / "prompt_level_strategy_codes.csv", index=False)
    transitions.to_csv(OUT / "prompt_transition_similarity.csv", index=False)
    merged.to_csv(OUT / "student_design_strategy_codes.csv", index=False)
    strategy_summary.to_csv(OUT / "strategy_summary.csv", index=False)
    crosstab.to_csv(OUT / "strategy_by_designer_profile_counts.csv")
    crosstab_pct.to_csv(OUT / "strategy_by_designer_profile_row_percent.csv")
    pd.DataFrame(stats_rows).to_csv(OUT / "strategy_association_statistics.csv", index=False)
    learning_summary.to_csv(OUT / "strategy_learning_summary.csv", index=False)
    agency_summary.to_csv(OUT / "strategy_agency_summary.csv")
    ena_summary.to_csv(OUT / "strategy_ena_centroids.csv", index=False)

    # Figure 1: strategy distribution.
    dist = merged["primary_design_strategy"].value_counts().reindex(STRATEGY_ORDER).dropna()
    width, height = 920, 470
    left, top, bar_h, gap = 280, 70, 34, 18
    max_v = max(dist.values) if len(dist) else 1
    scale = 540 / max_v
    body = [f'<text x="30" y="32" class="title">Prompt-based design strategy distribution</text>']
    for i, (label, v) in enumerate(dist.items()):
        y = top + i * (bar_h + gap)
        body.append(f'<text x="{left-12}" y="{y+22}" text-anchor="end" class="axis">{esc(label)}</text>')
        body.append(f'<rect x="{left}" y="{y}" width="{v*scale:.1f}" height="{bar_h}" rx="3" fill="#3C6E71"/>')
        body.append(f'<text x="{left + v*scale + 8:.1f}" y="{y+22}" class="axis">{int(v)}</text>')
    body.append(f'<text x="{left}" y="{height-28}" class="axis">Number of students/projects</text>')
    write_svg(OUT / "fig1_strategy_distribution.svg", width, height, "\n".join(body))

    # Figure 2: strategy x profile heatmap.
    cell_w, cell_h = 155, 58
    width = 260 + cell_w * crosstab.shape[1] + 30
    height = 150 + cell_h * crosstab.shape[0] + 30
    left, top = 250, 115
    body = ['<text x="28" y="34" class="title">Design strategies compared with model-derived designer profiles</text>']
    for j, col in enumerate(crosstab.columns):
        x = left + j * cell_w + cell_w / 2
        for k, line in enumerate(wrap_label(col, 18)):
            body.append(f'<text x="{x}" y="{72 + k*13}" text-anchor="middle" class="small">{esc(line)}</text>')
    for i, idx in enumerate(crosstab.index):
        y = top + i * cell_h
        body.append(f'<text x="{left-12}" y="{y+34}" text-anchor="end" class="axis">{esc(idx)}</text>')
        for j, col in enumerate(crosstab.columns):
            x = left + j * cell_w
            pct = float(crosstab_pct.loc[idx, col])
            count = int(crosstab.loc[idx, col])
            body.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{interp_color(pct)}" stroke="#ffffff"/>')
            body.append(f'<text x="{x+cell_w/2}" y="{y+25}" text-anchor="middle" class="axis">{count}</text>')
            body.append(f'<text x="{x+cell_w/2}" y="{y+43}" text-anchor="middle" class="small">{pct*100:.0f}%</text>')
    write_svg(OUT / "fig2_strategy_by_profile_heatmap.svg", width, height, "\n".join(body))

    # Figure 3: trajectory strip plot.
    strip_df = iter_out.copy()
    strip_df["strategy_order"] = strip_df["primary_design_strategy"].map({s: i for i, s in enumerate(STRATEGY_ORDER)})
    strip_df = strip_df.sort_values(["strategy_order", "student_id", "iteration"])
    students = strip_df[["student_id", "Name", "primary_design_strategy"]].drop_duplicates()
    students["y"] = np.arange(len(students))
    strip_df = strip_df.merge(students[["student_id", "y"]], on="student_id", how="left")
    color_map = {
        "Parameter": "#1B4965",
        "Performance": "#2A9D8F",
        "Site": "#E9C46A",
        "Detail": "#8AB17D",
        "Off-task": "#C44536",
        "General": "#ADB5BD",
    }
    width, height = 1050, 1180
    left, top, row_h = 155, 68, 14
    plot_w = 780
    x_max = min(19, int(strip_df["iteration"].max()))
    body = ['<text x="28" y="34" class="title">Prompt-state trajectory strip plot</text>']
    for it in range(1, x_max + 1):
        x = left + (it - 1) * plot_w / max(1, x_max - 1)
        body.append(f'<line x1="{x:.1f}" y1="{top-10}" x2="{x:.1f}" y2="{height-72}" class="tick"/>')
        body.append(f'<text x="{x:.1f}" y="{height-44}" text-anchor="middle" class="small">{it}</text>')
    for s, sub in students.groupby("primary_design_strategy", sort=False):
        y0, y1 = top + sub["y"].min() * row_h - 5, top + sub["y"].max() * row_h + 8
        body.append(f'<rect x="20" y="{y0:.1f}" width="{width-45}" height="{y1-y0:.1f}" fill="#f8f9fa" stroke="none"/>')
        body.append(f'<text x="28" y="{(y0+y1)/2+4:.1f}" class="small">{esc(s)}</text>')
    for _, r in strip_df.iterrows():
        x = left + (r["iteration"] - 1) * plot_w / max(1, x_max - 1)
        y = top + r["y"] * row_h
        body.append(f'<rect x="{x-4:.1f}" y="{y-4:.1f}" width="8" height="8" fill="{color_map.get(r["prompt_state"], "#999999")}" stroke="#ffffff" stroke-width="0.5"/>')
    lx, ly = 735, 28
    for k, state in enumerate(PROMPT_STATE_ORDER):
        x = lx + (k % 3) * 95
        y = ly + (k // 3) * 18
        body.append(f'<rect x="{x}" y="{y-9}" width="10" height="10" fill="{color_map[state]}"/>')
        body.append(f'<text x="{x+15}" y="{y}" class="small">{state}</text>')
    body.append(f'<text x="{left + plot_w/2}" y="{height-22}" text-anchor="middle" class="axis">Iteration</text>')
    write_svg(OUT / "fig3_prompt_state_trajectory_strip.svg", width, height, "\n".join(body))

    # Figure 4: learning gains by strategy.
    learn_plot = merged.dropna(subset=["gain"]).copy()
    if not learn_plot.empty:
        cats = [s for s in STRATEGY_ORDER if s in learn_plot["primary_design_strategy"].unique()]
        width, height = 950, 500
        left, top, plot_w, plot_h = 90, 60, 800, 320
        ymin, ymax = min(-4, learn_plot["gain"].min() - 1), max(8, learn_plot["gain"].max() + 1)
        def yscale(v): return top + plot_h - (v - ymin) / (ymax - ymin) * plot_h
        body = ['<text x="28" y="34" class="title">Pre-post conceptual gain by prompt-based strategy</text>']
        for val in range(math.floor(ymin), math.ceil(ymax) + 1, 2):
            y = yscale(val)
            body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" class="tick"/>')
            body.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="small">{val}</text>')
        zero = yscale(0)
        body.append(f'<line x1="{left}" y1="{zero:.1f}" x2="{left+plot_w}" y2="{zero:.1f}" stroke="#6c757d"/>')
        for i, cat in enumerate(cats):
            sub = learn_plot[learn_plot["primary_design_strategy"] == cat]
            x = left + (i + 0.5) * plot_w / len(cats)
            mean = sub["gain"].mean()
            sd = sub["gain"].std()
            if pd.notna(sd):
                body.append(f'<line x1="{x}" y1="{yscale(mean-sd):.1f}" x2="{x}" y2="{yscale(mean+sd):.1f}" stroke="#8a9a5b" stroke-width="4" opacity="0.55"/>')
            body.append(f'<circle cx="{x}" cy="{yscale(mean):.1f}" r="7" fill="#8AB17D" stroke="#264653"/>')
            for j, v in enumerate(sub["gain"]):
                jitter = ((j % 7) - 3) * 4
                body.append(f'<circle cx="{x+jitter:.1f}" cy="{yscale(v):.1f}" r="4" fill="#264653" opacity="0.72"/>')
            for k, line in enumerate(wrap_label(cat, 16)):
                body.append(f'<text x="{x}" y="{top+plot_h+35+k*12}" text-anchor="middle" class="small">{esc(line)}</text>')
            body.append(f'<text x="{x}" y="{top+plot_h+77}" text-anchor="middle" class="small">n={len(sub)}</text>')
        body.append(f'<text x="22" y="{top+plot_h/2}" transform="rotate(-90 22 {top+plot_h/2})" text-anchor="middle" class="axis">Post - pre score</text>')
        write_svg(OUT / "fig4_learning_gain_by_strategy.svg", width, height, "\n".join(body))

    # Figure 5: agency by strategy, selected dimensions.
    agency_long = merged.dropna(subset=["overall_agency"]).melt(
        id_vars=["student_id", "primary_design_strategy"],
        value_vars=["goal_setting", "self_adjustment", "responsible_action", "motivation", "overall_agency"],
        var_name="agency_dimension",
        value_name="score",
    )
    if not agency_long.empty:
        dims = ["goal_setting", "self_adjustment", "responsible_action", "motivation", "overall_agency"]
        cats = [s for s in STRATEGY_ORDER if s in agency_long["primary_design_strategy"].unique()]
        colors = ["#1B4965", "#2A9D8F", "#E76F51", "#8AB17D", "#6D597A"]
        width, height = 1020, 540
        left, top, plot_w, plot_h = 80, 65, 760, 320
        def yscale(v): return top + plot_h - (v - 1) / 4 * plot_h
        body = ['<text x="28" y="34" class="title">Exploratory agency patterns by design strategy</text>']
        for val in range(1, 6):
            y = yscale(val)
            body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" class="tick"/>')
            body.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="small">{val}</text>')
        for d_i, dim in enumerate(dims):
            pts = []
            for i, cat in enumerate(cats):
                sub = agency_long[(agency_long["primary_design_strategy"] == cat) & (agency_long["agency_dimension"] == dim)]
                if sub.empty:
                    continue
                x = left + (i + 0.5) * plot_w / len(cats) + (d_i - 2) * 5
                y = yscale(sub["score"].mean())
                pts.append((x, y))
                body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{colors[d_i]}"/>')
            if len(pts) > 1:
                body.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{colors[d_i]}" stroke-width="1.6" opacity="0.75"/>')
        for i, cat in enumerate(cats):
            x = left + (i + 0.5) * plot_w / len(cats)
            for k, line in enumerate(wrap_label(cat, 16)):
                body.append(f'<text x="{x}" y="{top+plot_h+35+k*12}" text-anchor="middle" class="small">{esc(line)}</text>')
        for d_i, dim in enumerate(dims):
            y = 75 + d_i * 22
            body.append(f'<circle cx="870" cy="{y-4}" r="5" fill="{colors[d_i]}"/>')
            body.append(f'<text x="884" y="{y}" class="small">{esc(dim)}</text>')
        body.append(f'<text x="20" y="{top+plot_h/2}" transform="rotate(-90 20 {top+plot_h/2})" text-anchor="middle" class="axis">Mean agency score (1-5)</text>')
        write_svg(OUT / "fig5_agency_by_strategy.svg", width, height, "\n".join(body))

    # Figure 6: ENA projection by strategy.
    ena_plot = merged.dropna(subset=["ENA_dim1_full", "ENA_dim2_full"]).copy()
    if not ena_plot.empty:
        cats = [s for s in STRATEGY_ORDER if s in ena_plot["primary_design_strategy"].unique()]
        palette = ["#1B4965", "#2A9D8F", "#8AB17D", "#E9C46A", "#C44536", "#6D597A", "#ADB5BD"]
        color_by = dict(zip(cats, palette))
        width, height = 900, 620
        left, top, plot_w, plot_h = 80, 60, 600, 440
        xmin, xmax = ena_plot["ENA_dim1_full"].min() - 0.25, ena_plot["ENA_dim1_full"].max() + 0.25
        ymin, ymax = ena_plot["ENA_dim2_full"].min() - 0.25, ena_plot["ENA_dim2_full"].max() + 0.25
        def xs(v): return left + (v - xmin) / (xmax - xmin) * plot_w
        def ys(v): return top + plot_h - (v - ymin) / (ymax - ymin) * plot_h
        body = ['<text x="28" y="34" class="title">ENA-style projection grouped by prompt-based strategy</text>']
        body.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" class="frame"/>')
        body.append(f'<line x1="{xs(0):.1f}" y1="{top}" x2="{xs(0):.1f}" y2="{top+plot_h}" class="tick"/>')
        body.append(f'<line x1="{left}" y1="{ys(0):.1f}" x2="{left+plot_w}" y2="{ys(0):.1f}" class="tick"/>')
        for _, r in ena_plot.iterrows():
            body.append(f'<circle cx="{xs(r["ENA_dim1_full"]):.1f}" cy="{ys(r["ENA_dim2_full"]):.1f}" r="5" fill="{color_by.get(r["primary_design_strategy"], "#999")}" opacity="0.82" stroke="#ffffff"/>')
        cents = ena_plot.groupby("primary_design_strategy")[["ENA_dim1_full", "ENA_dim2_full"]].mean().reset_index()
        for _, r in cents.iterrows():
            x, y = xs(r["ENA_dim1_full"]), ys(r["ENA_dim2_full"])
            body.append(f'<path d="M {x-7:.1f} {y:.1f} L {x:.1f} {y-7:.1f} L {x+7:.1f} {y:.1f} L {x:.1f} {y+7:.1f} Z" fill="#111827" stroke="#ffffff"/>')
        for i, cat in enumerate(cats):
            y = 80 + i * 28
            body.append(f'<circle cx="720" cy="{y-4}" r="5" fill="{color_by[cat]}"/>')
            body.append(f'<text x="735" y="{y}" class="small">{esc(cat)}</text>')
        body.append(f'<text x="{left+plot_w/2}" y="{height-55}" text-anchor="middle" class="axis">ENA dimension 1: technical / AI-reasoning coupling</text>')
        body.append(f'<text x="24" y="{top+plot_h/2}" transform="rotate(-90 24 {top+plot_h/2})" text-anchor="middle" class="axis">ENA dimension 2</text>')
        write_svg(OUT / "fig6_ena_projection_by_strategy.svg", width, height, "\n".join(body))

    # Figure 7: strategy signature radar-like heatmap.
    sig_cols = [
        "mean_parameter_rate",
        "mean_performance_rate",
        "mean_site_count",
        "mean_visual_rate",
        "mean_offtask_rate",
        "mean_jaccard",
        "mean_transformative_uptake",
        "mean_ENA_dim1",
    ]
    sig = strategy_summary.set_index("primary_design_strategy")[sig_cols].copy()
    sig_norm = sig.copy()
    for c in sig_norm.columns:
        vals = sig_norm[c].astype(float)
        rng = vals.max() - vals.min()
        sig_norm[c] = 0 if not np.isfinite(rng) or rng == 0 else (vals - vals.min()) / rng
    cell_w, cell_h = 96, 54
    width = 260 + len(sig_norm.columns) * cell_w + 30
    height = 130 + len(sig_norm.index) * cell_h + 30
    left, top = 245, 92
    headers = ["Parameter\nrate", "Performance\nrate", "Site\ncount", "Visual\nrate", "Off-task\nrate", "Prompt\nretention", "Transform.\nuptake", "ENA dim1"]
    body = ['<text x="28" y="34" class="title">Design strategy signatures across process, uptake, and ENA indicators</text>']
    for j, h in enumerate(headers):
        x = left + j * cell_w + cell_w / 2
        for k, line in enumerate(h.split("\n")):
            body.append(f'<text x="{x}" y="{62 + k*13}" text-anchor="middle" class="small">{esc(line)}</text>')
    for i, idx in enumerate(sig_norm.index):
        y = top + i * cell_h
        body.append(f'<text x="{left-12}" y="{y+32}" text-anchor="end" class="axis">{esc(idx)}</text>')
        for j, col in enumerate(sig_norm.columns):
            x = left + j * cell_w
            val = sig.loc[idx, col]
            t = sig_norm.loc[idx, col]
            body.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{interp_color(t, (253,245,230), (44,95,45))}" stroke="#ffffff"/>')
            body.append(f'<text x="{x+cell_w/2}" y="{y+32}" text-anchor="middle" class="small">{val:.2f}</text>')
    write_svg(OUT / "fig7_strategy_signature_heatmap.svg", width, height, "\n".join(body))

    print(f"Saved design strategy analysis to {OUT}")
    print(strategy_summary[["primary_design_strategy", "n", "mean_gain", "matched_gain_n", "mean_overall_agency", "matched_agency_n"]].to_string(index=False))


if __name__ == "__main__":
    main()
