def get_score(dice):
    from collections import Counter

    # Scoring rules
    score_map = {
        1: (1000, 200),  # (three of a kind score, two of a kind score)
        2: (200, 0),
        3: (300, 0),
        4: (400, 0),
        5: (500, 100),  # (three of a kind score, single score)
        6: (600, 0)
    }

    # Count occurrences of each die
    counts = Counter(dice)

    total_score = 0

    # Check for straight
    if sorted(counts.keys()) == [1, 2, 3, 4, 5, 6] and len(counts) == 6:
        return 1000

    # Check for three pairs
    pairs = sum(1 for count in counts.values() if count == 2)
    if pairs == 3:
        return 750

    # Calculate scores for three of a kind, four of a kind, five of a kind, and singles
    for die, count in counts.items():
        if count >= 3:
            three_of_a_kind_score = score_map[die][0]
            total_score += three_of_a_kind_score
            # Calculate additional scores for four, five, and six of a kind
            if count == 4:
                total_score += three_of_a_kind_score  # 2 * three of a kind
            elif count == 5:
                total_score += 2 * three_of_a_kind_score  # 3 * three of a kind
            elif count == 6:
                total_score += 3 * three_of_a_kind_score  # 4 * three of a kind

        # Handle singles for 1s and 5s
        if die == 1 and count == 1:
            total_score += score_map[1][1]  # single 1
        elif die == 5 and count == 1:
            total_score += score_map[5][1]  # single 5
        elif count == 2 and die in (1, 5):
            total_score += score_map[die][1]  # two of a kind for 1s or 5s

    return total_score if total_score > 0 else "Zonk"

print(get_score())