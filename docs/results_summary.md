# Results Summary

This file summarizes the current results and should be used when drafting Results, Discussion, and Abstract sections.

## RQ1: Conceptual Understanding

Matched pre/post sample: `n = 68`.

Pre-test:

- M = 5.53 / 12
- SD = 2.98

Post-test:

- M = 7.07 / 12
- SD = 3.98

Raw gain:

- M = 1.54
- SD = 3.71
- 95% CI = [0.65, 2.44]
- paired t(67) = 3.43
- p = .001
- Cohen's dz = 0.42

ANCOVA-style adjusted gain model:

- Model: `gain ~ pre + class`
- adjusted mean gain = 1.54
- SE = 0.44
- t(61) = 3.54
- p < .001
- 95% CI = [0.67, 2.42]
- R2 = .14

Pre-test score was a significant covariate:

- F(1, 61) = 5.92
- p = .018
- partial eta2 = .088

Class block was not significant:

- F(5, 61) = 0.67
- p = .651

Mixed model:

- Model: `score ~ time + class + (1 | student)`
- time effect b = 1.54
- SE = 0.45
- z = 3.46
- p < .001
- 95% CI = [0.67, 2.42]
- ICC = .43

Interpretation:

Students demonstrated significant conceptual gains after participating in the GenAI-supported CAD design activity. Lower pre-test scores were associated with larger gains, suggesting possible ceiling effects or greater benefit for lower-baseline students. Because no control group is available, avoid causal claims.

Recommended RQ1 figures:

- `outputs/rq1_figures/fig1_pre_post_slope.png`
- `outputs/rq1_figures/fig4_pre_vs_gain.png`

## RQ2: Designer Profiles

Valid projects with interaction logs: `n = 70`.

Five-profile solution after excluding `colonial` from visual/style coding:

1. AI-guided technical optimizers
2. Technical prompt composers with limited uptake
3. Visual-spatial generators
4. Off-task but technically iterative designers
5. Off-task weak-coupling explorers

Model comparison:

- 5-profile solution had the lowest BIC.
- Entropy = .988.
- Smallest profile size = 7.

Profile summaries:

### AI-guided technical optimizers

- n = 25
- AI reasoning uptake rate = 1.00
- transformative uptake rate = .53
- off-task ratio = 0.00
- average iterations = 7.44
- net change = -4475.70
- interpretation: students repeatedly incorporated AI reasoning into technical and performance-oriented design revision.

### Technical prompt composers with limited uptake

- n = 12
- technical parameter density = .123
- performance goal density = .068
- AI reasoning uptake rate = .60
- transformative uptake rate = .29
- off-task ratio = 0.00
- average iterations = 6.08
- interpretation: students wrote technical and performance-oriented prompts but did not consistently align subsequent prompts with AI reasoning.

### Visual-spatial generators

- n = 18
- technical parameter density = 0.00
- performance goal density = 0.00
- AI reasoning uptake rate = .05
- transformative uptake rate = 0.00
- average iterations = 1.61
- interpretation: students used GenAI-CAD mainly for visual/spatial generation rather than sustained engineering reasoning.

### Off-task but technically iterative designers

- n = 8
- off-task ratio = .41
- AI reasoning uptake rate = .95
- transformative uptake rate = .31
- average iterations = 9.25
- net change = -4939.73
- interpretation: students showed substantial task divergence but also continued technically iterative work; exploration and engineering reasoning coexisted.

### Off-task weak-coupling explorers

- n = 7
- off-task ratio = .24
- technical parameter density = .003
- performance goal density = 0.00
- transformative uptake rate = 0.00
- net change = +1670.33
- interpretation: students diverged from task goals with weak technical reasoning and weak human-AI coupling.

Recommended RQ2 figures:

- `outputs/rq2_profiles_no_colonial/fig1_profiles_no_colonial_indicator_bars.png`
- `outputs/rq2_profiles_no_colonial/fig2_lpa_model_comparison_no_colonial.png`
- `outputs/rq2_profiles_no_colonial/fig3_design_metric_change_no_colonial.png`

## RQ3: Learning Agency

Survey responses: `n = 38`.

Survey-log/profile matched cases: `n = 12`.

### Survey Dimension Descriptives

Overall agency:

- M = 3.41 / 5
- SD = 0.92

Composite dimensions:

- key abilities: M = 3.44
- active actions: M = 3.32
- mental characteristics: M = 3.50

Individual dimensions:

- self-cognition: M = 3.30
- goal setting: M = 3.28
- self-adjustment: M = 3.72
- self-reflection: M = 3.45
- selective action: M = 3.38
- responsible action: M = 3.41
- participative action: M = 3.16
- motivation: M = 3.55
- self-efficacy: M = 3.45

Interpretation:

Students reported moderate agency overall. The strongest dimensions were self-adjustment and motivation, suggesting that GenAI-CAD particularly supported adaptive prompting, design revision, and exploratory engagement. Participative action and goal setting were comparatively lower.

### Reliability

Two-item dimensions showed acceptable to strong reliability:

- self-cognition alpha = .809
- goal setting alpha = .928
- self-adjustment alpha = .746
- self-reflection alpha = .808
- selective action alpha = .874
- responsible action alpha = .809
- participative action alpha = .889
- motivation alpha = .937
- overall 17-item alpha = .961

### Survey-log Exploratory Patterns

Matched cases: `n = 12`; interpret cautiously.

