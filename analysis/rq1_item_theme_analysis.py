from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "rq1_item_themes"
OUT.mkdir(parents=True, exist_ok=True)

ASSESSMENT = ROOT / "data" / "Pre_Post_Assessment_Combined_with_Both_Indicator(1).xlsx"
TRANSCRIPT_DIR = ROOT / "data" / "transcript"
ITERATION_CODES = ROOT / "outputs" / "rq2_profiles_no_colonial" / "iteration_level_human_ai_reasoning_codes_no_colonial.csv"


ITEMS = {
    1: {
        "short": "Sweater insulation",
        "concept": "Insulation / R-value / U-value",
        "correct": "No, it acts as an insulator that slows down the loss of your own body heat.",
    },
    2: {
        "short": "R-value",
        "concept": "Insulation / R-value / U-value",
        "correct": "It has high thermal resistance.",
    },
    3: {
        "short": "Doubling insulation",
        "concept": "Insulation / R-value / U-value",
        "correct": "Heat loss is inversely proportional to R-value.",
    },
    4: {
        "short": "U-value",
        "concept": "Insulation / R-value / U-value",
        "correct": "The window is more effective at keeping heat inside.",
    },
    5: {
        "short": "Window greenhouse effect",
        "concept": "Windows / sunlight / radiant heat",
        "correct": "Visible light enters and is converted to infrared radiation that cannot easily escape.",
    },
    6: {
        "short": "Dark roof in hot climate",
        "concept": "Windows / sunlight / radiant heat",
        "correct": "Dark colors absorb more radiant energy from the sun.",
    },
    7: {
        "short": "Close curtains",
        "concept": "Windows / sunlight / radiant heat",
        "correct": "To block radiant energy from the sun.",
    },
    8: {
        "short": "Thermostat setback",
        "concept": "HVAC / thermostat / energy use",
        "correct": "Turn it down; you save energy every minute the house is at a lower temperature.",
    },
    9: {
        "short": "Thermostat above vent",
        "concept": "HVAC / thermostat / energy use",
        "correct": "The rest of the house will remain too cold.",
    },
    10: {
        "short": "Passive solar overhang",
        "concept": "Solar / passive solar / net-zero",
        "correct": "Calculating the exact length of roof overhangs (eaves).",
    },
    11: {
        "short": "Net-zero cold climate",
        "concept": "Insulation / R-value / U-value",
        "correct": "Using better insulation to prevent heat loss.",
    },
    12: {
        "short": "Solar panel orientation",
        "concept": "Solar / passive solar / net-zero",
        "correct": "To maximize production during late-afternoon peak demand.",
    },
}

