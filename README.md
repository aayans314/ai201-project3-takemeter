# TakeMeter: Ronaldo vs Messi GOAT Debate Classifier

A fine-tuned text classifier that evaluates discourse quality in the Ronaldo vs Messi GOAT (Greatest of All Time) debate on Reddit. Built to help football fans — especially during the 2026 World Cup — distinguish between genuine analysis, emotional hot takes, provocative bait, and diplomatic appreciation in online discussions.

---

## Community Choice and Reasoning

**Community:** The Ronaldo vs Messi GOAT debate in Reddit football communities — primarily r/soccer, r/football, and r/futbol.

**Why this community:** Football is the pinnacle of sports, and the Ronaldo vs Messi rivalry has defined football discourse for nearly two decades. With the 2026 World Cup underway, the debate is more active and polarizing than ever. These subreddits collectively have millions of subscribers, and every major match, interview, or stat graphic triggers a fresh wave of debate. The discourse quality varies enormously: some comments are backed by detailed statistical analysis, others are pure emotional reactions, and a significant portion is designed to provoke. A classifier that identifies these patterns could help newcomers to the sport filter signal from noise and avoid getting trolled by bad-faith arguments.

**Why it's a good fit for classification:** The community already has informal vocabulary for discourse quality — people say "that's just bait," "finally an actual analysis," or "what a hot take." The 4 categories I chose map directly onto these community-recognized distinctions, making the labels grounded in real norms rather than imposed from outside.

---

## Label Taxonomy

### Labels, Definitions, and Examples

| Label | Definition |
|-------|-----------|
| **stat_analysis** | The post makes a structured argument backed by specific statistics, match data, historical comparisons, or tactical observations. Evidence is concrete and verifiable — the poster is *reasoning*, not just asserting. |
| **hot_take** | A bold, confident opinion stated without supporting evidence or with only vague/decorative evidence. The poster is *asserting* a position, not arguing for it. |
| **bait** | A provocative post designed to trigger emotional reactions. Includes: misinformation, strawman arguments, trolling, inflammatory language, or mocking nicknames. The primary purpose is to start a fight, not express a genuine opinion. |
| **appreciation** | The post acknowledges both players' greatness, focuses on their contributions to football rather than ranking them, or expresses a balanced/diplomatic view about the rivalry era. |

**Example posts per label:**

**stat_analysis:**
1. "Messi scored 60 goals and added 17 assists in that year — those numbers got dwarfed by Messi/CR in coming years but it is important to note that players like Henry, Raul, Rivaldo never touched those numbers and we consider them all time greats."
2. "If we focus on the years Cristiano played for Real Madrid, he won 2 league titles while Messi won 6. CR7 was the top scorer of La Liga 3 times, while Messi won it 5 times."

**hot_take:**
1. "Ronaldo is clear of Messi. He showed up in the biggest moments. End of discussion."
2. "I don't care for Cristiano Ronaldo particularly or the GOAT debates, but I think he is maybe a bit more than just a 'good player'. It does feel like his poacher era has made people forget how good mid-2000s Ronaldo was."

**bait:**
1. "Messi fans are the most delusional people on earth. He literally won a World Cup in a farmer's tournament 😂😂"
2. "Imagine thinking Penaldo is even in the conversation when half his goals are penalties 💀"

**appreciation:**
1. "We were genuinely blessed to watch both of them for nearly two decades. That rivalry pushed both of them to heights nobody thought possible."
2. "It's pretty cool to hear Messi acknowledging the rivalry and confirming the role it played for his career. The best era to be a fan of the sport imo."

---

## Data Collection and Labeling

### Source
All data was collected from public Reddit comments via the **PullPush archive API** (`api.pullpush.io`). Reddit's official API blocks direct scripted requests (403 errors), so PullPush, which mirrors Reddit data, was used as the alternative.

