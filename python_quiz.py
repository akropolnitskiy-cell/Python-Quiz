import html
import json
import os
import random
from pathlib import Path

import requests

API_URL = "https://opentdb.com/api.php"
API_PARAMS = {
    "amount": 10,
    "category": 18,
    "difficulty": "easy",
    "type": "multiple",
}
SCORE_FILE = Path(__file__).with_name("score.json")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


response = requests.get(API_URL, params=API_PARAMS, timeout=10)
response.raise_for_status()
data = response.json()

if data.get("response_code") != 0 or not data.get("results"):
    print("The quiz could not get any questions. Please try again later.")
    raise SystemExit

with SCORE_FILE.open("r", encoding="utf-8") as file:
    score_data = json.load(file)

best_score = score_data.get("best_score", 0)
score = 0

clear_screen()
print("=" * 42)
print("          COMPUTER KNOWLEDGE QUIZ")
print("=" * 42)
print("Welcome! Let's see how much you know about computers.")
print(f"There are {len(data['results'])} questions.")
print("Choose the number of the answer you think is correct.")
print("A wrong answer moves you to the next question.")
input("Press Enter when you are ready to start...")

for question in data["results"]:
    question_text = html.unescape(question["question"])
    correct_answer = html.unescape(question["correct_answer"])
    answers = [
        html.unescape(answer)
        for answer in question["incorrect_answers"]
    ]
    answers.append(correct_answer)
    random.shuffle(answers)

    while True:
        clear_screen()
        print(question_text)

        for number, answer in enumerate(answers, start=1):
            print(f"{number}. {answer}")

        user_answer = input(f"Your answer (1-{len(answers)}): ")

        if not user_answer.isdigit():
            print("Please enter a number.")
            input("Press Enter to try again...")
            continue

        answer_number = int(user_answer)
        if not 1 <= answer_number <= len(answers):
            print(f"Choose a number from 1 to {len(answers)}.")
            input("Press Enter to try again...")
            continue

        if answers[answer_number - 1] == correct_answer:
            print("Correct!")
            score += 1
        else:
            print(f"Not quite. The correct answer is: {correct_answer}")

        input("Press Enter for the next question...")
        break

clear_screen()
print(f"You got {score} out of {len(data['results'])} questions right.")

if score > best_score:
    score_data["best_score"] = score

    with SCORE_FILE.open("w", encoding="utf-8") as file:
        json.dump(score_data, file, indent=2)
        file.write("\n")

    print(f"New best score: {score}!")
else:
    print(f"Your best score is still {best_score}.")
