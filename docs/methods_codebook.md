# Methods and Codebook

This document records the current analytic methods and coding rules. It should be treated as the source of truth for manuscript method writing.

## Overall Design

The study is best described as a profile-centered mixed-methods learning analytics study with an embedded one-group pretest-posttest design.

RQ1 examines conceptual learning gains. RQ2 identifies designer profiles from human-AI design reasoning trajectories. RQ3 integrates survey, log, and open-ended evidence to examine learning agency. ENA-style analysis models the structure of human-AI reasoning networks across designer profiles.

## RQ1: Learning Gain Modeling

### Data

Main data file:

- `data/Pre_Post_Assessment_Combined_with_Both_Indicator(1).xlsx`

Main sheets:

- `Student Match Summary`
- `Combined Pre Post`

### Variables

- `pre`: pre-test total score.
- `post`: post-test total score.
- `gain`: `post - pre`.
- `time`: pre = 0, post = 1.
- `class`: roster/class block.
- Maximum score used for normalized gain: 12.

### Models

ANCOVA-style adjusted gain model:

```text
gain ~ pre + class
```

Mixed model:

```text
score ~ time + class + (1 | student)
```

Interpretation caution: Because there is no randomized control group, report this as evidence of conceptual gains following participation, not causal proof that GenAI caused improvement.

## RQ2: Human-AI Design Reasoning Trajectory Coding

### Unit Structure

Raw design logs are wide-format project records with up to 19 iterations. They are reconstructed as iteration-level trajectories:

```text
student prompt_i -> AI reasoning_i -> next student prompt_i+1 / design metric change
```

The analytic unit for coding is the design iteration; student-level profile features are created by aggregating iteration-level codes.

### Prompt-side Codes

`prompt technical parameter`: prompt includes technical or engineering parameter language.

Current keyword families:

```text
R-value, U-value, insulation, thermal, HVAC, thermostat, temperature,
solar, PV, panel, overhang, glazing, ventilation, energy, net zero,
passive, efficient, efficiency, heating, cooling
```

`prompt performance goal`: prompt includes optimization or performance goal language.

Current keyword families:

```text
reduce, increase, improve, optimize, minimize, maximize, save,
efficient, efficiency, sustainable, energy, heating, cooling, solar,
net zero, passive
```

`prompt visual/spatial focus`: prompt includes form, color, size, or spatial design language.

Current keyword families:

```text
modern, style, color, colour, white, brown, pink, blue, green, red,
black, big, small, large, cozy, ergonomic, window, door, roof, wall,
room, floor, foundation, barbershop, mansion, garage, porch, trailer
```

Important exclusion:

`colonial` is excluded because it was a course/task requirement and should not be interpreted as a student-initiated visual/style choice.

`prompt off-task`: prompt shifts away from the sustainable building/CAD design task.

Current keyword families:

```text
barbershop, castle, minecraft, mcdonald, restaurant, school, store,
shop, fortnite, funny, random, car, pool, trailer, new york
```

## AI Reasoning Codes

`AI energy reasoning`: AI reasoning includes energy or thermal explanation.

Current keyword families:

```text
heating, cooling, energy, thermal, insulation, R-value, U-value, HVAC,
thermostat, solar, PV, net, electricity, demand, gain, loss, passive,
greenhouse
```

`AI parameter recommendation`: AI reasoning includes design parameters, components, or orientation.

Current keyword families:

```text
R-value, U-value, setpoint, thermostat, temperature, HVAC, solar panel,
PV, window, glazing, overhang, roof, wall, foundation, height, meter,
metre, m, array, orientation, south-facing, north-facing
```

`AI climate/site reasoning`: AI reasoning includes location, climate, weather, season, or solar context.

Current keyword families:

```text
climate, weather, latitude, location, site, hot, cold, warm, temperate,
winter, summer, sun, sunny, snow, rain, Netherlands, Switzerland,
Germany, Africa, Durham, Natick, Carolina, Amsterdam, Frankfurt,
Hawaii, Mexico, Raleigh, Benson
```

`AI trade-off reasoning`: AI reasoning includes balancing or trade-off language.

Current keyword families:

```text
trade-off, balance, balanced, while minimizing, while reducing,
however, but, optimize, compromise, both, without sacrificing
```