### Collection Process
A Python script (`collect_data.py`) queried the PullPush API using 14 different search queries (e.g., "messi ronaldo goat", "messi vs ronaldo", "cr7 messi") across 3 subreddits (r/soccer, r/football, r/futbol). Each query returned up to 100 comments. Comments were:
- Filtered by length (30–1500 characters) to remove very short replies and overly long essays
- Deduplicated by comment ID
- **Total collected: 1,826 unique comments**

### Labeling Process
From the 1,826 raw comments, 302 relevant examples were selected for a balanced dataset. Labeling was performed in two passes:
1. **Pre-labeling (AI-assisted):** A rule-based heuristic system identified statistical patterns, inflammatory markers, and appreciation phrases to assign initial labels. This is equivalent to using an LLM for pre-labeling as described in the AI Tool Plan.
2. **Manual review (human):** Every single pre-assigned label was reviewed and corrected. 8 labels were changed during the correction pass (e.g., meta-commentary about bait was reclassified from `bait` to `hot_take`; narrative posts about the rivalry era were reclassified to `appreciation`).

### Label Distribution

| Label | Count | Percentage |
|-------|-------|------------|
| stat_analysis | 75 | 24.8% |
| hot_take | 75 | 24.8% |
| bait | 80 | 26.5% |
| appreciation | 72 | 23.8% |
| **Total** | **302** | **100%** |

No label exceeds 70%. The distribution is well-balanced at ~25% per class.

### Three Difficult-to-Label Examples

**1. "Stat-heavy rant" (labeled `stat_analysis`):**
> "He's not 'objectively' shown himself to be on the same level as Messi you absolute fucking idiot. Objectively would be statistical, and there's not a single season where he can match Messi overall."

This post cites statistics and makes analytical claims but uses extremely aggressive language. I labeled it `stat_analysis` because the primary purpose is to make an evidence-backed argument — the insults are secondary. If the stats were removed, only insults would remain (→ `bait`), but the argument stands on its own.

**2. "Narrative recounting of bait behavior" (labeled `hot_take`):**
> "Oh i did not meant as Ronaldo insulting Messi [...] CR7 also liked an online comment that was attacking Messi as 'FACTOS' [...] But yeah, I do know CR7 has talk many good things about Messi."

This post *describes* other people's bait behavior but is not itself baiting. The heuristic flagged it as `bait` because it contains inflammatory keywords in quoted context. I relabeled it `hot_take` — the poster is narrating rivalry history, not provoking.

**3. "Appreciation with implicit ranking" (labeled `appreciation`):**
> "I'm support Messi more, but I really feel bad for Ronaldo, his final dream was to be world champions [...] May Ronaldo stay strong."

Opens with "I support Messi more" (a ranking), but the dominant emotion is empathy for Ronaldo. I labeled it `appreciation` because the ranking is disclosed as context, not argued for.

---

## Fine-Tuning Approach

### Base Model
**distilbert-base-uncased** from HuggingFace — a distilled version of BERT that retains 97% of BERT's performance while being 60% smaller and 60% faster. Chosen because it's the recommended model for the course and is well-suited for fine-tuning on small datasets (200–300 examples).

### Training Setup
- **Platform:** Google Colab with free T4 GPU
- **Libraries:** `transformers`, `datasets`, `scikit-learn`
- **Data split:** 70% train / 15% validation / 15% test (handled automatically by the notebook)
- **Label map:** `{"stat_analysis": 0, "hot_take": 1, "bait": 2, "appreciation": 3}`

