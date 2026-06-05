# Results Draft

This is a working draft assembled from current outputs. It should be refined after final decisions about figures, tables, and any additional validation.

## RQ1: Conceptual Understanding

Students demonstrated significant conceptual gains after participating in the GenAI-supported CAD design activity. In the matched sample (`n = 68`), students' mean score increased from 5.53 (`SD = 2.98`) at pre-test to 7.07 (`SD = 3.98`) at post-test on a 12-point assessment. The average raw gain was 1.54 points (`SD = 3.71`), 95% CI [0.65, 2.44], paired `t(67) = 3.43`, `p = .001`, `dz = 0.42`.

An ANCOVA-style adjusted gain model controlling for pre-test score and class confirmed the improvement. The adjusted mean gain was 1.54 points (`SE = 0.44`), `t(61) = 3.54`, `p < .001`, 95% CI [0.67, 2.42]. Pre-test score was a significant covariate, `F(1, 61) = 5.92`, `p = .018`, partial eta2 = .088, indicating that students with lower baseline scores tended to show larger gains. The class block was not significant, `F(5, 61) = 0.67`, `p = .651`.

A mixed model with student random intercepts also supported the same conclusion. In the model `score ~ time + class + (1 | student)`, the time effect was significant, `b = 1.54`, `SE = 0.45`, `z = 3.46`, `p < .001`, 95% CI [0.67, 2.42]. The intraclass correlation was .43, indicating substantial stable differences among students and supporting the use of a random-intercept model.

Together, these findings suggest that students demonstrated significant conceptual learning gains after the GenAI-CAD activity. Because the current design does not include a randomized control group, these gains should be interpreted as learning improvement following participation rather than causal evidence that GenAI alone produced the gains.

## RQ2: Designer Profiles

To examine what types of designers students became, we reconstructed each design log as a human-AI design reasoning trajectory linking each student prompt, the AI-generated reasoning, and the student's subsequent prompt or design change. The final analysis excluded `colonial` from visual/style coding because it was a course requirement rather than a student-initiated design choice. A five-profile solution was retained because it had the lowest BIC, high entropy (.988), and no profile smaller than seven students.

The first profile, AI-guided technical optimizers (`n = 25`), showed strong coupling between student design moves and AI reasoning. These students had an AI reasoning uptake rate of 1.00 and a transformative uptake rate of .53, with no off-task divergence. Their design trajectories showed an average net energy change of -4475.70, suggesting that their interaction patterns were associated with productive technical optimization.

The second profile, technical prompt composers with limited uptake (`n = 12`), showed the highest technical parameter and performance goal densities but only moderate AI reasoning uptake (.60). These students appeared to express technical intentions in their prompts, but their subsequent prompts were less consistently aligned with AI reasoning.

The third profile, visual-spatial generators (`n = 18`), showed little technical or performance-oriented prompting and low AI reasoning uptake (.05). Their average number of iterations was 1.61. This profile appears to represent students who used the system primarily for visual or spatial generation rather than sustained engineering reasoning.

The fourth profile, off-task but technically iterative designers (`n = 8`), combined a high off-task ratio (.41) with substantial iteration (`M = 9.25`) and high AI reasoning uptake (.95). Their net energy metric improved on average, suggesting that task divergence and technical iteration coexisted for this group.

The fifth profile, off-task weak-coupling explorers (`n = 7`), showed task divergence with weak technical prompting and no transformative uptake. Their net energy metric worsened on average, suggesting weak integration between student prompting and AI-generated engineering reasoning.

Overall, RQ2 results indicate that students did not simply differ in how often they prompted the system. They differed in how they coupled their own design goals with AI-generated reasoning, and this coupling shaped the kinds of designers they became.

## ENA-style Network Results

The ENA-style co-occurrence analysis provided additional evidence that designer profiles differed in the structure of their human-AI reasoning networks. The analysis included 70 student/project networks and 399 design stanzas. ENA dimension 1 explained 53.4% of the network variance, and ENA dimension 2 explained 13.7%.

Profile centroids showed a clear separation along ENA dimension 1. AI-guided technical optimizers were positioned on the negative side of dimension 1 (`M = -1.188`), as were technical prompt composers (`M = -0.569`) and off-task but technically iterative designers (`M = -0.816`). In contrast, visual-spatial generators (`M = 1.763`) and off-task weak-coupling explorers (`M = 1.616`) were positioned on the positive side.

Contrasting AI-guided technical optimizers with visual-spatial generators showed that the former had stronger connections among `TechPrompt`, `GoalPrompt`, `AIEnergy`, `AIParameter`, and uptake-related nodes. The strongest differentiating edges included `TechPrompt -> AIParameter`, `TechPrompt -> AIEnergy`, `GoalPrompt -> TechPrompt`, `GoalPrompt -> AIParameter`, and `GoalPrompt -> AIEnergy`. These results suggest that productive profiles were characterized not only by individual behaviors but by coherent networks linking goals, technical parameters, AI energy reasoning, AI parameter recommendations, and uptake.

## RQ3: Student Learning Agency

Students reported moderate learning agency overall. Across 38 survey responses, the overall agency mean was 3.41 on a 5-point scale (`SD = 0.92`). The composite mean for key abilities was 3.44, active actions was 3.32, and mental characteristics was 3.50. The strongest individual dimensions were self-adjustment (`M = 3.72`) and motivation (`M = 3.55`), while participative action (`M = 3.16`) and goal setting (`M = 3.28`) were comparatively lower.

Reliability estimates for the two-item dimensions were acceptable to strong. Cronbach's alpha values ranged from .746 for self-adjustment to .937 for motivation. The 17-item overall agency score had high internal consistency (`alpha = .961`).

Exploratory survey-log integration was possible for 12 matched cases. These results should be interpreted cautiously. Goal setting was negatively associated with off-task ratio (`rho = -.824`, `p = .001`), and self-cognition was also negatively associated with off-task ratio (`rho = -.706`, `p = .010`). Self-adjustment showed a positive association with transformative uptake (`rho = .555`, `p = .061`). These patterns suggest that students who reported stronger goal setting and self-cognition were less likely to diverge from the task, while students who reported stronger self-adjustment were more likely to transform AI reasoning into subsequent design action.

The mixed-methods joint display further suggested that agency took different forms across designer profiles. AI-guided technical optimizers showed high self-adjustment and high log-based uptake. Technical prompt composers reported high agency but had more limited uptake, suggesting that they may have treated AI as an executor of student-defined design intentions. Visual-spatial generators reported high agency but showed minimal AI reasoning uptake, indicating that subjective control may not always correspond to engineering reasoning coupling. Off-task weak-coupling explorers had the lowest agency scores and no transformative uptake.

Together, RQ3 findings suggest that GenAI-CAD interaction influenced agency by supporting self-adjustment, exploration, and reflection, but agency was unevenly distributed. Productive agency appeared most clearly when students monitored AI reasoning and transformed it into their own design decisions.

