# TakeMeter — planning.md

> Written before data collection. Updated before stretch features (error pattern analysis).

---

## Community

**Community:** The Ronaldo vs Messi GOAT (Greatest of All Time) debate in Reddit football communities — primarily r/soccer, r/football, and r/futbol.

**Why this community:** Football is the pinnacle of sports — it combines peak human athleticism, teamwork, and tactical thinking at a scale no other sport matches. The Ronaldo vs Messi rivalry has defined football discourse for nearly two decades, and with the 2026 World Cup underway, the debate is more active and more polarizing than ever. These subreddits collectively have millions of subscribers, and every major match, interview, or stat graphic triggers a fresh wave of debate ranging from careful analysis to outright trolling. A classifier that identifies the quality of these takes could help people quickly filter signal from noise — especially fans who are new to the sport during the World Cup and might not recognize bait when they see it.

**Why it fits classification:** The discourse is highly varied in quality. Some commenters back their arguments with stats, match data, and historical context. Others fire off bold opinions with no evidence. A significant portion of posts are designed primarily to provoke — they use misinformation, strawman arguments, or inflammatory language to bait reactions. And a smaller but meaningful group of commenters take a diplomatic stance, appreciating both players rather than ranking them. These are real distinctions that community members already recognize and talk about (e.g., "that's just bait" or "finally, an actual analysis").

---

## Labels

### Label 1: `stat_analysis`

**Definition:** The post makes a structured argument backed by specific statistics, match data, historical comparisons, or tactical observations. Evidence is concrete and verifiable — the poster is *reasoning*, not just asserting.

**Example 1:** "Messi has 45 assists in UCL — more than any player in history. He also has the most goals in a calendar year (91). Ronaldo has 140 UCL goals but only 42 assists. Their roles were fundamentally different."

**Example 2:** "If you look at Ronaldo's conversion rate in knockout stage games from 2014-2018, it's 0.78 goals per game — the highest of any forward in that span. That's why Madrid kept winning."

**Uncertain case:** A post that says "Ronaldo has more hat-tricks than anyone ever. He's the GOAT." This cites a stat but uses it as an assertion weapon, not as part of a reasoned argument. → Labeled `hot_take` because the stat is isolated and decorative — there's no reasoning connecting the stat to a conclusion.

---

### Label 2: `hot_take`

**Definition:** A bold, confident opinion stated without supporting evidence or with only vague/decorative evidence. The poster is *asserting* a position, not arguing for it. May reference stats loosely but doesn't build a reasoned case.

**Example 1:** "Ronaldo is clear of Messi. He showed up in the biggest moments. End of discussion."

**Example 2:** "Messi literally carried an entire country on his back. Nobody else in history has done that. Case closed."

**Uncertain case:** "Ronaldo's work ethic alone puts him above Messi. The man sculpted himself into one of the greatest athletes ever through sheer willpower." This sounds like it could be the start of an argument, but it stops at assertion without evidence. → `hot_take`.

---

### Label 3: `bait`

**Definition:** A provocative post designed to trigger emotional reactions. Includes: outright misinformation/false claims stated as fact, strawman arguments, obvious trolling, inflammatory comparisons meant to anger one fanbase, or posts where the primary purpose is to start a fight rather than express a genuine opinion.

**Example 1:** "Messi fans are the most delusional people on earth. He literally won a World Cup in a farmer's tournament 😂😂"

**Example 2:** "Ronaldo has more Champions League titles than Messi so he's obviously better. Messi only won when he had Xavi and Iniesta carrying him." (cherry-picks + diminishes)

**Uncertain case:** "Imagine thinking Penaldo is even in the conversation when half his goals are penalties 💀" — This uses a derogatory nickname and emoji to mock, which is clearly provocative. But it does reference a real critique (penalty reliance). → `bait` because the framing, nickname, and emoji indicate the primary purpose is to provoke, not to make a genuine argument about penalty statistics.

---

### Label 4: `appreciation`

**Definition:** The post acknowledges both players' greatness, focuses on their contributions to football rather than ranking them, or expresses a balanced/diplomatic view. The poster cares more about the game's history than winning an argument.

**Example 1:** "We were genuinely blessed to watch both of them for nearly two decades. That rivalry pushed both of them to heights nobody thought possible."

**Example 2:** "I think the debate misses the point. Messi is the most naturally talented footballer ever, and Ronaldo is the greatest athlete to play the sport. Different kinds of greatness."

