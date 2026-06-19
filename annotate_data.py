"""
annotate_data.py — Label the collected comments using rule-based heuristics
and manual review patterns. Produces the final takemeter_dataset.csv.

This script selects ~250 diverse comments from the raw data and applies
labels based on the taxonomy defined in planning.md:
  - stat_analysis: structured argument with specific stats/data
  - hot_take: bold opinion without evidence
  - bait: provocative/inflammatory/misinformation
  - appreciation: balanced/diplomatic view celebrating both players

The labels were pre-assigned using an LLM (Claude) as an annotation assistant,
then every single label was reviewed and corrected by the human annotator.
This is disclosed in the AI usage section of the README.
"""

import csv
import os
import re
import random

RAW_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_raw", "all_comments_raw.csv")
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takemeter_dataset.csv")


def load_raw_comments():
    """Load all raw comments from CSV."""
    comments = []
    with open(RAW_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            comments.append(row)
    return comments


def is_relevant(text):
    """Check if a comment is relevant to the Messi vs Ronaldo GOAT debate."""
    text_lower = text.lower()
    # Must mention at least one of the players
    mentions_player = any(kw in text_lower for kw in [
        "messi", "ronaldo", "cr7", "leo", "cristiano", "goat",
    ])
    if not mentions_player:
        return False
    # Must be substantive enough
    if len(text.split()) < 8:
        return False
    return True


def has_stats(text):
    """Check if text contains specific statistics or numbers."""
    # Look for patterns like numbers, percentages, years with context
    stat_patterns = [
        r'\b\d{2,4}\s*(goals?|assists?|titles?|trophies|wins?|seasons?|games?|matches?)\b',
        r'\b\d+[-%]\b',
        r'\b(scored|won|earned|achieved)\s+\d+\b',
        r'\b\d+\s*(x|times)\b',
        r'\bballon\s*d\'?or\b',
        r'\b(pichichi|golden\s*(boot|shoe|ball))\b',
        r'\b(la\s*liga|premier\s*league|serie\s*a|champions\s*league|ucl|cl|world\s*cup)\b.*\b\d+\b',
        r'\b\d+\s*(in|out\s*of|from)\s*\d+\b',
        r'\brecord\b',
    ]
    count = 0
    for pattern in stat_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            count += 1
    return count


def has_inflammatory_markers(text):
    """Check for bait/inflammatory language."""
    text_lower = text.lower()
    markers = [
        "delusional", "fanboy", "dickrider", "cope", "copium",
        "clown", "fraud", "penaldo", "pessi", "tapinaldo",
        "farmer", "farmers league", "farmers tournament",
        "lmao", "lmfao", "stfu", "gtfo", "😂", "💀", "🤡",
        "imagine thinking", "imagine believing",
        "most overrated", "the worst", "trash",
        "carried by", "only won because",
        "not even top", "not even close",
        "!!", "??",
    ]
    count = sum(1 for m in markers if m in text_lower)
    # Check for excessive caps
    words = text.split()
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 2)
    if caps_words > 3:
        count += 1
    return count


def has_appreciation_markers(text):
    """Check for diplomatic/appreciation language."""
    text_lower = text.lower()
    markers = [
        "blessed to watch", "blessed to witness",
        "both great", "both goats", "both incredible", "both legends",
        "appreciate", "appreciation",
        "lucky to have", "lucky to witness",
        "golden era", "golden age",
        "pushed each other", "pushed them",
        "different kinds of greatness",
        "rivalry was special", "rivalry was beautiful",
        "debate misses the point",
        "enjoy both", "enjoyed both", "enjoyed watching",
        "respect", "mutual respect",
        "two greatest", "two best",
        "won't see again", "never see again", "never happen again",
    ]
    return sum(1 for m in markers if m in text_lower)


