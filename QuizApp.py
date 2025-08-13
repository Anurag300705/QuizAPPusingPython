# quiz_any_topic.py
"""
CLI Quiz Application using Open Trivia DB (https://opentdb.com)
- User can specify any topic (we'll fuzzy-match it to available categories)
- Choose number of questions, difficulty, and type
- Shuffles options, decodes HTML entities, keeps score, and shows summary
"""

import random
import html
import sys
import difflib
from typing import List, Dict, Optional
try:
    import requests
except ImportError:
    print("The 'requests' package is required. Install it with:\n  pip install requests")
    sys.exit(1)


OTDB_CATEGORIES_URL = "https://opentdb.com/api_category.php"
OTDB_API_URL = "https://opentdb.com/api.php"

def fetch_categories() -> List[Dict]:
    """Fetch available categories from Open Trivia DB."""
    try:
        resp = requests.get(OTDB_CATEGORIES_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("trivia_categories", [])
    except Exception as e:
        print(f"⚠ Could not fetch categories: {e}")
        return []

def match_category(topic: str, categories: List[Dict]) -> Optional[Dict]:
    """
    Fuzzy-match the user's topic to the closest category.
    Returns the matched category dict or None if no decent match.
    """
    if not categories or not topic.strip():
        return None

    names = [c["name"] for c in categories]
    # Try strong match first
    best = difflib.get_close_matches(topic, names, n=1, cutoff=0.6)
    if best:
        name = best[0]
        for c in categories:
            if c["name"] == name:
                return c

    # Weak keyword containment as a backup
    topic_lower = topic.lower()
    partials = [c for c in categories if topic_lower in c["name"].lower()]
    if partials:
        return partials[0]
    return None

def fetch_questions(amount: int = 10,
                    category_id: Optional[int] = None,
                    difficulty: Optional[str] = None,
                    qtype: Optional[str] = None) -> List[Dict]:
    """
    Fetch questions from Open Trivia DB.
    - difficulty: "easy", "medium", "hard", or None
    - qtype: "multiple", "boolean", or None
    """
    params = {"amount": max(1, min(amount, 50))}  # OTDB max is 50
    if category_id:
        params["category"] = category_id
    if difficulty and difficulty.lower() in {"easy", "medium", "hard"}:
        params["difficulty"] = difficulty.lower()
    if qtype and qtype.lower() in {"multiple", "boolean"}:
        params["type"] = qtype.lower()

    try:
        resp = requests.get(OTDB_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        response_code = data.get("response_code", 1)
        if response_code != 0:
            # 1: No Results, 2: Invalid Parameter, 3: Token Not Found, 4: Token Empty
            return []
        return data.get("results", [])
    except Exception as e:
        print(f"⚠ Could not fetch questions: {e}")
        return []

def normalize_question(q: Dict) -> Dict:
    """Convert API question to our internal structure and decode HTML entities."""
    question_text = html.unescape(q.get("question", ""))
    correct = html.unescape(q.get("correct_answer", ""))
    incorrect = [html.unescape(x) for x in q.get("incorrect_answers", [])]
    all_options = incorrect + [correct]
    random.shuffle(all_options)
    return {
        "question": question_text,
        "options": all_options,
        "answer": correct,
        "type": q.get("type", "multiple"),
        "difficulty": q.get("difficulty", "unknown"),
        "category": q.get("category", "General")
    }

def prompt_int(msg: str, default: int, lo: int, hi: int) -> int:
    """Prompt for an integer with bounds and default."""
    while True:
        raw = input(f"{msg} [{default}]: ").strip()
        if not raw:
            return default
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            print(f"Enter a number between {lo} and {hi}.")
        except ValueError:
            print("Enter a valid integer.")

def prompt_choice(msg: str, choices: List[str], default: str) -> str:
    """Prompt for a choice (case-insensitive)."""
    choices_lower = [c.lower() for c in choices]
    default_lower = default.lower()
    while True:
        raw = input(f"{msg} {choices} [{default}]: ").strip().lower()
        if not raw:
            return default_lower
        if raw in choices_lower:
            return raw
        print(f"Choose one of {choices} (case-insensitive).")

def run_quiz(questions: List[Dict]):
    score = 0
    print("\n🔹 Starting Quiz! Good luck!\n")
    for idx, q in enumerate(questions, start=1):
        print(f"Q{idx} ({q.get('category', 'General')} - {q.get('difficulty', 'unknown').title()}):")
        print(q["question"])

        # True/False questions sometimes come with only 2 options; ensure numbered menu
        for i, option in enumerate(q["options"], start=1):
            print(f"  {i}. {option}")

        while True:
            try:
                ans = int(input("Your answer (enter option number): "))
                if 1 <= ans <= len(q["options"]):
                    break
                print(f"Enter a number between 1 and {len(q['options'])}.")
            except ValueError:
                print("Please enter a valid number.")

        chosen = q["options"][ans - 1]
        if chosen == q["answer"]:
            print("✅ Correct!\n")
            score += 1
        else:
            print(f"❌ Wrong. Correct answer: {q['answer']}\n")

    print("🏁 Quiz Finished!")
    print(f"Your Score: {score}/{len(questions)}")
    pct = (score / len(questions)) * 100 if questions else 0
    if pct == 100:
        print("🎉 Perfect! You nailed it!")
    elif pct >= 70:
        print("👏 Great job! Keep it up.")
    elif pct >= 40:
        print("👍 Not bad—practice makes perfect.")
    else:
        print("📚 Keep learning—you’ll improve fast!")

def main():
    print("\n====== Any-Topic Quiz (Open Trivia DB) ======\n")
    topic = input("Enter a topic (e.g., 'history', 'science', 'sports', or leave blank for random): ").strip()

    amount = prompt_int("How many questions? (1–50)", default=10, lo=1, hi=50)
    difficulty = prompt_choice("Difficulty?", ["any", "easy", "medium", "hard"], default="any")
    qtype = prompt_choice("Type?", ["any", "multiple", "boolean"], default="any")

    # Fetch categories and match
    categories = fetch_categories()
    matched = match_category(topic, categories) if topic else None
    if matched:
        print(f"🔎 Matched topic to category: {matched['name']} (id {matched['id']})")
    else:
        if topic:
            print("ℹ No close category found. Using random categories instead.")
        else:
            print("ℹ Random topic selected.")

    # Fetch questions
    cat_id = matched["id"] if matched else None
    cat_questions = fetch_questions(amount=amount,
                                    category_id=cat_id,
                                    difficulty=(None if difficulty == "any" else difficulty),
                                    qtype=(None if qtype == "any" else qtype))

    # If no results, try without category/difficulty/type as fallbacks
    if not cat_questions:
        print("⚠ No questions found for that selection. Trying broader search...")
        cat_questions = fetch_questions(amount=amount,
                                        category_id=None,
                                        difficulty=(None if difficulty == "any" else difficulty),
                                        qtype=(None if qtype == "any" else qtype))
    if not cat_questions:
        print("⚠ Still no questions. Trying fully random...")
        cat_questions = fetch_questions(amount=amount)

    if not cat_questions:
        # Final offline fallback
        print("❌ Could not fetch questions from the API. Using a tiny offline set.")
        offline = [
            {
                "category": "General",
                "type": "multiple",
                "difficulty": "easy",
                "question": "What is the capital of France?",
                "correct_answer": "Paris",
                "incorrect_answers": ["Berlin", "Madrid", "Lisbon"],
            },
            {
                "category": "Science",
                "type": "boolean",
                "difficulty": "easy",
                "question": "The chemical symbol for Gold is Au.",
                "correct_answer": "True",
                "incorrect_answers": ["False"],
            },
        ]
        questions = [normalize_question(q) for q in offline]
    else:
        questions = [normalize_question(q) for q in cat_questions]

    random.shuffle(questions)
    run_quiz(questions)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Quiz cancelled.")