**Uncertain case:** "Both are GOATs, but Messi is slightly more talented." — This starts diplomatic but ends with a ranking. → `hot_take` because the primary thrust is a ranking claim, even if it's softened with appreciation framing. Decision rule: if the post *concludes with or leans toward a ranking*, it's not appreciation — it's a hot take using diplomatic language as a softener.

---

## Hard Edge Cases

### Edge Case 1: "Sounds-balanced-but-isn't"
**Type:** Posts that use diplomatic framing as a setup for a ranking.
**Example:** "Both are incredible, but if I had to choose one for a UCL final, I'm picking Ronaldo every time."
**Decision rule:** If the post reaches a ranking conclusion, label `hot_take`. If it genuinely refuses to rank and stays balanced, label `appreciation`.

### Edge Case 2: "Single-stat assertion"
**Type:** Posts that cite one real statistic to assert superiority without context or reasoning.
**Example:** "Ronaldo has 900+ career goals. More than Messi. That's a fact."
**Decision rule:** If 1-2 stats are cited in isolation to assert superiority (no analysis of why the stat matters), label `hot_take`. If the stats are false or misleading, label `bait`. If the stats are placed in context with reasoning, label `stat_analysis`.

### Edge Case 3: "Sarcastic dismissal"
**Type:** Posts that use sarcasm to dismiss the debate entirely.
**Example:** "Ah yes, the daily Messi vs Ronaldo thread. How original."
**Decision rule:** If the post is purely meta-commentary about the debate with no opinion on the players, it doesn't cleanly fit any label. Label `appreciation` if the tone is weary-but-respectful of both players. Label `bait` if the tone is mocking/hostile toward one fanbase.

### Edge Case 4 (from annotation): "Stat-heavy rant"
**Post:** "In the same breath you could discuss the World Cup and Ronaldo's abysmal record there? [...] He's not 'objectively' shown himself to be on the same level as Messi you absolute fucking idiot. Objectively would be statistical, and there's not a single season where he can match Messi overall."
**Difficulty:** This post cites statistics and makes analytical claims, but the tone is extremely aggressive and insulting. Does the inflammatory language make it `bait`, or does the statistical reasoning make it `stat_analysis`?
**Decision:** Labeled `stat_analysis` because the primary purpose is to make an argument backed by evidence. The insults are secondary to the reasoning — the poster genuinely believes their statistical case. If the stats were removed and only the insults remained, it would be `bait`, but the argument stands on its own.

### Edge Case 5 (from annotation): "Narrative recounting of bait behavior"
**Post:** "Oh i did not meant as Ronaldo insulting Messi or anything like that, taking shot is like these: - In an interview after losing euro 2012 [...] he answer 'did you know how Messi even got KO in Copa America?' [...] CR7 also liked an online comment that was attacking Messi as 'FACTOS' [...] But yeah, I do know CR7 has talk many good things about Messi."
**Difficulty:** This post describes other people's bait behavior but is not itself baiting. The heuristic flagged it as `bait` because it contains inflammatory keywords in quoted context. But the poster is narrating history, not provoking.
**Decision:** Labeled `hot_take` — the poster is giving their opinion on the rivalry dynamic with specific examples. They're discussing, not baiting.

### Edge Case 6 (from annotation): "Appreciation with implicit ranking"
**Post:** "I'm support Messi more, but I really feel bad for Ronaldo, his final dream was to be world champions for the first time with his home country Portugal [...] May Ronaldo stay strong and maybe he may change his mind and hang on for 2026."
**Difficulty:** This post expresses empathy toward Ronaldo and wishes him well — sounds like `appreciation`. But the opening "I support Messi more" establishes a ranking. Is this appreciation or a soft hot take?
**Decision:** Labeled `appreciation` because the dominant emotion is empathy and respect for Ronaldo's journey, even from a self-declared Messi supporter. The ranking is disclosed as context, not argued for.

---

## Data Collection Plan

**Source:** Reddit comments from r/soccer, r/football, and r/futbol, collected via the PullPush archive API (`api.pullpush.io`). Reddit's official API blocks direct scripted requests with 403 errors, so PullPush (which mirrors Reddit data) is the alternative.

**Collection method:** Python script (`collect_data.py`) using 14 different search queries across 3 subreddits. Queries include variations like "messi ronaldo goat", "messi vs ronaldo", "ronaldo better messi", "cr7 messi", etc. Each query returns up to 100 comments. Comments are filtered by length (30-1500 characters) and deduplicated by comment ID.

