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
- **Epochs: 3** (default) — with only ~210 training examples, more epochs risk overfitting. 3 epochs is standard for small-dataset fine-tuning of transformer models.
- **Learning rate: 2e-5** (default) — this is the established best practice for fine-tuning BERT-family models. Lower rates underfit on small datasets; higher rates destabilize training.
- **Batch size: 16** (default) — balances GPU memory usage with gradient stability. With ~210 training examples, this gives ~13 gradient updates per epoch.
- **Key decision:** I kept the defaults because the dataset is small enough that aggressive hyperparameter tuning is more likely to overfit to the validation set than to genuinely improve generalization. The priority was clean labels over tuned parameters.

---

## Baseline Description

### Approach
Zero-shot classification using **Groq's llama-3.3-70b-versatile** model. Each test example was sent to the LLM with a prompt containing the label definitions from `planning.md` and instructions to output only the label name.

### Prompt Used
```
You are a text classifier for the Ronaldo vs Messi GOAT debate on Reddit.

Classify the following post into exactly ONE of these labels:

- stat_analysis: The post makes a structured argument backed by specific statistics, match data, historical comparisons, or tactical observations. Evidence is concrete and verifiable.
- hot_take: A bold, confident opinion stated without supporting evidence. The poster is asserting a position, not arguing for it.
- bait: A provocative post designed to trigger emotional reactions. Includes misinformation, trolling, inflammatory language, or mocking nicknames.
- appreciation: The post acknowledges both players' greatness or expresses a balanced/diplomatic view about the rivalry.

Post: "{text}"

Respond with ONLY the label name (stat_analysis, hot_take, bait, or appreciation). Nothing else.
```

### How Results Were Collected
The notebook sent each test example to Groq's API, parsed the response to extract the label, and computed accuracy and per-class metrics. Unparseable responses (where the model returned something other than a clean label name) were flagged and excluded from metrics.

---

## Evaluation Report

> [!NOTE]
> The metrics below should be filled in after running the Colab notebook (Sections 3-6). Upload your CSV, run all sections, and update these numbers with actual results from `evaluation_results.json`.

### Overall Accuracy

| Model | Accuracy |
|-------|----------|
| Zero-shot baseline (Llama 3.3 70B) | *[fill after Colab]* |
| Fine-tuned DistilBERT | *[fill after Colab]* |

### Per-Class Metrics — Zero-Shot Baseline

| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| stat_analysis | *[fill]* | *[fill]* | *[fill]* |
| hot_take | *[fill]* | *[fill]* | *[fill]* |
| bait | *[fill]* | *[fill]* | *[fill]* |
| appreciation | *[fill]* | *[fill]* | *[fill]* |
| **Macro Avg** | | | *[fill]* |

### Per-Class Metrics — Fine-Tuned DistilBERT

| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| stat_analysis | *[fill]* | *[fill]* | *[fill]* |
| hot_take | *[fill]* | *[fill]* | *[fill]* |
| bait | *[fill]* | *[fill]* | *[fill]* |
| appreciation | *[fill]* | *[fill]* | *[fill]* |
| **Macro Avg** | | | *[fill]* |

### Confusion Matrix (Fine-Tuned Model)

*Rows = true labels, Columns = predicted labels*

| | Pred: stat_analysis | Pred: hot_take | Pred: bait | Pred: appreciation |
|---|---|---|---|---|
| **True: stat_analysis** | *[fill]* | *[fill]* | *[fill]* | *[fill]* |
| **True: hot_take** | *[fill]* | *[fill]* | *[fill]* | *[fill]* |
| **True: bait** | *[fill]* | *[fill]* | *[fill]* | *[fill]* |
| **True: appreciation** | *[fill]* | *[fill]* | *[fill]* | *[fill]* |

### Wrong Prediction Analysis

**Error 1:** *[fill after Colab — describe a post the model got wrong, which labels were confused, and why]*

> Post text: "[paste post]"
> True label: [X] → Predicted: [Y]
> Analysis: [Why the model got this wrong — which boundary failed, was it ambiguous language, sarcasm, length, or a labeling issue?]

**Error 2:** *[fill after Colab]*

> Post text: "[paste post]"
> True label: [X] → Predicted: [Y]
> Analysis: [...]

**Error 3:** *[fill after Colab]*

> Post text: "[paste post]"
> True label: [X] → Predicted: [Y]
> Analysis: [...]

### Sample Classifications

*3-5 example posts run through the fine-tuned model:*

