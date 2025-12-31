def generate_reason_breakdown(tags, user_interests, breakdown, decayed_tags, diversity_penalty=0):
    reasons = []

    for tag in tags:
        if tag in breakdown:
            reasons.append(
                f"• You’re interested in **{tag}** (+{round(breakdown[tag], 2)})"
            )

        if tag in decayed_tags:
            reasons.append(
                f"• Your interest in **{tag}** has slightly decreased due to inactivity"
            )

    if diversity_penalty < 0:
        reasons.append("• Shown to keep your feed diverse")

    if not reasons:
        reasons.append("• This post is shown to explore new topics")

    return reasons