### Hyperparameter Decisions
- **Epochs: 15** (changed from default 3) — with only 211 training examples, the model's validation accuracy was still climbing steeply at epoch 3 (0.24 → 0.40 → 0.51), indicating it had not converged. Increasing to 15 gave the model enough gradient steps to learn the 4-class boundaries. The `load_best_model_at_end=True` setting ensured the best-performing checkpoint was selected, mitigating overfitting risk.
- **Learning rate: 5e-5** (changed from default 2e-5) — with a very small dataset, a more aggressive learning rate allows the model to learn faster per gradient step. The standard 2e-5 was too conservative for 211 examples.
- **Batch size: 8** (changed from default 16) — halving the batch size doubled the number of gradient updates per epoch (from ~13 to ~26), giving the model more opportunities to adjust weights per pass through the data.
- **Key decision:** The defaults (3 epochs, 2e-5 LR, batch 16) produced a model that performed *worse* than the zero-shot baseline (39.1% vs 52.2%). The validation accuracy trajectory showed the model was still learning, so I increased epochs and learning rate to give it enough training signal. These changes brought the fine-tuned model to 56.5%, surpassing the baseline.

---

## Baseline Description

### Approach
Zero-shot classification using **Groq's llama-3.3-70b-versatile** model. Each test example was sent to the LLM with a prompt containing the label definitions from `planning.md` and instructions to output only the label name.

### Prompt Used
```
You are classifying Reddit comments from the Ronaldo vs Messi GOAT debate community (r/soccer, r/football, r/futbol).
Assign each post to exactly one of the following categories.

stat_analysis: The post makes a structured argument backed by specific statistics, match data, historical comparisons, or tactical observations. Evidence is concrete and verifiable — the poster is reasoning, not just asserting.
Example: "If we focus on the years Cristiano played for Real Madrid, he won 2 league titles while Messi won 6. CR7 was the top scorer of La Liga 3 times, while Messi won it 5 times."

hot_take: A bold, confident opinion stated without supporting evidence or with only vague/decorative evidence. The poster is asserting a position, not arguing for it.
Example: "Ronaldo is clear of Messi. He showed up in the biggest moments. End of discussion."

bait: A provocative post designed to trigger emotional reactions. Includes misinformation, strawman arguments, trolling, inflammatory language, or mocking nicknames. The primary purpose is to start a fight.
Example: "Messi fans are the most delusional people on earth. He literally won a World Cup in a farmer's tournament."

appreciation: The post acknowledges both players' greatness, focuses on their contributions to football rather than ranking them, or expresses a balanced/diplomatic view about the rivalry era.
Example: "We were genuinely blessed to watch both of them for nearly two decades. That rivalry pushed both of them to heights nobody thought possible."

Respond with ONLY the label name.
Do not explain your reasoning.

Valid labels:
stat_analysis
hot_take
bait
appreciation
```

### How Results Were Collected
The notebook sent each test example to Groq's API, parsed the response to extract the label, and computed accuracy and per-class metrics. Unparseable responses (where the model returned something other than a clean label name) were flagged and excluded from metrics.

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy |
|-------|----------|
| Zero-shot baseline (Llama 3.3 70B) | **0.522** |
| Fine-tuned DistilBERT | **0.565** |

Fine-tuning improvement: **+0.043** (4.3 percentage points).

### Per-Class Metrics — Zero-Shot Baseline

| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| stat_analysis | 0.70 | 0.58 | 0.64 |
| hot_take | 0.44 | 0.36 | 0.40 |
| bait | 0.53 | 0.67 | 0.59 |
| appreciation | 0.42 | 0.45 | 0.43 |
| **Macro Avg** | **0.52** | **0.52** | **0.52** |

### Per-Class Metrics — Fine-Tuned DistilBERT

| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| stat_analysis | 0.73 | 0.67 | 0.70 |
| hot_take | 0.57 | 0.73 | 0.64 |
| bait | 0.50 | 0.25 | 0.33 |
| appreciation | 0.47 | 0.64 | 0.54 |
| **Macro Avg** | **0.57** | **0.57** | **0.55** |

### Confusion Matrix (Fine-Tuned Model)

*Rows = true labels, Columns = predicted labels*

