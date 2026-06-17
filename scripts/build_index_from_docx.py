from __future__ import annotations

import html
import re
import shutil
import zipfile
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


DOCX = Path(r"D:\Penn Study\Education\Aladdin\Aladin-draft-0617.docx")
OUT = Path("index.html")
ASSET_DIR = Path("assets/aladin_draft_0617")
TITLE = "Coupling Human and AI Reasoning: Student Agency and Designer Identity in GenAI-Enabled Design Learning"
ASSET_PUBLIC_PREFIX = "https://lee-arts-02.github.io/Aladin-summer/"


def p_text(elm) -> str:
    return "".join(t.text or "" for t in elm.iter(qn("w:t"))).strip()


def p_style(elm) -> str:
    p_pr = elm.find(qn("w:pPr"))
    if p_pr is None:
        return ""
    p_style_el = p_pr.find(qn("w:pStyle"))
    return p_style_el.get(qn("w:val")) if p_style_el is not None else ""


def image_rids(elm) -> list[str]:
    rids = []
    for blip in elm.iter(qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid:
            rids.append(rid)
    return rids


def rows_from_table(tbl) -> list[list[str]]:
    rows = []
    for tr in tbl.iter(qn("w:tr")):
        row = []
        for tc in tr.iter(qn("w:tc")):
            texts = [t.text or "" for t in tc.iter(qn("w:t"))]
            row.append(" ".join("".join(texts).split()))
        if row:
            rows.append(row)
    return rows


def clean_heading(text: str) -> str:
    text = re.sub(r"(\d+)\.\s+(\d+)", r"\1.\2", text)
    return re.sub(r"\s+", " ", text).strip()


def is_subheading_text(text: str) -> bool:
    return bool(re.match(r"^\d+\.\d+(?:\.\d+)?\s+", text))


def html_paragraph(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\b(RQ[12]\.)", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\b(p)\s*([<>=]\s*\.?\d+)", r"<em>\1</em> \2", escaped)
    escaped = re.sub(r"\b(n)\s*=\s*(\d+)", r"<em>\1</em> = \2", escaped)
    escaped = escaped.replace("χ²", "&chi;<sup>2</sup>")
    return f"        <p>{escaped}</p>"


def html_table(rows: list[list[str]], caption: str | None) -> str:
    if not rows:
        return ""
    max_cols = max(len(r) for r in rows)
    normalized = [r + [""] * (max_cols - len(r)) for r in rows]
    out = ["        <table>"]
    if caption:
        out.append(f"          <caption>{html.escape(caption)}</caption>")
    out.append("          <thead>")
    out.append("            <tr>")
    for cell in normalized[0]:
        out.append(f"              <th>{html.escape(cell)}</th>")
    out.append("            </tr>")
    out.append("          </thead>")
    out.append("          <tbody>")
    for row in normalized[1:]:
        out.append("            <tr>")
        for cell in row:
            out.append(f"              <td>{html.escape(cell)}</td>")
        out.append("            </tr>")
    out.append("          </tbody>")
    out.append("        </table>")
    return "\n".join(out)


def mcnemar_table_html() -> str:
    rows = [
        ("1", "12", "5", "0.143463", "ns"),
        ("2", "24", "6", "0.001431", "**"),
        ("3", "15", "6", "0.078354", "ns"),
        ("4", "21", "4", "0.000911", "***"),
        ("5", "15", "11", "0.557197", "ns"),
        ("6", "7", "14", "0.189247", "ns"),
        ("7", "10", "10", "1.000000", "ns"),
        ("8", "18", "6", "0.022656", "*"),
        ("9", "14", "8", "0.286279", "ns"),
        ("10", "19", "7", "0.028959", "*"),
        ("11", "19", "10", "0.136046", "ns"),
        ("12", "22", "4", "0.000534", "***"),
    ]
    out = [
        "        <table>",
        "          <caption>Table 4. McNemar's test results for question-level improvements.</caption>",
        "          <thead>",
        "            <tr>",
        "              <th>Question</th>",
        "              <th>Wrong to correct</th>",
        "              <th>Correct to wrong</th>",
        "              <th><em>p</em>-value</th>",
        "              <th>Significance</th>",
        "            </tr>",
        "          </thead>",
        "          <tbody>",
    ]
    for row in rows:
        out.append("            <tr>")
        for cell in row:
            out.append(f"              <td>{cell}</td>")
        out.append("            </tr>")
    out.extend(
        [
            "          </tbody>",
            "        </table>",
            '        <p class="table-note">Note. * <em>p</em> &lt; .05, ** <em>p</em> &lt; .01, *** <em>p</em> &lt; .001; ns = not significant. Questions with significant improvement: 2, 4, 8, 10, and 12.</p>',
        ]
    )
    return "\n".join(out)


def extract_images(doc: Document) -> dict[str, str]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    rel_to_path: dict[str, str] = {}
    used = set()
    idx = 1
    for child in doc.element.body.iterchildren():
        if child.tag != qn("w:p"):
            continue
        for rid in image_rids(child):
            if rid in rel_to_path:
                continue
            part = doc.part.related_parts[rid]
            ext = Path(part.partname).suffix or ".png"
            out_name = f"figure_{idx:02d}{ext.lower()}"
            idx += 1
            out_path = ASSET_DIR / out_name
            out_path.write_bytes(part.blob)
            rel_to_path[rid] = out_path.as_posix()
            used.add(out_path)

    for old in ASSET_DIR.glob("*"):
        if old not in used and old.is_file():
            old.unlink()
    return rel_to_path


def supplemental_discussion() -> list[str]:
    return [
        '        <h2>5 Discussion</h2>',
        '        <h3>5.1 Conceptual learning in GenAI-CAD design</h3>',
        html_paragraph(
            "The first research question asked whether interacting with a GenAI-based CAD tool could improve students' conceptual understanding of sustainable building design. The results provide affirmative evidence: students demonstrated statistically significant gains from pre- to post-test, with the largest improvements concentrated in concepts that were directly actionable within the design task. This pattern suggests that GenAI-supported CAD activity can support conceptual learning when students encounter scientific ideas as design levers rather than as decontextualized facts."
        ),
        html_paragraph(
            "The selective pattern of gains is theoretically important. Items related to R-value, U-value, thermostat efficiency, passive solar design, and solar-panel orientation improved, whereas concepts that were already comparatively familiar or less explicitly connected to students' design moves changed less. This suggests that GenAI-CAD environments do not automatically produce uniform conceptual growth. Instead, learning appears most likely when concepts are visible, manipulable, and consequential in the design process."
        ),
        html_paragraph(
            "The decline on the dark-roof item further illustrates this point. Students often manipulated visible design features such as roofs, colors, windows, and solar panels, but visible manipulation alone did not ensure understanding of the underlying energy mechanism. For Computer & Education audiences, this finding underscores the need to design GenAI learning environments that connect generated artifacts to explanatory mechanisms and simulation evidence."
        ),
        '        <h3>5.2 Designer types as patterns of human-AI reasoning</h3>',
        html_paragraph(
            "The second research question examined what types of designers students became and how those types unfolded through the GenAI-CAD process. The three-cluster solution shows that students differed not simply in the amount of tool use, but in how they configured iteration, prompt sophistication, AI-reasoning uptake, and energy-performance change. High-Iteration Sophisticated Prompters appeared to engage in sustained human-AI design reasoning, Self-Exploratory Testers showed moderate but less systematic engagement, and Short-Run Sophistication Improvers demonstrated rapid prompt growth within fewer design cycles."
        ),
        html_paragraph(
            "The design-action analysis clarifies how these profiles emerged over time. Productive engagement was characterized by continuity across prompts, action sets, and simulation feedback. Students who repeatedly refined or expanded action sets were better positioned to connect AI suggestions to design constraints and energy goals. In contrast, less integrated trajectories could still involve active prompting, but the activity was less likely to become sustained engineering reasoning."
        ),
        html_paragraph(
            "These findings suggest that productive GenAI use in engineering design should be understood as human-AI reasoning coupling. The educational value of GenAI does not come only from generating a design or providing an explanation; it depends on whether students interpret AI reasoning, select relevant ideas, and transform those ideas into subsequent design decisions."
        ),
        '        <h3>5.3 Implications for instruction and tool design</h3>',
        html_paragraph(
            "Instructionally, students may need scaffolds that help them translate broad goals, such as net-zero energy, into actionable engineering parameters. Reflection prompts, worksheets, and interface cues can ask students to identify which AI suggestions they accepted, modified, or rejected and to justify those decisions using simulation evidence."
        ),
        html_paragraph(
            "For tool design, the results point toward interfaces that make reasoning-action links visible. A GenAI-CAD environment could highlight when AI reasoning refers to insulation, solar orientation, climate, or feasibility, and then prompt students to decide whether and how to incorporate that reasoning into the next design move. Such support would keep students' design agency and disciplinary reasoning at the center of AI-assisted design learning."
        ),
        '        <h3>5.4 Limitations and future research</h3>',
        html_paragraph(
            "Several limitations should be noted. The study used a one-group pre/post design, so learning gains should be interpreted as improvement following participation rather than as causal evidence that GenAI alone produced the gains. The designer profiles were based on a modest log-data sample and should be validated with larger cohorts. In addition, the action-code scheme was developed for this sustainable building task and should be tested in other GenAI-supported design contexts."
        ),
        html_paragraph(
            "Future research should use stronger comparison designs and richer process measures to examine how scaffolds for goal setting, AI-reasoning evaluation, and parameter-based revision affect both conceptual learning and designer-profile development. Such work can clarify how GenAI tools support engineering learning while preserving students' role as active designers and reasoners."
        ),
    ]


PROMOTED_SUBHEADINGS = {
    "Learning Objectives",
    "Core Activity Supported by Aladdin",
    "Generate a design solution",
    "Analyze the design solution",
    "Iteratively Improve the Design Solution",
    "Document interaction with AI",
    "Reflection",
    "Pre- and Post-Test",
    "Interview Design",
    "Student Learning Agency Survey",
}


FEATURE_METHOD_HTML = [
    "        <h4>Prompt sophistication: qualitative coding to quantitative features</h4>",
    html_paragraph(
        "Prompt sophistication was quantified at the iteration level using a Prompt Sophistication Index (PSI). Each student prompt was coded for three components: specificity, conceptual/computational breadth (CCB), and reasoning orientation. The iteration-level score was calculated as PSI_i = specificity_i + CCB_i + reasoning orientation_i. Two student-level features were then derived from the sequence of iteration-level PSI scores. Mean PSI represented the average sophistication of a student's prompts across all valid iterations. PSI growth represented the ordinary least squares linear regression slope of PSI_i regressed on iteration number, capturing whether a student's prompting became more sophisticated over time."
    )
    .replace("PSI_i", "PSI<sub>i</sub>")
    .replace("specificity_i", "specificity<sub>i</sub>")
    .replace("CCB_i", "CCB<sub>i</sub>")
    .replace("reasoning orientation_i", "reasoning orientation<sub>i</sub>"),
    "        <h4>AI reasoning uptake: qualitative coding to quantitative features</h4>",
    html_paragraph(
        "AI reasoning uptake was quantified by estimating the extent to which students incorporated AI-generated reasoning into subsequent prompts. For each iteration, uptake combined semantic similarity and concept overlap: uptake_i = 0.5 x semantic uptake_i + 0.5 x concept overlap_i. Semantic uptake was computed using TF-IDF cosine similarity between the AI reasoning and the student's subsequent prompt, while concept overlap measured the extent to which key concepts from the AI reasoning reappeared in the next student prompt. Two student-level features were derived from this sequence. Mean uptake represented the average uptake of AI reasoning across iterations. Uptake growth represented the ordinary least squares linear regression slope of uptake_i regressed on iteration number, capturing whether students increasingly incorporated AI reasoning as the design task progressed."
    )
    .replace("uptake_i", "uptake<sub>i</sub>")
    .replace("concept overlap_i", "concept overlap<sub>i</sub>")
    .replace("semantic uptake<sub>i</sub>", "semantic uptake<sub>i</sub>")
    .replace("0.5 x", "0.5 &times;"),
]


def should_promote_paragraph(text: str) -> bool:
    return text in PROMOTED_SUBHEADINGS or text.startswith("Cluster 1:") or text.startswith("Cluster 2:") or text.startswith("Cluster 3:")


def build_body(doc: Document, rel_to_path: dict[str, str]) -> str:
    blocks = list(doc.element.body.iterchildren())
    lines: list[str] = []
    section_open = False
    pending_caption: str | None = None
    pending_figure: str | None = None
    figure_no = 0
    i = 0
    while i < len(blocks):
        child = blocks[i]
        if child.tag == qn("w:p"):
            text = p_text(child)
            style = p_style(child)
            rids = image_rids(child)
            if rids:
                for rid in rids:
                    figure_no += 1
                    src = rel_to_path[rid]
                    caption = None
                    j = i + 1
                    while j < len(blocks):
                        if blocks[j].tag == qn("w:p"):
                            candidate = p_text(blocks[j])
                            if candidate:
                                caption = candidate if candidate.startswith("Figure") else None
                                break
                        elif blocks[j].tag == qn("w:tbl"):
                            break
                        j += 1
                    if caption and "Item-level significance" in caption:
                        lines.append(mcnemar_table_html())
                        i = j
                    else:
                        public_src = ASSET_PUBLIC_PREFIX + src
                        fig = f'        <figure>\n          <img src="{html.escape(public_src)}" alt="Figure {figure_no} from the manuscript draft">'
                        if caption:
                            fig += f"\n          <figcaption>{html.escape(caption)}</figcaption>"
                            i = j
                        fig += "\n        </figure>"
                        lines.append(fig)
                i += 1
                continue

            if text.startswith("Figure"):
                i += 1
                continue

            if not text:
                i += 1
                continue

            if text.startswith("From the interview/ focus group data"):
                i += 1
                continue

            if text.startswith("5   Discussion"):
                if section_open:
                    lines.append("      </section>")
                    section_open = False
                lines.append('      <section id="discussion">')
                lines.extend(supplemental_discussion())
                # Skip draft discussion paragraphs until Conclusion.
                i += 1
                while i < len(blocks):
                    if blocks[i].tag == qn("w:p") and p_text(blocks[i]).startswith("6   Conclusion"):
                        break
                    i += 1
                continue

            if style == "Heading1":
                if section_open:
                    lines.append("      </section>")
                section_open = True
                ident = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
                lines.append(f'      <section id="{html.escape(ident)}">')
                lines.append(f"        <h2>{html.escape(clean_heading(text))}</h2>")
            elif style == "Heading2":
                lines.append(f"        <h3>{html.escape(clean_heading(text))}</h3>")
            elif is_subheading_text(text):
                lines.append(f"        <h4>{html.escape(clean_heading(text))}</h4>")
            elif should_promote_paragraph(text):
                lines.append(f"        <h4>{html.escape(clean_heading(text))}</h4>")
            elif text.startswith("Table "):
                pending_caption = text
            else:
                lines.append(html_paragraph(text))
                if text.startswith("Seven student-level features were constructed"):
                    lines.extend(FEATURE_METHOD_HTML)
        elif child.tag == qn("w:tbl"):
            rows = rows_from_table(child)
            lines.append(html_table(rows, pending_caption))
            pending_caption = None
        i += 1

    if section_open:
        lines.append("      </section>")
    return "\n\n".join(lines)


def build_html(body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(TITLE)}</title>
  <style>
    :root {{
      --ink: #1f2933;
      --muted: #5f6b7a;
      --rule: #d9dee7;
      --soft: #f6f8fb;
      --accent: #1f5f9f;
    }}
    html {{ background: #eef2f7; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Times New Roman", Times, serif;
      line-height: 1.52;
      font-size: 17px;
    }}
    .page {{
      max-width: 1120px;
      margin: 32px auto;
      background: white;
      box-shadow: 0 12px 34px rgba(15, 23, 42, .12);
      min-height: 100vh;
    }}
    header {{
      padding: 44px 56px 24px;
      border-bottom: 1px solid var(--rule);
    }}
    .journal {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
      letter-spacing: .08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 18px;
    }}
    h1 {{
      font-size: 30px;
      line-height: 1.2;
      margin: 0 0 14px;
      font-weight: 700;
    }}
    main {{ padding: 28px 56px 60px; }}
    h2 {{
      font-size: 24px;
      margin: 34px 0 14px;
      border-bottom: 2px solid var(--ink);
      padding-bottom: 5px;
      font-weight: 700;
    }}
    h3 {{
      font-size: 20px;
      margin: 28px 0 8px;
      font-weight: 700;
    }}
    h4 {{
      font-size: 17px;
      margin: 18px 0 6px;
      font-weight: 700;
      font-style: italic;
    }}
    p {{ margin: 9px 0; text-align: justify; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0 20px;
      font-size: 15px;
    }}
    caption {{
      caption-side: top;
      text-align: left;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    th, td {{
      border: 1px solid #cfd7e3;
      padding: 8px 10px;
      vertical-align: top;
    }}
    th {{
      background: #f2f5f9;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
      text-align: left;
    }}
    figure {{ margin: 22px 0 26px; }}
    figure img {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 0 auto;
      border: 1px solid var(--rule);
      background: white;
    }}
    figcaption {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
      color: var(--muted);
      margin-top: 8px;
      text-align: left;
    }}
    .references {{ font-size: 14px; text-align: left; }}
    @media (max-width: 760px) {{
      .page {{ margin: 0; box-shadow: none; }}
      header, main {{ padding-left: 22px; padding-right: 22px; }}
      table {{ font-size: 13px; display: block; overflow-x: auto; white-space: nowrap; }}
    }}
  </style>
</head>
<body>
  <article class="page">
    <header>
      <div class="journal">Computers &amp; Education manuscript draft</div>
      <h1>{html.escape(TITLE)}</h1>
    </header>
    <main>
{body}
    </main>
  </article>
</body>
</html>
"""


def main() -> None:
    doc = Document(DOCX)
    rel_to_path = extract_images(doc)
    body = build_body(doc, rel_to_path)
    html_text = build_html(body)
    OUT.write_text(html_text, encoding="utf-8", newline="\n")
    for asset in ASSET_DIR.glob("*"):
        if asset.as_posix() not in html_text:
            asset.unlink()
    print(f"wrote {OUT} with {len(rel_to_path)} images")


if __name__ == "__main__":
    main()