`AI feasibility reasoning`: AI reasoning includes constraints, boundaries, geometry, or feasibility.

Current keyword families:

```text
feasible, ensure, avoid, overlap, within, boundary, boundaries, valid,
constraint, fit, fits, remain, closed loop, outward-facing, verified,
safe, clearance
```

## Uptake / Human-AI Coupling Codes

Uptake is coded by comparing `AI reasoning_i` with `student prompt_i+1`.

Concept categories used for overlap:

```text
insulation, solar, windows, roof, orientation, energy, climate_site,
size_area, doors_walls, color_style
```

Again, `colonial` is excluded from `color_style`.

`direct uptake`: the next prompt overlaps with AI reasoning concepts but does not clearly transform or extend them.

`selective uptake`: the next prompt absorbs only part of the AI reasoning concepts.

`transformative uptake`: the next prompt absorbs AI reasoning concepts while adding technical/performance language or a new design concept relative to the current prompt.

`no uptake`: the next prompt has no conceptual overlap with prior AI reasoning.

`weak/off-task coupling`: the student interaction shifts away from sustainable building/CAD task goals or remains weakly connected to AI engineering reasoning.

## RQ2 Profile Variables

The final no-colonial profile solution uses these six clustering variables:

```text
technical_parameter_density
performance_goal_density
energy_reasoning_density
AI_reasoning_uptake_rate
transformative_uptake_rate
off_task_ratio
```

The selected solution is a five-profile model:

1. AI-guided technical optimizers
2. Technical prompt composers with limited uptake
3. Visual-spatial generators
4. Off-task but technically iterative designers
5. Off-task weak-coupling explorers

## RQ3: SLA-GAI Agency Dimensions

The agency survey is aligned with the Student Learning Agency in Generative AI-supported contexts framework.

### Key Abilities

`self_cognition`:

- I knew the difficulties I may face in the design process.
- I knew my advantages in making design solutions.

`goal_setting`:

- I set clear goals for my design solutions.
- I set goals to guide how I improve my design solutions over time.

`self_adjustment`:

- I refined my prompts when the AI does not generate useful results.
- I adjusted the design generated by AI when it is unsatisfactory.

`self_reflection`:

- I reflected on the effectiveness of generative AI when I review my house designs.
- I reflected on whether my design solutions could be improved.

### Active Actions

`selective_action`:

- I knew how to write prompts for my design solution.
- I chose when to interact with generative AI based on my own design goals.

`responsible_action`:

- I took responsibility for my design process without letting generative AI replace my thinking.
- I paid close attention to AI reasoning when designing my house using prompts.

`participative_action`:

- I asked help from my peers when facing difficulties.
- I collaborated with my peers to revise the design solutions when necessary.

### Mental Characteristics

`motivation`:

- I was curious when I started using generative AI to help with design.
- I enjoyed exploring design solutions through generative AI.

`self_efficacy`:

- I believe I can succeed in even the most challenging parts of the design process with help from generative AI.

Volition is not currently analyzed as a separate dimension because there is no clear item dedicated to volition in the survey.

## RQ3 Open-ended Agency Themes

Open-ended survey responses are coded deductively using these themes:

- planning / goal setting
- adaptive prompting
- AI reasoning monitoring
- selective reliance
- ownership protection
- peer-supported agency
- agency expansion
- agency constraint
- future control support

## ENA-style Analysis

### Unit, Stanza, Codes

Unit: student/project.

Stanza: one design episode:

```text
prompt_i + AI reasoning_i + uptake behavior toward prompt_i+1
```

ENA nodes:

```text
GoalPrompt
TechPrompt
VisualSpatial
AIEnergy
AIParameter
AIClimate
AIFeasibility
SelectiveUptake
TransformUptake
OffTask
```

### Procedure

1. Create binary code vectors for each stanza.
2. Create co-occurrence edge vectors for each stanza.
3. Aggregate normalized edge vectors to the student/project level.
4. Center student network vectors.
5. Use SVD/PCA to project networks into two dimensions.
6. Compare profile centroids and profile-level mean networks.

This is described as an ENA-style co-occurrence network analysis rather than a full external ENA software workflow.

