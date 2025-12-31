import json
import os

INTEREST_FILE = "user_interests.json"

def load_interests():
    if os.path.exists(INTEREST_FILE):
        with open(INTEREST_FILE, "r") as f:
            return json.load(f)
    return {}

def save_interests(interests):
    with open(INTEREST_FILE, "w") as f:
        json.dump(interests, f)

SAVED_FILE = "saved_posts.json"

def load_saved_posts():
    if os.path.exists(SAVED_FILE):
        with open(SAVED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_saved_posts(saved_posts):
    with open(SAVED_FILE, "w") as f:
        json.dump(list(saved_posts), f)