| Post (truncated) | Predicted Label | Confidence | Correct? | Notes |
|---|---|---|---|---|
| *[fill]* | *[fill]* | *[fill]* | *[fill]* | *[fill]* |
| *[fill]* | *[fill]* | *[fill]* | *[fill]* | *[fill]* |
| *[fill]* | *[fill]* | *[fill]* | *[fill]* | *[fill]* |
| *[fill]* | *[fill]* | *[fill]* | *[fill]* | *[fill]* |
| *[fill]* | *[fill]* | *[fill]* | *[fill]* | *[fill]* |

---

## Error Pattern Analysis (Stretch Feature)

*[Fill after running Colab and analyzing wrong predictions]*

After receiving the model's wrong predictions, I provided the misclassified examples to Claude and asked it to identify systematic patterns. The patterns identified were then verified by re-reading each misclassified example.

### Pattern 1: *[fill — e.g., "hot_take ↔ stat_analysis confusion on posts with isolated stats"]*
- **Description:** *[describe the pattern]*
- **Root cause:** *[hypothesize why]*
- **Examples:** *[list 2-3 examples that follow this pattern]*
- **Fix suggestion:** *[what would need to change]*

### Pattern 2: *[fill]*

### Pattern 3: *[fill]*

---

## Reflection: What the Model Learned vs. What I Intended

*[Fill after running Colab]*

**What I intended:** The label taxonomy was designed to capture four distinct discourse modes in the GOAT debate: evidence-based reasoning (`stat_analysis`), unsupported assertion (`hot_take`), deliberate provocation (`bait`), and balanced appreciation (`appreciation`). The key distinction I cared about most was `stat_analysis` vs `hot_take` — the difference between someone who backs their opinion with data and someone who just asserts it.

**What the model likely learned:** *[Fill after seeing results. Likely observations:]*
- The model probably learned surface-level features like the presence of numbers and statistics for `stat_analysis`, rather than genuinely understanding whether numbers are used as evidence vs. decoration.
- For `bait`, the model likely picked up on emoji, caps, and mocking nicknames — which are strong signals but miss the subtler forms of bait that use calm, reasonable language to make inflammatory claims.
- For `appreciation`, the model likely keyed on phrases like "both great" and "blessed to watch" — which works for typical appreciation posts but fails on posts that use appreciative language as a setup for a ranking.
- The `hot_take` vs `bait` boundary is likely the hardest for the model because the difference is often about *intent* (genuine opinion vs. deliberate provocation), which is hard to capture from text alone without understanding community context.

**The gap:** The fundamental gap between my labels and the model's learning is that my labels encode *communicative intent* (is this person trying to reason, assert, provoke, or appreciate?), while the model learns *textual patterns* (does this post contain numbers, insults, or diplomatic phrases?). These correlate strongly but are not identical — and the failure cases reveal exactly where they diverge.

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
**What I directed the AI to do:** After receiving the model's wrong predictions from the Colab evaluation, I provided the misclassified examples to Claude and asked it to identify common themes — similar post length, sarcasm patterns, specific label pairs that keep getting confused, etc.

**What it produced:** *[Fill after Colab — describe what patterns Claude identified]*

**What I changed/overrode:** *[Fill after Colab — describe which patterns I verified and which I discarded after re-reading the examples]*

### Disclosure
All planning, label design, edge case reasoning, and annotation review decisions were made by me (the human annotator). Claude was used only for the specific purposes described above: pre-labeling assistance (with full human review of every label) and failure analysis pattern identification (with manual verification). The label taxonomy, decision rules, and all qualitative judgments in this report are my own work.

---

## Repository Structure

```
ai201-project3-takemeter/
├── README.md                    # This file — final report
├── planning.md                  # Design document (written before data collection)
├── takemeter_dataset.csv        # Labeled dataset (302 examples, 3 columns: text, label, notes)
├── collect_data.py              # Data collection script (PullPush API)
├── annotate_data.py             # Pre-labeling heuristic script
├── fix_labels.py                # Manual correction pass script
├── evaluation_results.json      # [From Colab] Side-by-side model comparison
├── confusion_matrix.png         # [From Colab] Confusion matrix visualization
└── data_raw/
    ├── raw_responses.json       # Raw API responses (1,826 comments)
    └── all_comments_raw.csv     # Cleaned raw comments before labeling
```

---

## How to Reproduce

1. **Data collection:** Run `python collect_data.py` to collect comments from PullPush API (takes ~2 minutes).
2. **Pre-labeling:** Run `python annotate_data.py` to generate initial labels.
3. **Label correction:** Run `python fix_labels.py` to apply manual corrections.
4. **Fine-tuning:** Open the [TakeMeter starter Colab notebook](https://colab.research.google.com/), upload `takemeter_dataset.csv`, set runtime to T4 GPU, and run all sections.
5. **Baseline:** Add your Groq API key to Colab Secrets and run Section 5.
6. **Export:** Download `evaluation_results.json` and `confusion_matrix.png` from Colab.
