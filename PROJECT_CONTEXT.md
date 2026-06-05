# Aladdin GenAI-CAD Learning Study

This repository is the source of truth for the Aladdin GenAI-based CAD learning study. Future AI-assisted writing and analysis should read this file, then the files in `docs/`, before relying on chat history.

## Study Focus

The project examines how students interacted with a GenAI-based CAD tool, Aladdin, while completing a challenging sustainable / net-zero energy house design task.

## Research Questions

RQ1: Can interacting with a GenAI-based Computer-Aided Design (CAD) tool improve students' conceptual understanding of sustainable building design and STEM engineering education?

RQ2: Through this GenAI-guided CAD process, what different types of designers did students become, and how?

RQ3: How did interacting with a GenAI-based CAD tool on sustainable building design influence students' agency?

## Current Analytical Framing

The project currently uses a profile-centered mixed-methods learning analytics design:

- RQ1 uses pre/post assessment modeling, including ANCOVA-style adjusted gain analysis and a student random-intercept mixed model.
- RQ2 uses human-AI design reasoning trajectory analysis and LPA-style model-based clustering.
- RQ3 uses SLA-GAI-aligned agency survey scoring, survey-log integration, open-ended response coding, and mixed-methods joint display.
- ENA-style co-occurrence analysis connects RQ2 and RQ3 by modeling how prompt-side reasoning, AI reasoning, and uptake behaviors co-occur in students' design trajectories.

## Source-of-Truth Documents

- `docs/analysis_log.md`: what has been analyzed, using which files, and where outputs are saved.
- `docs/methods_codebook.md`: coding rules, variables, profile labels, and analysis procedures.
- `docs/results_summary.md`: main statistical and learning analytics findings.
- `docs/paper_outline.md`: manuscript structure and argument.

## Important Methodological Cautions

- The study currently has no randomized control group. Avoid causal language such as "GenAI caused improvement." Prefer "students demonstrated gains after participating in the GenAI-supported CAD activity."
- RQ2 coding excludes "colonial" from visual/style coding because it was a course requirement, not an autonomous student design choice.
- RQ3 survey has 38 responses, but only 12 can currently be matched to RQ2 log/profile data. Survey-log profile analysis should be described as exploratory.
- ENA-style analysis uses all available log/profile data (`n = 70`) and should be treated as a co-occurrence/network learning analytics analysis.

## Preferred Manuscript Claim

The strongest current contribution is not simply that GenAI improved learning. The stronger claim is:

Students developed different forms of agency and designer identity depending on how they coupled their own design goals with AI-generated reasoning. Productive use of GenAI-CAD was characterized by goal-directed prompting, technical parameter use, attention to AI energy/parameter reasoning, and selective or transformative uptake of AI reasoning into subsequent design moves.