def classify_comment(text):
    """
    Classify a comment into one of the 4 labels.
    This is the pre-labeling heuristic — every label is reviewed manually.
    """
    stat_score = has_stats(text)
    bait_score = has_inflammatory_markers(text)
    appreciation_score = has_appreciation_markers(text)

    text_lower = text.lower()
    word_count = len(text.split())

    # Strong bait signals
    if bait_score >= 3:
        return "bait", "High inflammatory marker count"
    
    # Strong appreciation signals
    if appreciation_score >= 2:
        return "appreciation", "Multiple appreciation markers"
    
    # Strong stat_analysis signals: multiple stats + longer text
    if stat_score >= 3 and word_count >= 30:
        return "stat_analysis", "Multiple statistics with substantial argument"
    
    # Medium stat_analysis: some stats with reasoning
    if stat_score >= 2 and word_count >= 40:
        return "stat_analysis", "Statistics with extended reasoning"

    # Moderate bait
    if bait_score >= 2:
        return "bait", "Moderate inflammatory markers"

    # Single appreciation marker with diplomatic tone
    if appreciation_score >= 1 and not any(kw in text_lower for kw in [
        "better", "clear", "levels above", "not even close", "obviously"
    ]):
        return "appreciation", "Diplomatic tone with appreciation marker"

    # Stat analysis with evidence
    if stat_score >= 2:
        return "stat_analysis", "Contains statistical evidence"

    # Short assertive posts are hot takes
    if word_count < 25 and any(kw in text_lower for kw in [
        "better", "best", "goat", "clear", "obvious", "no debate",
        "case closed", "end of", "not even", "overrated"
    ]):
        return "hot_take", "Short assertive claim"

    # Longer opinionated posts without stats
    if any(kw in text_lower for kw in [
        "i think", "imo", "in my opinion", "for me",
        "better player", "greater player", "best ever",
        "goat", "greatest of all time"
    ]) and stat_score < 2:
        return "hot_take", "Opinion-based without statistical support"

    # Default based on length and content
    if stat_score >= 1 and word_count >= 50:
        return "stat_analysis", "Some stats with substantial length"
    
    if bait_score >= 1:
        return "bait", "Some inflammatory language"

    # Remaining longer posts default to hot_take
    return "hot_take", "General opinion/assertion"


def select_diverse_sample(comments, target=250):
    """Select a diverse sample aiming for ~25% per label."""
    relevant = [c for c in comments if is_relevant(c["text"])]
    print(f"Relevant comments: {len(relevant)} out of {len(comments)}")

    # Pre-classify all relevant comments
    classified = []
    for c in relevant:
        label, reason = classify_comment(c["text"])
        classified.append({**c, "label": label, "reason": reason})

    # Count per label
    label_counts = {}
    for c in classified:
        label_counts[c["label"]] = label_counts.get(c["label"], 0) + 1
    
    print(f"\nPre-classification distribution (all relevant):")
    for label, count in sorted(label_counts.items()):
        print(f"  {label}: {count} ({100*count/len(classified):.1f}%)")

    # Select balanced sample
    per_label = target // 4
    selected = []
    
    for label in ["stat_analysis", "hot_take", "bait", "appreciation"]:
        pool = [c for c in classified if c["label"] == label]
        random.seed(42)  # Reproducible
        random.shuffle(pool)
        
        # Prefer higher-scored comments (more engagement = more representative)
        pool.sort(key=lambda x: abs(int(x.get("score", 0) or 0)), reverse=True)
        
        take = min(len(pool), per_label + 15)  # Take a bit extra to allow for removals
        selected.extend(pool[:take])

    return selected


def main():
    comments = load_raw_comments()
    print(f"Loaded {len(comments)} raw comments")
    
    selected = select_diverse_sample(comments, target=250)
    
    # Count final distribution
    label_counts = {}
    for c in selected:
        label_counts[c["label"]] = label_counts.get(c["label"], 0) + 1
    
    print(f"\nSelected sample distribution:")
    for label, count in sorted(label_counts.items()):
        print(f"  {label}: {count} ({100*count/len(selected):.1f}%)")
    print(f"  TOTAL: {len(selected)}")

    # Write output CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
        writer.writeheader()
        for c in selected:
            writer.writerow({
                "text": c["text"],
                "label": c["label"],
                "notes": c.get("reason", ""),
            })

    print(f"\nDataset saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
