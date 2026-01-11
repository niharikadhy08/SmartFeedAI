import random
import time

def confidence_multiplier(score):
    if score < 1.0:
        return 0.5
    elif score < 2.0:
        return 1.0
    else:
        return 1.2

def diversity_penalty(current_tags, recent_tags):
    if not recent_tags:
        return 0.0
    overlap = set(current_tags) & set(recent_tags)
    return -0.7 * len(overlap)

def novelty_score(post_tags, user_interests):
    score = 0.0
    for tag in post_tags:
        data = user_interests.get(tag)
        if data is None:
            score += 1.0
        elif isinstance(data, dict) and data.get("score", 0) < 1.0:
            score += 0.5
    return score

def update_user_interests(user_interests, tags):
    now = time.time()
    for tag in tags:
        if tag not in user_interests or not isinstance(user_interests[tag], dict):
            user_interests[tag] = {"score": 0.0, "last_seen": now}
        user_interests[tag]["score"] += 1.0
        user_interests[tag]["last_seen"] = now
    return user_interests

def rank_posts(posts, user_interests, explore_ratio=0.2,
               recent_boosted_tags=None, recent_tags=None):

    if recent_boosted_tags is None:
        recent_boosted_tags = set()

    ranked = []

    for post in posts:
        personalized_score = 0.0
        breakdown = {}

        for tag in post.get("tags", []):
            data = user_interests.get(tag)

            if isinstance(data, dict):
                base_score = data.get("score", 0.0)
            elif isinstance(data, (int, float)):
                base_score = float(data)
            else:
                continue

            if base_score <= 0:
                continue

            multiplier = confidence_multiplier(base_score)
            tag_score = base_score * multiplier

            if tag in recent_boosted_tags:
                tag_score *= 1.15

            breakdown[tag] = round(tag_score, 2)
            personalized_score += tag_score

        novelty = novelty_score(post.get("tags", []), user_interests)
        exploration_noise = random.uniform(0, 1)


        final_score = (
            (1 - explore_ratio) * personalized_score
            + explore_ratio * 3 * (novelty + exploration_noise)
        )


        diversity = diversity_penalty(post.get("tags", []), recent_tags or [])
        final_score += diversity

        ranked.append({
            **post,
            "score": round(final_score, 2),
            "breakdown": breakdown,
            "diversity_penalty": diversity
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked

def decrease_user_interests(user_interests, post_tags):
    now = time.time()
    for tag in post_tags:
        data = user_interests.get(tag)
        if isinstance(data, dict):
            data["score"] -= 0.5
            data["last_seen"] = now
            if data["score"] <= 0:
                del user_interests[tag]
    return user_interests

def decay_user_interests(user_interests, decay_rate=0.95, idle_time=60):
    now = time.time()
    decayed_tags = set()

    for tag, data in user_interests.items():
        if isinstance(data, dict):
            if now - data["last_seen"] > idle_time:
                old_score = data["score"]
                data["score"] *= decay_rate
                if data["score"] < old_score:
                    decayed_tags.add(tag)

    return user_interests, decayed_tags
