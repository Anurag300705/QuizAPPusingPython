# QuizApp

A command-line quiz application using [Open Trivia DB](https://opentdb.com).  
Users can specify any topic, number of questions, difficulty, and question type.  
The app fetches questions from the API, shuffles options, decodes HTML entities, keeps score, and shows a summary.

## Features

- Fuzzy topic matching to available trivia categories
- Select number of questions (1–50)
- Choose difficulty: any, easy, medium, hard
- Choose type: any, multiple choice, true/false
- Shuffles answer options for fairness
- Decodes HTML entities for readable questions
- Offline fallback if API is unavailable

## Requirements

- Python 3.7+
- `requests` library (`pip install requests`)

## Usage

```sh
python QuizApp.py
```

## Code Walkthrough

### Imports

- `random`, `html`, `sys`, `difflib`: Standard Python libraries for shuffling, decoding, system exit, and fuzzy matching.
- `requests`: For HTTP requests to the trivia API.
- `typing`: Type hints for clarity.

### Constants

- `OTDB_CATEGORIES_URL`: API endpoint for categories.
- `OTDB_API_URL`: API endpoint for questions.

### Functions

#### `fetch_categories()`
Fetches available trivia categories from the API.  
Handles errors gracefully and returns an empty list if the API is unreachable.

#### `match_category(topic, categories)`
Fuzzy-matches the user's topic to the closest available category using `difflib.get_close_matches`.  
Falls back to keyword containment if no strong match is found.

#### `fetch_questions(amount, category_id, difficulty, qtype)`
Fetches questions from the API based on user preferences.  
Handles API errors and returns an empty list if no questions are found.

#### `normalize_question(q)`
Decodes HTML entities in the question and answers.  
Shuffles answer options for fairness.

#### `prompt_int(msg, default, lo, hi)`
Prompts the user for an integer input within bounds, with a default value.

#### `prompt_choice(msg, choices, default)`
Prompts the user for a choice from a list, case-insensitive, with a default.

#### `run_quiz(questions)`
Runs the quiz loop:
- Displays each question and its options.
- Prompts for the user's answer.
- Checks correctness and updates score.
- Shows feedback and final summary.

#### `main()`
Main entry point:
- Prompts user for topic, number of questions, difficulty, and type.
- Fetches categories and matches topic.
- Fetches questions (with fallbacks if needed).
- Normalizes and shuffles questions.
- Runs the quiz.

### Error Handling

- If the API is unreachable or returns no questions, falls back to a small offline question set.

### Entry Point

- The script runs `main()` if executed directly.
- Handles `KeyboardInterrupt` (Ctrl+C) gracefully.

## Example Session

```
====== Any-Topic Quiz (Open Trivia DB) ======

Enter a topic (e.g., 'history', 'science', 'sports', or leave blank for random): science
How many questions? (1–50) [10]:
Difficulty? ['any', 'easy', 'medium', 'hard'] [any]:
Type? ['any', 'multiple', 'boolean'] [any]:
🔎 Matched topic to category: Science & Nature (id 17)

Q1 (Science & Nature - Medium):
What is the chemical symbol for Gold?
  1. Au
  2. Ag
  3. Fe
  4. Pb
Your answer (enter option number): 1
✅ Correct!

...

🏁 Quiz Finished!
Your Score: 8/10
👏 Great job! Keep it up.
```

## License

MIT License
