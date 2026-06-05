# Analysis Log

This file records the analyses completed so far and points to the outputs that should be used when writing the manuscript.

## Data Sources

- Pre/post assessment: `data/Pre_Post_Assessment_Combined_with_Both_Indicator(1).xlsx`
- Design log data: `data/aladdin_all_projects_design - Cleaned+Added_projects_with_name_class.csv`
- Agency survey: `data/Aladdin - Student Learning Agency Survey (Responses).xlsx`
- Interview / transcript files: `data/transcript/`
- C&E reference papers: `C&E/`

## RQ1: Conceptual Learning Gains

Question: Can interacting with the GenAI-based CAD tool improve students' conceptual understanding?

Completed analyses:

- Matched pre/post descriptive statistics.
- ANCOVA-style adjusted gain model: `gain = post - pre`, modeled as `gain ~ pre + class`.
- Mixed model: `score ~ time + class + (1 | student)`.
- Sensitivity checks using matched-only mixed model and excluding `Not found in roster`.

Key outputs:

- `outputs/rq1_results.json`
- `outputs/rq1_sensitivity.json`
- `outputs/rq1_class_descriptives.csv`
- `outputs/rq1_figures/fig1_pre_post_slope.png`
- `outputs/rq1_figures/fig2_gain_distribution.png`
- `outputs/rq1_figures/fig3_class_gains.png`
- `outputs/rq1_figures/fig4_pre_vs_gain.png`

## RQ2: Designer Profiles

Question: Through the GenAI-guided CAD process, what different types of designers did students become, and how?

Completed analyses:

- Reconstructed each project as human-AI design reasoning trajectories:
  `student prompt -> AI reasoning -> next prompt / design metric change`.
- Conducted rule-based content coding for prompt-side, AI reasoning-side, and human-AI coupling indicators.
- Excluded `colonial` from visual/style coding because it was a course requirement.
- Aggregated iteration-level codes to student-level features.
- Conducted LPA-style diagonal Gaussian mixture / model-based clustering.
- Selected a five-profile solution after excluding `colonial`.

Key outputs:

- `outputs/rq2_profiles_no_colonial/iteration_level_human_ai_reasoning_codes_no_colonial.csv`
- `outputs/rq2_profiles_no_colonial/student_level_profile_features_no_colonial_renamed.csv`
- `outputs/rq2_profiles_no_colonial/designer_profile_summary_no_colonial_renamed.csv`
- `outputs/rq2_profiles_no_colonial/lpa_model_comparison_no_colonial.csv`
- `outputs/rq2_profiles_no_colonial/representative_human_ai_trajectory_snippets_no_colonial.csv`
- `outputs/rq2_profiles_no_colonial/fig1_profiles_no_colonial_indicator_bars.png`
- `outputs/rq2_profiles_no_colonial/fig2_lpa_model_comparison_no_colonial.png`
- `outputs/rq2_profiles_no_colonial/fig3_design_metric_change_no_colonial.png`

## RQ3: Learning Agency

Question: How did interacting with GenAI-CAD influence students' agency?

Completed analyses:

- Scored the agency survey using SLA-GAI-aligned dimensions.
- Computed dimension-level descriptives and reliability.
- Matched survey responses to RQ2 profiles where possible.
- Correlated survey agency dimensions with log-based agency indicators.
- Coded open-ended survey responses using deductive agency themes.
- Generated a mixed-methods joint display.

Important limitation:

- Survey responses: `n = 38`.
- Survey-log/profile matched cases: `n = 12`.
- Profile-informed survey-log findings should be interpreted as exploratory.

Key outputs:

- `outputs/rq3_agency_final/agency_dimension_descriptives.csv`
- `outputs/rq3_agency_final/agency_dimension_reliability.csv`
- `outputs/rq3_agency_final/agency_log_spearman_correlations.csv`
- `outputs/rq3_agency_final/rq3_mixed_methods_joint_display.csv`
- `outputs/rq3_agency_final/survey_profile_match_audit.csv`
- `outputs/rq3_agency_final/fig1_agency_dimension_means.png`
- `outputs/rq3_agency_final/fig2_agency_by_designer_profile.png`
- `outputs/rq3_agency_final/fig3_open_ended_agency_themes.png`

The final, stricter matched version is saved under `outputs/rq3_agency_final/`. Avoid using `outputs/rq3_agency_fuzzy_matched/` because it temporarily included an incorrect low-confidence match.

## ENA-style Network Analysis

Purpose: Connect RQ2 and RQ3 by examining the structure of human-AI reasoning networks.

Completed analyses:

- Treated each design episode as a stanza.
- Used 10 ENA nodes: `GoalPrompt`, `TechPrompt`, `VisualSpatial`, `AIEnergy`, `AIParameter`, `AIClimate`, `AIFeasibility`, `SelectiveUptake`, `TransformUptake`, `OffTask`.
- Generated student-level co-occurrence network vectors.
- Projected centered network vectors using SVD/PCA.
- Compared networks across RQ2 designer profiles.

Key outputs:

- `outputs/rq_ena/ena_student_network_vectors.csv`
- `outputs/rq_ena/ena_profile_centroids.csv`
- `outputs/rq_ena/ena_top_edges_by_profile.csv`
- `outputs/rq_ena/ena_profile_edge_contrasts.csv`
- `outputs/rq_ena/fig1_ena_projection_by_profile.png`
- `outputs/rq_ena/fig2_contrast_ai_guided_vs_visual_network.png`
- `outputs/rq_ena/network_ai_guided_technical_optimizers.png`
- `outputs/rq_ena/network_technical_prompt_composers_with_limited_uptake.png`
- `outputs/rq_ena/network_visual_spatial_generators.png`

## Conceptual Understanding-based ENA

Purpose: Examine whether students with different levels of conceptual understanding show different human-AI reasoning network structures.

Completed analyses:

- Matched ENA student/project networks to pre/post assessment records by normalized student names.
- Created two grouping strategies:
  - post-test conceptual understanding: high post-test understanding vs low/mid post-test understanding using the median post-test score.
  - learning gain: high learning gain vs low/mid learning gain using the median matched gain.
- Compared ENA coordinates and edge-level network contrasts between groups.

Important sample sizes:

- ENA units with post-test match: `n = 27`.
- ENA units with matched pre/post gain: `n = 24`.

Key outputs:

- `outputs/rq_ena_conceptual_understanding/ena_assessment_matched_students.csv`
- `outputs/rq_ena_conceptual_understanding/post_understanding_group_summary.csv`
- `outputs/rq_ena_conceptual_understanding/gain_group_summary.csv`
- `outputs/rq_ena_conceptual_understanding/post_understanding_edge_contrast.csv`
- `outputs/rq_ena_conceptual_understanding/gain_edge_contrast.csv`
- `outputs/rq_ena_conceptual_understanding/fig1_ena_by_post_understanding.png`
- `outputs/rq_ena_conceptual_understanding/fig2_ena_by_learning_gain.png`
- `outputs/rq_ena_conceptual_understanding/fig3_contrast_high_vs_low_post_understanding.png`
- `outputs/rq_ena_conceptual_understanding/fig4_contrast_high_vs_low_gain.png`
- `outputs/rq_ena/network_off_task_but_technically_iterative_designers.png`
- `outputs/rq_ena/network_off_task_weak_coupling_explorers.png`
