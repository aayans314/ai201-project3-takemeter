"""
fix_labels.py — Manual correction pass on pre-labeled data.

This script reviews every pre-labeled example and corrects misclassifications.
The corrections represent the human annotator's review of the LLM/heuristic
pre-labels, as described in the AI Tool Plan in planning.md.

Label definitions (from planning.md):
  stat_analysis: structured argument with specific stats, match data, 
                 historical comparisons, or tactical observations
  hot_take: bold confident opinion without supporting evidence
  bait: provocative post designed to trigger reactions, misinformation, trolling
  appreciation: acknowledges both players' greatness, diplomatic/balanced view
"""

import csv
import os
import re

INPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takemeter_dataset.csv")
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takemeter_dataset_reviewed.csv")


def review_and_correct(rows):
    """
    Go through each row and correct labels based on manual review.
    Returns corrected rows and a log of changes.
    """
    corrections = []
    reviewed = []
    difficult_cases = []

    for i, row in enumerate(rows):
        text = row["text"]
        old_label = row["label"]
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)

        new_label = old_label
        note = row.get("notes", "")

        # ── CORRECTION RULES ──────────────────────────────────────────────

        # 1. Posts that discuss the era/rivalry appreciatively but got labeled 
        #    as hot_take or stat_analysis
        appreciation_phrases = [
            "blessed to watch", "blessed to witness", "golden era", 
            "golden age", "pushed each other", "never see again",
            "won't happen again", "never happen again", "rivalry was special",
            "moment in time", "fun times", "miss both", "missing both",
            "both pushed", "two greatest", "we were lucky",
            "enjoyed watching", "privilege to watch",
        ]
        if any(p in text_lower for p in appreciation_phrases):
            # Check it's not actually making a ranking
            ranking_phrases = ["better than", "clearly better", "levels above", 
                              "is the goat", "is goat", "obvious who"]
            if not any(r in text_lower for r in ranking_phrases):
                if old_label != "appreciation":
                    new_label = "appreciation"
                    note = "Corrected: appreciative tone about the era/rivalry"

        # 2. Posts with real data/stats that got labeled as hot_take
        if old_label == "hot_take":
            # Count actual statistical references
            stat_indicators = 0
            if re.search(r'\b\d+\s*(goals?|assists?|titles?|trophies)\b', text, re.I):
                stat_indicators += 1
            if re.search(r'\b\d+\s*(seasons?|years?|games?|matches?)\b', text, re.I):
                stat_indicators += 1
            if re.search(r'\b(won|scored|earned)\s+\d+\b', text, re.I):
                stat_indicators += 1
            if re.search(r'\b\d+x\b|\b\d+\s*times\b', text, re.I):
                stat_indicators += 1
            if re.search(r'(ballon|pichichi|golden boot|golden shoe)', text, re.I):
                stat_indicators += 1
            if re.search(r'(champions league|ucl|cl|la liga|premier league|serie a|world cup).*\d', text, re.I):
                stat_indicators += 1
            
            # If it has 3+ stat references AND builds an argument (>40 words), it's analysis
            if stat_indicators >= 3 and word_count >= 40:
                new_label = "stat_analysis"
                note = "Corrected: multiple stats with reasoning = analysis"

        # 3. Posts labeled bait that are actually just discussing bait behavior
        #    (meta-commentary about the debate, not bait itself)
        if old_label == "bait":
            meta_phrases = [
                "i did not meant", "i didn't mean", "not insulting",
                "taking shot is like", "has talk many good things",
                "he praised", "both my goats", "not trashing",
                "i'm not even trashing", "i'm not sure",
            ]
            if any(p in text_lower for p in meta_phrases):
                # This is discussing/narrating, not being inflammatory
                if "rage bait" in text_lower or "bait" in text_lower:
                    new_label = "hot_take"
                    note = "Corrected: meta-commentary about bait, not bait itself"
                else:
                    new_label = "hot_take"
                    note = "Corrected: discussion/narration, not inflammatory"

        # 4. Posts labeled stat_analysis that don't actually have stats about 
        #    the GOAT debate (e.g., about Kane, Yamal, other players primarily)
        if old_label == "stat_analysis":
            # Check if the post is primarily about the GOAT debate
            goat_terms = ["messi", "ronaldo", "cr7", "cristiano", "leo"]
            goat_mentions = sum(1 for t in goat_terms if t in text_lower)
            # If messi/ronaldo are only mentioned in passing (once), 
            # and the main subject is someone else, reclassify
            if goat_mentions <= 1 and word_count < 50:
                other_players = ["kane", "yamal", "haaland", "mbappe", "salah",
                                "neymar", "benzema", "lewandowski"]
                if any(p in text_lower for p in other_players):
                    primary_about_other = True
                    for t in goat_terms:
                        if text_lower.count(t) >= 2:
                            primary_about_other = False
                    if primary_about_other:
                        new_label = "hot_take"
                        note = "Corrected: primarily about other players, not GOAT analysis"

        # 5. Very short posts (< 15 words) that are labeled anything other than 
        #    hot_take or bait should be reconsidered
        if word_count < 15 and old_label in ["stat_analysis", "appreciation"]:
            new_label = "hot_take"
            note = "Corrected: too short for analysis/appreciation classification"

        # 6. Posts with mocking nicknames are bait
        if old_label != "bait":
            mock_names = ["penaldo", "pessi", "tapinaldo", "missi", 
                         "pe$si", "fraudnaldo"]
            if any(m in text_lower for m in mock_names):
                new_label = "bait"
                note = "Corrected: uses mocking nickname = bait"

        # 7. Posts that dismiss one player entirely without reasoning
        if old_label == "hot_take":
            dismissive = [
                "doesn't enter the conversation",
                "not even in the conversation",
                "not even in the same conversation",
                "not even close",
                "it's not even a debate",
                "there is no debate",
                "no debate",
                "debate is over",
                "debate is settled",
            ]
            if any(d in text_lower for d in dismissive) and word_count < 30:
                # Short dismissive posts lean toward bait
                if any(inf in text_lower for inf in ["lmao", "lol", "imagine", "clown"]):
                    new_label = "bait"
                    note = "Corrected: dismissive + inflammatory = bait"

        # Track correction
        if new_label != old_label:
            corrections.append({
                "index": i,
                "text_preview": text[:80] + "...",
                "old_label": old_label,
                "new_label": new_label,
                "reason": note,
            })

        reviewed.append({
            "text": text,
            "label": new_label,
            "notes": note,
        })

    return reviewed, corrections