THEMES = {
    "Insulation / R-value / U-value": {
        "items": [1, 2, 3, 4, 11],
        "keywords": ["insulation", "insulator", "r value", "r-value", "u value", "u-value", "heat loss"],
        "quotes": [
            {
                "speaker": "Student1, Recording 2",
                "quote": "you have to take insulation into consideration to like help save energy.",
            },
            {
                "speaker": "Enil, Recording 5",
                "quote": "I learned about like insulation like or like R values, like when you add insulation, the r value increases.",
            },
        ],
    },
    "Solar / passive solar / net-zero": {
        "items": [10, 12],
        "keywords": ["solar", "panel", "panels", "sun", "net zero", "net-zero", "passive solar"],
        "quotes": [
            {
                "speaker": "Maria",
                "quote": "you can save a lot of energy, if you like, install solar panels on your room ... you collect energy from the sun.",
            },
            {
                "speaker": "McKenzie, Recording 4",
                "quote": "The solar panels can bring down the energy level of the net.",
            },
        ],
    },
    "Windows / sunlight / radiant heat": {
        "items": [5, 6, 7],
        "keywords": ["window", "windows", "sunlight", "radiant", "curtains", "roof", "dark"],
        "quotes": [
            {
                "speaker": "Carlos, Recording 5",
                "quote": "It like in the software, you can meet with a big window.",
            }
        ],
    },
    "HVAC / thermostat / energy use": {
        "items": [8, 9],
        "keywords": ["thermostat", "heater", "heating", "ac", "air condition", "cooling", "energy"],
        "quotes": [
            {
                "speaker": "Raul, Recording 4",
                "quote": "Depending on the location of where you put the building at, it differs on how much ac and how much heater you use.",
            },
            {
                "speaker": "Enil, Recording 5",
                "quote": "I realized like our country, we use like a lot of like energy like on heaters and like ac and stuff.",
            },
        ],
    },
}


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
.tiny {{ font-size: 9px; fill: #4b5563; }}
.tick {{ stroke: #d0d7de; stroke-width: 1; }}
.frame {{ fill: #ffffff; stroke: #d0d7de; stroke-width: 1; }}
</style>
<rect width="100%" height="100%" fill="#ffffff"/>
{body}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def wrap_label(text: str, max_chars: int = 20, max_lines: int = 3) -> list[str]:
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
    return lines[:max_lines]


def score_to_float(x: object) -> float:
    if pd.isna(x):
        return np.nan
    m = re.search(r"([0-9.]+)\s*/", str(x))
    if m:
        return float(m.group(1))
    return pd.to_numeric(x, errors="coerce")


def normalize_name(s: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def get_item_columns(df: pd.DataFrame) -> dict[int, dict[str, str]]:
    out = {}
    for i in range(1, 13):
        answer_cols = [c for c in df.columns if c.startswith(f"{i}. ") and not c.endswith("[Score]") and not c.endswith("[Feedback]")]
        score_cols = [c for c in df.columns if c.startswith(f"{i}. ") and c.endswith("[Score]")]
        if not answer_cols or not score_cols:
            raise ValueError(f"Missing columns for item {i}")
        out[i] = {"answer": answer_cols[0], "score": score_cols[0]}
    return out


def read_assessment() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_excel(ASSESSMENT, sheet_name="Combined Pre Post")
    item_cols = get_item_columns(df)
    df["name_norm"] = df["Username"].map(normalize_name)
    df["assessment_type"] = df["Assessment Type"].astype(str)
    for i, cols in item_cols.items():
        df[f"Q{i}_score"] = df[cols["score"]].map(score_to_float)
        df[f"Q{i}_answer"] = df[cols["answer"]]
    matched = df[df["Pre+Post Both"].astype(str).str.lower().eq("yes")].copy()

    rows = []
    for i in range(1, 13):
        for sample_label, sample_df in [("all_available", df), ("matched_only", matched)]:
            pre = sample_df[sample_df["assessment_type"].eq("Pre")][f"Q{i}_score"].dropna()
            post = sample_df[sample_df["assessment_type"].eq("Post")][f"Q{i}_score"].dropna()
            rows.append(
                {
                    "sample": sample_label,
                    "item": i,
                    "item_short": ITEMS[i]["short"],
                    "concept": ITEMS[i]["concept"],
                    "pre_n": len(pre),
                    "post_n": len(post),
                    "pre_correct_pct": 100 * pre.mean() if len(pre) else np.nan,
                    "post_correct_pct": 100 * post.mean() if len(post) else np.nan,
                    "gain_pct_points": 100 * (post.mean() - pre.mean()) if len(pre) and len(post) else np.nan,
                }
            )
    item_summary = pd.DataFrame(rows)

    choice_rows = []
    for i, cols in item_cols.items():
        for typ in ["Pre", "Post"]:
            sub = matched[matched["assessment_type"].eq(typ)]
            counts = sub[f"Q{i}_answer"].fillna("Missing").astype(str).value_counts()
            total = counts.sum()
            for answer, count in counts.items():
                choice_rows.append(
                    {
                        "item": i,
                        "assessment_type": typ,
                        "answer": answer,
                        "is_correct": answer == ITEMS[i]["correct"],
                        "count": int(count),
                        "pct": 100 * count / total if total else np.nan,
                    }
                )
    choice_dist = pd.DataFrame(choice_rows)
    return df, item_summary, choice_dist


def extract_strings_from_binary(path: Path) -> str:
    data = path.read_bytes()
    chunks = []
    for enc in ["utf-8", "utf-16le", "latin-1"]:
        text = data.decode(enc, errors="ignore")
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)
        chunks.append(text)
    text = "\n".join(chunks)
    # Keep mostly readable runs.
    runs = re.findall(r"[A-Za-z][A-Za-z0-9 ,.'\"?!:;()\-]{20,}", text)
    return "\n".join(runs)


def read_transcripts() -> pd.DataFrame:
    rows = []
    for p in TRANSCRIPT_DIR.iterdir():
        if not p.is_file():
            continue
        text = ""
        if p.suffix.lower() == ".pdf":
            try:
                import pypdf

                reader = pypdf.PdfReader(str(p))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                text = ""
        elif p.suffix.lower() in {".doc", ".docx"}:
            text = extract_strings_from_binary(p)
        if text.strip():
            rows.append({"file": p.name, "text": text})
    return pd.DataFrame(rows)


def sentence_hits(text: str, keywords: list[str], max_hits: int = 8) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text)
    hits = []
    for s in pieces:
        clean = re.sub(r"\s+", " ", s).strip()
        low = clean.lower()
        if 20 <= len(clean) <= 260 and any(k in low for k in keywords):
            hits.append(clean)
        if len(hits) >= max_hits:
            break
    return hits


def analyze_themes(item_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    transcripts = read_transcripts()
    hit_rows = []
    for theme, meta in THEMES.items():
        kws = meta["keywords"]
        for _, r in transcripts.iterrows():
            hits = sentence_hits(r["text"], kws)
            for h in hits:
                hit_rows.append({"theme": theme, "file": r["file"], "evidence": h})
    hits_df = pd.DataFrame(hit_rows)

    matched = item_summary[item_summary["sample"].eq("matched_only")]
    theme_rows = []
    for theme, meta in THEMES.items():
        items = meta["items"]
        sub = matched[matched["item"].isin(items)]
        quotes = " | ".join([f"{q['speaker']}: {q['quote']}" for q in meta["quotes"]])
        theme_rows.append(
            {
                "theme": theme,
                "items": ", ".join(f"Q{i}" for i in items),
                "pre_mean_pct": sub["pre_correct_pct"].mean(),
                "post_mean_pct": sub["post_correct_pct"].mean(),
                "gain_pct_points": sub["gain_pct_points"].mean(),
                "n_interview_keyword_hits": int((hits_df["theme"].eq(theme)).sum()) if not hits_df.empty else 0,
                "illustrative_quotes": quotes,
                "interpretation": theme_interpretation(theme, sub),
            }
        )
    return pd.DataFrame(theme_rows), hits_df


def theme_interpretation(theme: str, sub: pd.DataFrame) -> str:
    if theme == "Insulation / R-value / U-value":
        return "Interviews showed uptake of insulation vocabulary, and item gains were positive for R-value, U-value, and cold-climate insulation, but Q3 declined sharply, suggesting confusion about proportional/inverse relationships."
    if theme == "Solar / passive solar / net-zero":
        return "Students described solar panels as reducing net energy, and assessment gains were especially visible for solar-panel orientation."
    if theme == "Windows / sunlight / radiant heat":
        return "Students noticed windows in the design environment, but assessment results were mixed; Q6 declined, suggesting color/radiant absorption may not have been consolidated."
    if theme == "HVAC / thermostat / energy use":
        return "Students connected location to heating and AC use, and thermostat-related items improved modestly."
    return ""


def figure_item_prepost(item_summary: pd.DataFrame) -> None:
    df = item_summary[item_summary["sample"].eq("matched_only")].copy()
    width, height = 1180, 620
    left, top, plot_w, plot_h = 75, 70, 1040, 370
    body = ['<text x="28" y="34" class="title">Item-level pre/post correct rates (matched students)</text>']
    for val in range(0, 101, 20):
        y = top + plot_h - val / 100 * plot_h
        body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" class="tick"/>')
        body.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="small">{val}%</text>')
    band_w = plot_w / 12
    for _, r in df.iterrows():
        i = int(r["item"]) - 1
        x = left + i * band_w + 12
        pre_h = r["pre_correct_pct"] / 100 * plot_h
        post_h = r["post_correct_pct"] / 100 * plot_h
        body.append(f'<rect x="{x}" y="{top+plot_h-pre_h:.1f}" width="22" height="{pre_h:.1f}" fill="#9CA3AF"/>')
        body.append(f'<rect x="{x+26}" y="{top+plot_h-post_h:.1f}" width="22" height="{post_h:.1f}" fill="#1F5F9F"/>')
        body.append(f'<text x="{x+24}" y="{top+plot_h+20}" text-anchor="middle" class="small">Q{int(r["item"])}</text>')
        for k, line in enumerate(wrap_label(r["item_short"], 12, 2)):
            body.append(f'<text x="{x+24}" y="{top+plot_h+36+k*11}" text-anchor="middle" class="tiny">{esc(line)}</text>')
    body.append('<rect x="930" y="30" width="14" height="14" fill="#9CA3AF"/><text x="950" y="42" class="small">Pre</text>')
    body.append('<rect x="1000" y="30" width="14" height="14" fill="#1F5F9F"/><text x="1020" y="42" class="small">Post</text>')
    body.append(f'<text x="22" y="{top+plot_h/2}" transform="rotate(-90 22 {top+plot_h/2})" text-anchor="middle" class="axis">Correct response rate</text>')
    write_svg(OUT / "fig1_item_prepost_correct_rates.svg", width, height, "\n".join(body))


def figure_item_gains(item_summary: pd.DataFrame) -> None:
    df = item_summary[item_summary["sample"].eq("matched_only")].sort_values("gain_pct_points")
    width, height = 900, 600
    left, top, plot_w, row_h = 310, 55, 500, 34
    min_gain = min(-55, math.floor(df["gain_pct_points"].min() / 10) * 10)
    max_gain = max(55, math.ceil(df["gain_pct_points"].max() / 10) * 10)
    def xs(v): return left + (v - min_gain) / (max_gain - min_gain) * plot_w
    body = ['<text x="28" y="34" class="title">Item-level gains in correct response rate</text>']
    for val in range(int(min_gain), int(max_gain) + 1, 20):
        x = xs(val)
        body.append(f'<line x1="{x:.1f}" y1="{top-8}" x2="{x:.1f}" y2="{top+row_h*12}" class="tick"/>')
        body.append(f'<text x="{x:.1f}" y="{top+row_h*12+18}" text-anchor="middle" class="small">{val}</text>')
    zero = xs(0)
    body.append(f'<line x1="{zero:.1f}" y1="{top-10}" x2="{zero:.1f}" y2="{top+row_h*12}" stroke="#4b5563"/>')
    for idx, (_, r) in enumerate(df.iterrows()):
        y = top + idx * row_h
        label = f"Q{int(r['item'])}: {r['item_short']}"
        body.append(f'<text x="{left-10}" y="{y+21}" text-anchor="end" class="axis">{esc(label)}</text>')
        x0, x1 = xs(0), xs(r["gain_pct_points"])
        color = "#0F766E" if r["gain_pct_points"] >= 0 else "#C2410C"
        body.append(f'<rect x="{min(x0,x1):.1f}" y="{y+7}" width="{abs(x1-x0):.1f}" height="18" fill="{color}"/>')
        body.append(f'<text x="{x1 + (6 if r["gain_pct_points"] >= 0 else -6):.1f}" y="{y+21}" text-anchor="{"start" if r["gain_pct_points"] >= 0 else "end"}" class="small">{r["gain_pct_points"]:+.1f}</text>')
    body.append(f'<text x="{left+plot_w/2}" y="{height-22}" text-anchor="middle" class="axis">Post - pre percentage points</text>')
    write_svg(OUT / "fig2_item_gain_sorted.svg", width, height, "\n".join(body))


def figure_theme_prepost(theme_summary: pd.DataFrame) -> None:
    df = theme_summary.copy()
    width, height = 980, 470
    left, top, plot_w, plot_h = 90, 65, 780, 280
    body = ['<text x="28" y="34" class="title">Concept-theme pre/post correct rates</text>']
    for val in range(0, 101, 20):
        y = top + plot_h - val / 100 * plot_h
        body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" class="tick"/>')
        body.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="small">{val}%</text>')
    band_w = plot_w / len(df)
    for idx, r in df.iterrows():
        x = left + idx * band_w + 35
        pre_h = r["pre_mean_pct"] / 100 * plot_h
        post_h = r["post_mean_pct"] / 100 * plot_h
        body.append(f'<rect x="{x}" y="{top+plot_h-pre_h:.1f}" width="36" height="{pre_h:.1f}" fill="#9CA3AF"/>')
        body.append(f'<rect x="{x+42}" y="{top+plot_h-post_h:.1f}" width="36" height="{post_h:.1f}" fill="#0F766E"/>')
        for k, line in enumerate(wrap_label(r["theme"], 19, 3)):
            body.append(f'<text x="{x+39}" y="{top+plot_h+25+k*12}" text-anchor="middle" class="small">{esc(line)}</text>')
        body.append(f'<text x="{x+39}" y="{top+plot_h+68}" text-anchor="middle" class="tiny">{esc(r["items"])}</text>')
    body.append('<rect x="760" y="30" width="14" height="14" fill="#9CA3AF"/><text x="780" y="42" class="small">Pre</text>')
    body.append('<rect x="825" y="30" width="14" height="14" fill="#0F766E"/><text x="845" y="42" class="small">Post</text>')
    write_svg(OUT / "fig3_theme_prepost_correct_rates.svg", width, height, "\n".join(body))


def figure_q6_choice_distribution(choice_dist: pd.DataFrame) -> None:
    q6 = choice_dist[choice_dist["item"].eq(6)].copy()
    # Keep answer order by post frequency for readability.
    answers = list(q6[q6["assessment_type"].eq("Post")].sort_values("pct", ascending=False)["answer"])
    width, height = 1050, 500
    left, top, plot_w, row_h = 420, 60, 500, 55
    body = ['<text x="28" y="34" class="title">Q6 answer distribution: dark-colored roofs in hot, sunny climates</text>']
    for val in range(0, 101, 20):
        x = left + val / 100 * plot_w
        body.append(f'<line x1="{x:.1f}" y1="{top-8}" x2="{x:.1f}" y2="{top+len(answers)*row_h}" class="tick"/>')
        body.append(f'<text x="{x:.1f}" y="{top+len(answers)*row_h+18}" text-anchor="middle" class="small">{val}%</text>')
    for idx, ans in enumerate(answers):
        y = top + idx * row_h
        is_correct = ans == ITEMS[6]["correct"]
        label = ans + (" (correct)" if is_correct else "")
        for k, line in enumerate(wrap_label(label, 48, 2)):
            body.append(f'<text x="{left-12}" y="{y+17+k*12}" text-anchor="end" class="small">{esc(line)}</text>')
        pre = q6[(q6["assessment_type"].eq("Pre")) & (q6["answer"].eq(ans))]["pct"]
        post = q6[(q6["assessment_type"].eq("Post")) & (q6["answer"].eq(ans))]["pct"]
        pre = float(pre.iloc[0]) if len(pre) else 0
        post = float(post.iloc[0]) if len(post) else 0
        body.append(f'<rect x="{left}" y="{y+8}" width="{pre/100*plot_w:.1f}" height="16" fill="#9CA3AF"/>')
        body.append(f'<rect x="{left}" y="{y+29}" width="{post/100*plot_w:.1f}" height="16" fill="#C2410C"/>')
        body.append(f'<text x="{left+pre/100*plot_w+6:.1f}" y="{y+21}" class="tiny">{pre:.1f}</text>')
        body.append(f'<text x="{left+post/100*plot_w+6:.1f}" y="{y+42}" class="tiny">{post:.1f}</text>')
    body.append('<rect x="790" y="30" width="14" height="14" fill="#9CA3AF"/><text x="810" y="42" class="small">Pre</text>')
    body.append('<rect x="850" y="30" width="14" height="14" fill="#C2410C"/><text x="870" y="42" class="small">Post</text>')
    body.append(f'<text x="{left+plot_w/2}" y="{height-22}" text-anchor="middle" class="axis">Percent of matched responses</text>')
    write_svg(OUT / "fig4_q6_answer_distribution.svg", width, height, "\n".join(body))


def figure_theme_joint_display(theme_summary: pd.DataFrame) -> None:
    width, row_h = 1250, 122
    height = 80 + row_h * len(theme_summary) + 40
    body = ['<text x="28" y="34" class="title">Interview themes triangulated with item-level assessment patterns</text>']
    headers = [("Theme", 30, 180), ("Items", 210, 70), ("Pre -> Post", 295, 120), ("Interview evidence", 430, 410), ("Interpretation", 860, 350)]
    for h, x, _ in headers:
        body.append(f'<text x="{x}" y="66" class="axis" font-weight="700">{h}</text>')
    for idx, r in theme_summary.iterrows():
        y = 82 + idx * row_h
        body.append(f'<rect x="24" y="{y-18}" width="{width-48}" height="{row_h-8}" fill="{"#f8fafc" if idx % 2 == 0 else "#ffffff"}" stroke="#d0d7de"/>')
        for k, line in enumerate(wrap_label(r["theme"], 24, 3)):
            body.append(f'<text x="30" y="{y+k*13}" class="small">{esc(line)}</text>')
        body.append(f'<text x="210" y="{y}" class="small">{esc(r["items"])}</text>')
        body.append(f'<text x="295" y="{y}" class="small">{r["pre_mean_pct"]:.1f}% -> {r["post_mean_pct"]:.1f}%</text>')
        body.append(f'<text x="295" y="{y+16}" class="tiny">gain {r["gain_pct_points"]:+.1f} pp</text>')
        quote_text = r["illustrative_quotes"]
        for k, line in enumerate(wrap_label(quote_text, 62, 5)):
            body.append(f'<text x="430" y="{y+k*13}" class="tiny">{esc(line)}</text>')
        for k, line in enumerate(wrap_label(r["interpretation"], 55, 6)):
            body.append(f'<text x="860" y="{y+k*13}" class="tiny">{esc(line)}</text>')
    write_svg(OUT / "fig5_interview_assessment_joint_display.svg", width, height, "\n".join(body))


def main() -> None:
    _, item_summary, choice_dist = read_assessment()
    theme_summary, transcript_hits = analyze_themes(item_summary)
    prompt_exposure = analyze_q6_prompt_exposure()

    item_summary.to_csv(OUT / "rq1_item_level_prepost_summary.csv", index=False)
    choice_dist.to_csv(OUT / "rq1_item_answer_choice_distribution.csv", index=False)
    theme_summary.to_csv(OUT / "rq1_theme_assessment_joint_display.csv", index=False)
    transcript_hits.to_csv(OUT / "interview_theme_keyword_hits.csv", index=False)
    prompt_exposure.to_csv(OUT / "q6_prompt_exposure_summary.csv", index=False)

    figure_item_prepost(item_summary)
    figure_item_gains(item_summary)
    figure_theme_prepost(theme_summary)
    figure_q6_choice_distribution(choice_dist)
    figure_theme_joint_display(theme_summary)

    matched = item_summary[item_summary["sample"].eq("matched_only")]
    print(matched[["item", "item_short", "pre_correct_pct", "post_correct_pct", "gain_pct_points"]].to_string(index=False))
    print("\nTheme summary:")
    print(theme_summary[["theme", "items", "pre_mean_pct", "post_mean_pct", "gain_pct_points"]].to_string(index=False))
    print(f"\nSaved outputs to {OUT}")


def analyze_q6_prompt_exposure() -> pd.DataFrame:
    if not ITERATION_CODES.exists():
        return pd.DataFrame()
    df = pd.read_csv(ITERATION_CODES)
    prompts = df["prompt"].fillna("").astype(str).str.lower()
    patterns = {
        "roof": r"\broof\b|roofs|roofing",
        "color_or_visible_color": r"\bcolor\b|\bcolour\b|\bwhite\b|\bblack\b|\bbrown\b|\bred\b|\bblue\b|\bgreen\b|\bpink\b|\byellow\b|\bdark\b|\blight\b",
        "dark_or_black": r"\bdark\b|\bblack\b",
        "hot_sunny_climate": r"\bhot\b|\bsunny\b|\bsummer\b|\bdesert\b|\bclimate\b",
        "radiant_or_absorption_mechanism": r"\bradiant\b|\bradiation\b|\babsorb\b|\babsorbs\b|\babsorption\b|\breflect\b|\bsolar gain\b",
    }
    rows = []
    for name, pat in patterns.items():
        hit = prompts.str.contains(pat, regex=True)
        rows.append(
            {
                "prompt_feature": name,
                "n_iteration_prompts": int(hit.sum()),
                "pct_iteration_prompts": 100 * float(hit.mean()),
                "n_unique_students": int(df.loc[hit, "student_id"].nunique()) if "student_id" in df.columns else np.nan,
            }
        )
    combos = {
        "roof + dark/black": patterns["roof"] + "||" + patterns["dark_or_black"],
        "roof + hot/sunny climate": patterns["roof"] + "||" + patterns["hot_sunny_climate"],
        "dark/black + hot/sunny climate": patterns["dark_or_black"] + "||" + patterns["hot_sunny_climate"],
        "roof + dark/black + hot/sunny climate": patterns["roof"] + "||" + patterns["dark_or_black"] + "||" + patterns["hot_sunny_climate"],
        "roof + radiant/absorption mechanism": patterns["roof"] + "||" + patterns["radiant_or_absorption_mechanism"],
    }
    for name, combo in combos.items():
        masks = [prompts.str.contains(p, regex=True) for p in combo.split("||")]
        hit = masks[0]
        for m in masks[1:]:
            hit = hit & m
        rows.append(
            {
                "prompt_feature": name,
                "n_iteration_prompts": int(hit.sum()),
                "pct_iteration_prompts": 100 * float(hit.mean()),
                "n_unique_students": int(df.loc[hit, "student_id"].nunique()) if "student_id" in df.columns else np.nan,
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()
