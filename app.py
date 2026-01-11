import streamlit as st

from recommender import (
    update_user_interests,
    decrease_user_interests,
    rank_posts,
    decay_user_interests
)
from llm_utils import explain_recommendation
from storage import load_interests, save_interests
from explanations import generate_reason_breakdown
from confidence import interest_confidence
import pandas as pd
import os
from storage import (
    load_interests,
    save_interests,
    load_saved_posts,
    save_saved_posts
)


st.set_page_config(page_title="SmartFeed AI", layout="wide")
st.title("📱SmartFeed AI")


st.markdown("""
<style>
/* Tag-style buttons */
div[data-testid="column"] button {
    border-radius: 999px !important;
    padding: 6px 14px !important;
    border: 1px solid #333 !important;
    background-color: #111 !important;
    color: white !important;
}

/* Align buttons inside columns */
.like-col {
    display: flex;
    justify-content: flex-start;
}
.center-col {
    display: flex;
    justify-content: center;
}
.save-col {
    display: flex;
    justify-content: flex-end;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Center feed */
.feed-wrapper {
    display: flex;
    justify-content: center;
}

/* Post card */
.post-card {
    width: 360px;
    padding: 12px;
    border-radius: 14px;
    background-color: #111418;
    border: 1px solid #2a2f36;
}

/* Title */
.post-title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 8px;
}

/* Media FIX — THIS IS THE KEY */
.post-card img,
.post-card video {
    width: 100% !important;
    max-width: 100% !important;
    height: auto !important;
    border-radius: 10px;
    display: block;
}
/* Force Streamlit media wrapper to obey container width */
div[data-testid="stImage"],
div[data-testid="stVideo"] {
    width: 100% !important;
}

.tag-container {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 4px;
}

.tag-btn {
    background-color: #1f2933;
    border: 1px solid #374151;
    color: white;
    padding: 6px 12px;
    border-radius: 12px;
    cursor: pointer;
    font-size: 13px;
}

.tag-btn:hover {
    background-color: #374151;
}


/* Buttons */
.action-row {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POSTS = [
    {
        "id": 1,
        "type": "video",
        "file": os.path.join(BASE_DIR, "assets", "posts", "cook", "bake.mp4"),
        "title": "Baking therapy 🧁",
        "tags": ["food", "baking", "dessert","muffin","recipe"]
    },
    {
        "id": 2,
        "type": "video",
        "file": os.path.join(BASE_DIR, "assets", "posts", "cook", "dessert1.mp4"),
        "title": "Dessert ASMR 🍰",
        "tags": ["food", "dessert", "ASMR" , "eating"]
    },
    {
        "id": 3,
        "type": "video",
        "file": os.path.join(BASE_DIR, "assets", "posts", "cook", "pizza.mp4"),
        "title": "Homemade pizza supremacy 🍕",
        "tags": ["food", "pizza", "eating" , "ASMR"]
    },
    {
        "id": 4,
        "type": "image",
        "file": os.path.join(BASE_DIR, "assets", "posts", "memes", "spider.png"),
        "title": "That one fear you never recover from 🕷️",
        "tags": ["meme", "dark-humor" , "funny" , "sarcasm"]
    },
    {
        "id": 5,
        "type": "image",
        "file": os.path.join(BASE_DIR, "assets", "posts", "memes", "monday.png"),
        "title": "Mondays should be illegal 😭",
        "tags": ["meme", "relatable" , "lazy" , "funny"]
    },
    {
        "id": 6,
        "type": "image",
        "file": os.path.join(BASE_DIR, "assets", "posts", "memes", "zoom.png"),
        "title": "Online meetings be like 💀",
        "tags": ["meme", "college" , "work" , "funny" ]
    },
    {
        "id": 7,
        "type": "image",
        "file": os.path.join(BASE_DIR, "assets", "posts", "movie", "cast.jpg"),
        "title": "This cast >>> 🔥",
        "tags": ["Dhurandhar" , "movie", "celebrity" , "cast" , "real vs reel"]
    },
    {
        "id": 8,
        "type": "image",
        "file": os.path.join(BASE_DIR, "assets", "posts", "movie", "record.jpg"),
        "title": "Breaking records already 👀",
        "tags": ["Dhurandhar" , "movie", "news" , "record" , "success"]
    },
    {
        "id": 9,
        "type": "video",
        "file": os.path.join(BASE_DIR, "assets", "posts", "travel", "bali.mp4"),
        "title": "Bali is always a good idea 🌴",
        "tags": ["Bali" , "travel", "vacation" , "relax"]
    },
    {
        "id": 10,
        "type": "video",
        "file": os.path.join(BASE_DIR, "assets", "posts", "travel", "india.mp4"),
        "title": "Hidden gems of India 💎",
        "tags": ["India" , "travel", "explore","sponsored"]
    }
]

search_query = st.text_input("🔍 Search posts by keyword or tag")
btn_left, btn_right = st.columns([1, 1])

with btn_left:
    if st.button("🔄 Reset Feed & Interests", use_container_width=True):
        st.session_state.user_interests = {}
        st.session_state.liked_posts = set()
        st.session_state.post_actions = {}
        st.session_state.recent_tags = []
        save_interests({})
        st.rerun()

with btn_right:
    if st.button("💾 View Saved Posts", use_container_width=True):
        st.session_state.show_saved_posts = True
        st.rerun()

st.subheader("🎛️ Feed Preference")

explore_ratio = st.slider(
    "Explore new content vs show what I like",
    min_value=0.0,
    max_value=0.5,
    value=0.2,
    step=0.05
)


if "user_interests" not in st.session_state:
    st.session_state.user_interests = load_interests()

if "decay_done" not in st.session_state:
    st.session_state.user_interests, st.session_state.decayed_tags = decay_user_interests(
        st.session_state.user_interests
    )
    st.session_state.decay_done = True

if "decayed_tags" not in st.session_state:
    st.session_state.decayed_tags = set()

if "recent_boosted_tags" not in st.session_state:
    st.session_state.recent_boosted_tags = set()

if "recent_tags" not in st.session_state:
    st.session_state.recent_tags = []

if "liked_posts" not in st.session_state:
    st.session_state.liked_posts = set()

if "post_actions" not in st.session_state:
    st.session_state.post_actions = {}

if "saved_posts" not in st.session_state:
    st.session_state.saved_posts = load_saved_posts()
    
if "show_saved_posts" not in st.session_state:
    st.session_state.show_saved_posts = False


if "active_tag_filter" not in st.session_state:
    st.session_state.active_tag_filter = None
    
if "llm_explanations" not in st.session_state:
    st.session_state.llm_explanations = {}

if "just_interacted" not in st.session_state:
    st.session_state.just_interacted = False


effective_explore_ratio = explore_ratio

ranked_posts = rank_posts(
    POSTS,
    st.session_state.user_interests,
    explore_ratio=effective_explore_ratio,
    recent_boosted_tags=st.session_state.recent_boosted_tags,
    recent_tags=st.session_state.recent_tags
)


if search_query:
    ranked_posts = [
        post for post in ranked_posts
        if search_query.lower() in post["title"].lower()
        or any(search_query.lower() in tag.lower() for tag in post["tags"])
    ]

if st.session_state.active_tag_filter:
    ranked_posts = [
        post for post in ranked_posts
        if st.session_state.active_tag_filter in post["tags"]
    ]

if st.session_state.active_tag_filter:
    st.info(f"Filtering by tag: #{st.session_state.active_tag_filter}")

    if st.button("❌ Clear tag filter"):
        st.session_state.active_tag_filter = None
        st.rerun()

if st.session_state.show_saved_posts:
    st.divider()
    st.subheader("💾 Saved Posts")

    if not st.session_state.saved_posts:
        st.info("No saved posts yet 👀")
    else:
        for post in POSTS:
            if post["id"] in st.session_state.saved_posts:

                left, center, right = st.columns([1, 2, 1])

                with center:
                    with st.container(border=True):

                        st.markdown(f"**{post['title']}**")

                        if post["type"] == "image":
                            st.image(post["file"], use_container_width=True)
                        else:
                            st.video(post["file"])

                        st.caption(f"🏷️ {', '.join(post['tags'])}")

                        if st.button(
                            "❌ Remove from Saved",
                            key=f"unsave_saved_view_{post['id']}"
                        ):
                            st.session_state.saved_posts.remove(post["id"])
                            save_saved_posts(st.session_state.saved_posts)
                            st.rerun()

    if st.button("⬅️ Back to Feed"):
        st.session_state.show_saved_posts = False
        st.rerun()

    st.stop()

for index, post in enumerate(ranked_posts):

    left, center, right = st.columns([1, 2, 1])

    with center:
        with st.container(border=True):

            title = post["title"]
            tags = post["tags"]
            score = post.get("score", 0)
            breakdown = post.get("breakdown", {})
            post_id = post["id"]

            st.markdown(f"**{title}**")

            if post["type"] == "image":
                st.image(post["file"], use_container_width=True)
            elif post["type"] == "video":
                st.video(post["file"])
            
            st.markdown("🏷️ Tags:")
            tag_cols = st.columns(len(tags), gap="small")

            for i, tag in enumerate(tags):
                with tag_cols[i]:
                    if st.button(
            tag,
            key=f"tag_{post_id}_{tag}",
            use_container_width=True
        ):
                        st.session_state.active_tag_filter = tag
                        st.rerun()



            st.caption(f"🔢 Match score: {round(score, 2)}")

            if st.session_state.user_interests:
                with st.expander("🤖 Why am I seeing this?"):
                    reasons = generate_reason_breakdown(
        tags,
        st.session_state.user_interests,
        breakdown,
        st.session_state.decayed_tags
    )
                    for r in reasons:
                        st.write(r)
                    st.divider()

                    try:
                        explanation = explain_recommendation(
            title,
            tags,
            st.session_state.user_interests
        )
                    except Exception:
                        explanation = "⚠️ AI explanation temporarily unavailable (rate limit)."
                    st.write(explanation)
            
            action = st.session_state.post_actions.get(post_id)

            col1, col2, col_spacer, col3 = st.columns([1, 1, 3, 1])

            if action is None:

                with col1:
                    if st.button("❤️ Like", key=f"like_{post_id}"):

                        st.session_state.post_actions[post_id] = "like"

                        st.session_state.user_interests = update_user_interests(
                            st.session_state.user_interests, tags
                        )

                        st.session_state.recent_tags.extend(tags)
                        st.session_state.recent_tags = st.session_state.recent_tags[-5:]

                        st.session_state.just_interacted = True

                        save_interests(st.session_state.user_interests)
                        st.rerun()

                with col2:
                    if st.button("👎 Skip", key=f"dislike_{post_id}"):
                        st.session_state.post_actions[post_id] = "dislike"
                        st.session_state.user_interests = decrease_user_interests(
                            st.session_state.user_interests, tags
                        )

                        save_interests(st.session_state.user_interests)
                        st.rerun()

            else:
                with col1:
                    if st.button("↩️ Undo", key=f"undo_{post_id}"):
                        if action == "like":
                            st.session_state.user_interests = decrease_user_interests(
                                st.session_state.user_interests, tags
                            )
                        elif action == "dislike":
                            st.session_state.user_interests = update_user_interests(
                                st.session_state.user_interests, tags
                            )

                        del st.session_state.post_actions[post_id]
                        save_interests(st.session_state.user_interests)
                        st.rerun()

            with col3:
                if post_id in st.session_state.saved_posts:
                    if st.button("💾 Saved", key=f"unsave_{post_id}"):
                        st.session_state.saved_posts.remove(post_id)
                        save_saved_posts(st.session_state.saved_posts)
                        st.rerun()
                else:
                    if st.button("💾 Save", key=f"save_{post_id}"):
                        st.session_state.saved_posts.add(post_id)
                        save_saved_posts(st.session_state.saved_posts)
                        st.rerun()

st.divider()
st.subheader("🧠 Your Interest Profile")

if st.session_state.user_interests:
    for tag, data in st.session_state.user_interests.items():
        score = data.get("score", 0)
        confidence = interest_confidence(score)
        st.write(f"• **{tag.upper()}** → {round(score, 2)} {confidence}")
else:
    st.write("Like some posts to build your profile 👆")

if st.session_state.user_interests:
    chart_data = {
        tag.upper(): data.get("score", 0)
        for tag, data in st.session_state.user_interests.items()
    }

    df = pd.DataFrame.from_dict(
        chart_data,
        orient="index",
        columns=["Interest Strength"]
    )

    st.bar_chart(df)