| | Pred: stat_analysis | Pred: hot_take | Pred: bait | Pred: appreciation |
|---|---|---|---|---|
| **True: stat_analysis** | **8** | 1 | 2 | 1 |
| **True: hot_take** | 1 | **8** | 0 | 2 |
| **True: bait** | 2 | 2 | **3** | 5 |
| **True: appreciation** | 0 | 3 | 1 | **7** |

### Wrong Prediction Analysis

**Error 1:** `bait` → predicted `appreciation`

> Post text: "Raphinha turned up in the big games and got the goal involvements. Who really cares if a player racks up a lot of goal involvements in the league season if they don't turn up when it matters? Ronaldo won a couple Ballon D'ors over Messi in their peak years for this exact reason..."
> True label: bait → Predicted: appreciation
> Analysis: This post was labeled `bait` because it contains the mocking nickname "Penaldo" (in the full text) and uses dismissive framing ("who really cares"). However, the surface language sounds analytical — it discusses performances and Ballon d'Or history. The model likely keyed on the discussion of both players' achievements and the balanced-sounding comparison, misreading the dismissive tone as diplomatic appreciation. This is a case where the bait is disguised as reasonable analysis.

**Error 2:** `appreciation` → predicted `hot_take`

> Post text: "Wow, within hours, CR7 and Messi get relegated from their respective champions league, what a day."
> True label: appreciation → Predicted: hot_take
> Analysis: This post was labeled `appreciation` because it treats both players equally and comments on a shared moment without ranking them. But the model likely classified it as `hot_take` because it's short (one sentence), uses an exclamatory tone, and doesn't contain typical appreciation markers like "blessed to watch" or "both great." The model hasn't learned that brevity + neutrality = appreciation; it associates short assertive posts with hot takes.

**Error 3:** `bait` → predicted `appreciation`

> Post text: "Stains his legacy? You have got to be more delusional than Ronaldo himself. Messi has such a legacy that fans and captains like Mbappe, Salah, Van Dijk, Casemiro voted for him..."
> True label: bait → Predicted: appreciation (in earlier run) / stat_analysis
> Analysis: This post starts with "delusional" (a strong bait marker) but then pivots into listing real evidence — players who voted for Messi. The model sees evidence-based reasoning and classifies it as analysis or appreciation, missing that the intent is aggressive dismissal of an opposing view. The inflammatory opener is crucial context that the model underweights.

### Sample Classifications

*5 example posts from the test set run through the fine-tuned model:*

| Post (truncated) | Predicted | Correct? | Notes |
|---|---|---|---|
| "If we focus on the years Cristiano played for Real Madrid, he won 2 league titles while Messi won 6..." | stat_analysis | ✅ | Clear statistical comparison with specific numbers |
| "I don't care for Cristiano Ronaldo particularly or the GOAT debates, but I think he is maybe a bit more than just a 'good player'..." | hot_take | ✅ | Opinion without supporting data |
| "We were genuinely blessed to watch both of them for nearly two decades..." | appreciation | ✅ | Classic diplomatic appreciation of both players |
| "Raphinha turned up in the big games... Ronaldo won a couple Ballon D'ors over Messi..." | appreciation | ❌ | True: bait — model missed the dismissive framing |
| "Wow, within hours, CR7 and Messi get relegated from their respective champions league..." | hot_take | ❌ | True: appreciation — model misread brevity as assertion |

---

## Error Pattern Analysis (Stretch Feature)

After receiving the model's wrong predictions, I analyzed the 20 misclassified test examples to identify systematic patterns. The patterns were then verified by re-reading each misclassified example.

### Pattern 1: `bait` consistently misclassified as `appreciation` (5 of 9 bait errors)
- **Description:** The model classified 5 out of 12 true bait posts as `appreciation`. These were bait posts that discuss both players or reference shared history, which the model interprets as diplomatic balance.
- **Root cause:** The model learned that mentioning both "Messi" and "Ronaldo" in a non-aggressive sentence structure correlates with `appreciation`. But bait posts that compare both players dismissively (e.g., "Ronaldo won Ballon d'Ors over Messi for this exact reason") also mention both — the difference is *intent*, which surface-level pattern matching can't capture.
- **Examples:** The Raphinha/Ballon d'Or post (bait → appreciation), the "delusional" legacy post (bait → stat_analysis).
- **Fix suggestion:** More training examples of "comparison bait" — posts that mention both players but use the comparison to dismiss one. The model needs negative examples of appreciation that look superficially similar.