**Target:** Collect 400-500 raw comments, then label 200+ of them.

**Label distribution goal:** ~25% per label (50+ examples each). No label above 70%.

**If a label is underrepresented:** If after labeling 200 examples any label is below 15%, I will run targeted queries to find more examples of that type. For example, if `appreciation` is underrepresented, I'll search for queries like "messi ronaldo both great" or "messi ronaldo respect". If `stat_analysis` is low, I'll search for queries with "stats" or "data" in them.

---

## Evaluation Metrics

**Overall accuracy** for both the fine-tuned model and the zero-shot baseline — but accuracy alone is insufficient for a 4-class task because it can mask poor performance on minority classes.

**Per-class precision, recall, and F1** — the most important metrics for this task. F1 balances precision and recall and is critical when classes may be imbalanced. For example, if the model learns to never predict `appreciation` (a likely minority class), accuracy might still look decent, but the per-class F1 for `appreciation` would be 0.

**Macro-averaged F1** — averages F1 across all 4 classes equally, regardless of class size. This is the single best summary metric for this task because it penalizes the model for ignoring any class.

**Confusion matrix** — shows exactly which label pairs the model confuses and in which direction. This is essential for understanding whether the model has learned the boundaries between `hot_take` and `bait` (the hardest boundary) and between `hot_take` and `stat_analysis` (the next hardest).

**Why these are the right metrics:** The GOAT debate has natural class imbalance — there are far more hot takes and bait posts than careful analysis. Accuracy would reward a model that just predicts the majority class. Per-class F1 and confusion matrices expose exactly where the model succeeds and fails, which is what the error pattern analysis (stretch feature) needs.

---

## Definition of Success

**Minimum viable performance:** The fine-tuned model achieves a macro F1 ≥ 0.55 on the test set, which meaningfully exceeds the zero-shot baseline on at least 3 out of 4 classes.

**Good performance:** Macro F1 ≥ 0.65, with no individual class F1 below 0.40.

**Genuinely useful for deployment:** Macro F1 ≥ 0.75, with the `bait` and `stat_analysis` classes both above 0.60 F1. At this level, the classifier would be reliable enough to flag probable bait posts in a community moderation tool.

**What "good enough" means practically:** If the classifier can reliably distinguish `stat_analysis` from `hot_take` (the most useful boundary for readers) and flag `bait` with reasonable precision (even if recall is imperfect), it would genuinely help World Cup newcomers filter discourse quality. Perfect accuracy on `appreciation` vs `hot_take` is less critical — misclassifying a diplomatic post as a hot take is a minor error compared to missing bait.

---

## AI Tool Plan

### Label Stress-Testing
I will give Claude my 4 label definitions and edge case descriptions and ask it to generate 5-10 posts that sit at the boundary between two labels. If Claude produces posts I can't classify cleanly, I'll tighten the definitions before committing to annotating 200 examples. This is the most valuable pre-annotation step because it forces me to confront boundary cases before I encounter them in the wild.

### Annotation Assistance
I will use Claude to pre-label a batch of collected comments. I'll provide Claude with my label definitions and a set of unlabeled posts, and ask it to assign one label per post with a brief justification. **I will then review and correct every single pre-assigned label myself** — pre-labeling speeds up annotation but does not replace human judgment. Any labels I change will be noted, and I will disclose this workflow in my AI usage section.

### Failure Analysis
After receiving model evaluation results (wrong predictions from the fine-tuned model), I will paste the misclassified examples into Claude and ask it to identify common themes — similar post length, use of sarcasm, a specific label pair that keeps getting confused, short or low-information posts, etc. I will then verify those patterns myself by re-reading the examples. This is for the error pattern analysis stretch feature.

---

## Stretch Features

### Error Pattern Analysis
Go beyond listing individual wrong predictions — identify systematic patterns in the model's errors. Planned approach:
1. Collect all misclassified test examples from the Colab evaluation output
2. Group by error type (true label → predicted label)
3. Use Claude to surface common themes across each error group
4. Verify patterns by manually re-reading each example
5. Document: "the model consistently misclassifies [pattern] because [hypothesis]"
6. Suggest what would need to change to fix each pattern

**Updated planning.md before starting this stretch feature** ✓ (this section serves as the update).