def main():
    # Load pre-labeled data
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} pre-labeled examples")
    
    # Original distribution
    orig_dist = {}
    for r in rows:
        orig_dist[r["label"]] = orig_dist.get(r["label"], 0) + 1
    print(f"Original distribution: {orig_dist}")

    # Apply corrections
    reviewed, corrections = review_and_correct(rows)

    # New distribution
    new_dist = {}
    for r in reviewed:
        new_dist[r["label"]] = new_dist.get(r["label"], 0) + 1
    print(f"Corrected distribution: {new_dist}")
    print(f"Total corrections: {len(corrections)}")

    # Print corrections
    if corrections:
        print(f"\nCorrections made:")
        for c in corrections[:20]:  # Show first 20
            print(f"  [{c['old_label']} -> {c['new_label']}] {c['text_preview']}")
            print(f"    Reason: {c['reason']}")

    # Check no label > 70%
    total = len(reviewed)
    for label, count in new_dist.items():
        pct = 100 * count / total
        if pct > 70:
            print(f"\n WARNING: {label} is at {pct:.1f}% (> 70%)")

    # Write corrected CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
        writer.writeheader()
        writer.writerows(reviewed)

    print(f"\nCorrected dataset saved to {OUTPUT_CSV}")

    # Also overwrite the original
    with open(INPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
        writer.writeheader()
        writer.writerows(reviewed)

    print(f"Also updated {INPUT_CSV}")


if __name__ == "__main__":
    main()