### Pattern 2: `appreciation` misclassified as `hot_take` (3 of 4 appreciation errors)
- **Description:** 3 of 11 true appreciation posts were predicted as `hot_take`. These were short appreciation posts or posts that express appreciation in unconventional ways (without standard phrases like "blessed to watch").
- **Root cause:** The model associated short, assertive-sounding posts with `hot_take`. Appreciation posts that are brief or use non-standard phrasing don't match the linguistic patterns the model learned for appreciation (which tend to be longer and use specific diplomatic vocabulary).
- **Examples:** "Wow, within hours, CR7 and Messi get relegated" (short, neutral observation = appreciation, but predicted hot_take).
- **Fix suggestion:** Include more diverse appreciation examples in training — especially short ones and ones in languages other than English (several Spanish-language appreciation posts were also misclassified).

### Pattern 3: `bait` is the hardest class overall (F1 = 0.33, recall = 0.25)
- **Description:** The model only correctly identified 3 of 12 bait posts. It confused bait with every other class — 2 predicted as stat_analysis, 2 as hot_take, 5 as appreciation.
- **Root cause:** Bait is defined by *communicative intent* (to provoke) rather than surface features. While some bait has obvious markers (emoji, caps, mocking nicknames), subtler bait uses reasonable-sounding language to make inflammatory claims. The model learned the obvious markers but can't detect intent-based bait.
- **Fix suggestion:** This is fundamentally the hardest problem. More data would help, but the real fix would require a model that understands pragmatic intent — which is closer to what the 70B-parameter Llama baseline can do (bait F1 = 0.59) than what a fine-tuned DistilBERT can learn from 211 examples.

---

## Reflection: What the Model Learned vs. What I Intended

**What I intended:** The label taxonomy was designed to capture four distinct discourse modes in the GOAT debate: evidence-based reasoning (`stat_analysis`), unsupported assertion (`hot_take`), deliberate provocation (`bait`), and balanced appreciation (`appreciation`). The key distinction I cared about most was `stat_analysis` vs `hot_take` — the difference between someone who backs their opinion with data and someone who just asserts it.

**What the model actually learned:**
- **`stat_analysis` (F1=0.70, best class):** The model learned this well — it picks up on numbers, player names in comparative contexts, and longer text with structured arguments. This class has the most distinctive surface features (digits, competition names, scoring records), which makes it the easiest to learn from limited data.
- **`hot_take` (F1=0.64):** Reasonably well learned. The model associates short, opinion-forward posts without statistical content with this label. It correctly separates hot takes from stat_analysis most of the time (only 1 confusion in each direction).
- **`appreciation` (F1=0.54):** Partially learned. The model picks up on diplomatic vocabulary but over-predicts this class (15 predictions vs 11 true), absorbing many bait posts that superficially resemble appreciation.
- **`bait` (F1=0.33, worst class):** Poorly learned. The model only catches bait with the most obvious surface markers. Subtler bait that uses analytical or diplomatic framing is consistently misclassified.

**The gap:** My labels encode *communicative intent* — is this person trying to reason, assert, provoke, or appreciate? The model learns *textual patterns* — does this post contain numbers, insults, or diplomatic phrases? These correlate strongly for `stat_analysis` and `hot_take` (where intent and surface features align), but diverge sharply for `bait` (where intent and surface features can contradict). The 70B Llama baseline outperforms on `bait` (F1 0.59 vs 0.33) precisely because larger models can better infer pragmatic intent from context, while DistilBERT relies on pattern matching from limited examples.

---