Largest Spearman associations:

- goal setting with off-task ratio: rho = -.824, p = .001
- self-cognition with off-task ratio: rho = -.706, p = .010
- motivation with off-task ratio: rho = -.576, p = .050
- self-adjustment with transformative uptake: rho = .555, p = .061

Interpretation:

Students who reported stronger goal setting and self-cognition tended to show less off-task divergence in log data. Students reporting stronger self-adjustment tended to show more transformative uptake of AI reasoning.

### Profile-informed Agency Patterns

Exploratory because matched profile groups are small.

- AI-guided technical optimizers: high self-adjustment and high AI uptake/transformative uptake.
- Technical prompt composers: high overall agency but moderate uptake.
- Visual-spatial generators: high self-reported agency but minimal log-based uptake, suggesting subjective control may not always appear as AI reasoning coupling.
- Off-task technically iterative designers: moderate agency with high iteration and off-task ratio.
- Off-task weak-coupling explorers: lowest agency and no transformative uptake.

Recommended RQ3 figures:

- `outputs/rq3_agency_final/fig1_agency_dimension_means.png`
- `outputs/rq3_agency_final/fig2_agency_by_designer_profile.png`
- `outputs/rq3_agency_final/fig3_open_ended_agency_themes.png`

## ENA-style Network Analysis

Units: `n = 70` student/project networks.

Stanzas: `399`.

Edges: `45` possible code co-occurrences among 10 nodes.

Projection:

- ENA dimension 1 explains 53.4% of network variance.
- ENA dimension 2 explains 13.7% of network variance.

Profile centroids on ENA dimension 1:

- AI-guided technical optimizers: -1.188
- Technical prompt composers with limited uptake: -0.569
- Off-task but technically iterative designers: -0.816
- Off-task weak-coupling explorers: 1.616
- Visual-spatial generators: 1.763

Interpretation:

ENA dimension 1 separates technical, goal-directed, AI-reasoning-coupled profiles from visual/weak-coupling profiles.

AI-guided technical optimizers showed stronger edges than visual-spatial generators among:

- TechPrompt -> AIParameter
- TechPrompt -> AIEnergy
- GoalPrompt -> TechPrompt
- GoalPrompt -> AIParameter
- GoalPrompt -> AIEnergy
- VisualSpatial -> SelectiveUptake
- GoalPrompt -> VisualSpatial

Interpretation:

The ENA-style analysis supports the RQ2 profile solution by showing that profiles differ not only in frequency of behaviors but in the structure of human-AI reasoning networks. AI-guided optimizers integrated goal-directed prompting, technical parameter use, AI energy reasoning, AI parameter recommendations, and uptake behaviors. Visual-spatial generators and weak-coupling explorers showed weaker integration between student prompting and AI-generated engineering reasoning.

Recommended ENA figures:

- `outputs/rq_ena/fig1_ena_projection_by_profile.png`
- `outputs/rq_ena/fig2_contrast_ai_guided_vs_visual_network.png`
- profile-specific network figures in `outputs/rq_ena/`

## Conceptual Understanding-based ENA

This follow-up ENA analysis matched assessment records to ENA student/project networks.

Post-test conceptual understanding grouping:

- Matched ENA units with post-test scores: `n = 27`.
- Median post-test score: 9.0.
- High post-test understanding group: `n = 10`, post M = 11.30, gain M = 3.89, ENA dim1 M = -0.834.
- Low/mid post-test understanding group: `n = 17`, post M = 6.41, gain M = 1.40, ENA dim1 M = -0.221.

Interpretation:

Students with higher post-test conceptual understanding were positioned further toward the technical / AI-reasoning-coupled side of ENA dimension 1. Their networks showed stronger connections among technical prompting, AI energy reasoning, AI parameter recommendations, AI climate reasoning, feasibility reasoning, and selective/transformative uptake.

Top edges stronger for the high post-test understanding group included:

- AIClimate -> SelectiveUptake
- TechPrompt -> AIClimate
- TechPrompt -> AIParameter
- TechPrompt -> AIEnergy
- TechPrompt -> AIFeasibility
- AIEnergy -> SelectiveUptake
- AIEnergy -> TransformUptake

Learning gain grouping:

- Matched ENA units with pre/post gain: `n = 24`.
- Median gain: 2.0.
- High learning gain group: `n = 10`, gain M = 4.90, ENA dim1 M = -0.621.
- Low/mid learning gain group: `n = 14`, gain M = 0.50, ENA dim1 M = -0.386.

Interpretation:

High learning-gain students showed stronger network edges around climate/site and feasibility reasoning, including AIClimate -> AIFeasibility, VisualSpatial -> AIClimate, AIParameter -> AIClimate, AIEnergy -> AIClimate, and AIClimate -> SelectiveUptake. This suggests that learning gains may be associated not only with technical prompting but also with integrating climate/site reasoning and feasibility constraints into the human-AI design process.

Recommended conceptual-understanding ENA figures:

- `outputs/rq_ena_conceptual_understanding/fig1_ena_by_post_understanding.png`
- `outputs/rq_ena_conceptual_understanding/fig2_ena_by_learning_gain.png`
- `outputs/rq_ena_conceptual_understanding/fig3_contrast_high_vs_low_post_understanding.png`
- `outputs/rq_ena_conceptual_understanding/fig4_contrast_high_vs_low_gain.png`
