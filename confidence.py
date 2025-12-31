def interest_confidence(score):
    if score >= 2:
        return "🟢 Strong"
    elif score >= 1:
        return "🟡 Medium"
    else:
        return "🔴 Exploring"