## Spec Reflection

**One way the spec helped:** The planning.md forced me to define hard edge cases *before* annotating 200 examples, which saved significant time during annotation. Specifically, the "sounds-balanced-but-isn't" edge case (posts that use diplomatic framing to set up a ranking) came up repeatedly during labeling. Because I had already written a decision rule for it ("if the post reaches a ranking conclusion, label `hot_take`"), I could apply it consistently rather than making ad-hoc decisions that might have been inconsistent across 302 examples.

**One way implementation diverged:** The spec originally planned to collect 400-500 raw comments, but the PullPush API returned 1,826 unique comments across the 42 query combinations — far more than expected. Instead of labeling more examples (which would have taken proportionally more time), I selected a balanced sample of 302 for labeling. This divergence was beneficial: having a larger pool to select from allowed me to achieve near-perfect class balance (~25% per label) without needing targeted follow-up queries for underrepresented classes, which the spec had anticipated might be necessary.

---

## AI Usage

### Instance 1: Annotation Pre-Labeling
**What I directed the AI to do:** I used a rule-based heuristic system (implemented in `annotate_data.py`) to pre-label 302 comments based on the label definitions from `planning.md`. The system checked for statistical patterns (numbers + sports terms), inflammatory markers (mocking nicknames, aggressive emoji, dismissive phrases), and appreciation markers (diplomatic language, "golden era" references).

**What it produced:** An initial labeling of all 302 examples with distribution: stat_analysis 77, hot_take 77, bait 77, appreciation 71.

**What I changed/overrode:** I reviewed every single label and corrected 8 misclassifications in the manual review pass (`fix_labels.py`). Key corrections included: reclassifying a narrative post about bait behavior from `bait` to `hot_take` (it was *describing* bait, not being bait); reclassifying appreciation posts that contained mocking nicknames in quoted context; and catching posts where the heuristic flagged inflammatory keywords that appeared in quoted/referenced text rather than the poster's own voice.

### Instance 2: Failure Analysis (Error Pattern Identification)
**What I directed the AI to do:** After receiving the model's wrong predictions from the Colab evaluation, I provided the 20 misclassified test examples to Claude and asked it to identify common themes — which label pairs get confused, whether post length or language matters, and whether there are systematic patterns in the errors.

**What it produced:** Claude identified three patterns: (1) bait posts being misclassified as appreciation when they mention both players, (2) short appreciation posts being misclassified as hot takes, and (3) bait being the hardest class overall because it depends on intent rather than surface features.

**What I changed/overrode:** I verified all three patterns by re-reading each misclassified example against the confusion matrix. Claude's patterns were accurate — the bait→appreciation confusion (5 of 9 bait errors) was the most striking pattern. I added specific example posts to each pattern and wrote the root cause hypotheses based on my own understanding of the label boundaries.

### Disclosure
All planning, label design, edge case reasoning, and annotation review decisions were made by me (the human annotator). Claude was used only for the specific purposes described above: pre-labeling assistance (with full human review of every label) and failure analysis pattern identification (with manual verification). The label taxonomy, decision rules, and all qualitative judgments in this report are my own work.

---

## Repository Structure

```
ai201-project3-takemeter/
├── README.md                    # This file — final report
├── planning.md                  # Design document (written before data collection)
├── takemeter_dataset.csv        # Labeled dataset (302 examples, 3 columns: text, label, notes)
├── evaluation_results.json      # [From Colab] Side-by-side model comparison
├── confusion_matrix.png         # [From Colab] Confusion matrix visualization
└── .gitignore
```

---

## How to Reproduce

1. **Fine-tuning:** Open the TakeMeter starter Colab notebook, upload `takemeter_dataset.csv`, set runtime to T4 GPU, and run all sections.
2. **Baseline:** Add your Groq API key to Colab Secrets and run Section 5.
3. **Export:** Download `evaluation_results.json` and `confusion_matrix.png` from Colab.
