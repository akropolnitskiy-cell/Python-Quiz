import html
import json
import random
import tkinter as tk
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

BACKGROUND = "#101820"
PANEL = "#1B2733"
ACCENT = "#72E0B5"
TEXT = "#F2F5F7"
MUTED = "#AAB7C4"


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Computer Knowledge Quiz")
        # Keep enough room for long questions, answer buttons, feedback, and Next.
        self.root.geometry("720x660")
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND)

        self.questions = []
        self.question_index = 0
        self.score = 0
        self.answers = []
        self.correct_answer = ""
        self.answered = False

        self.panel = tk.Frame(root, bg=PANEL, padx=34, pady=30)
        self.panel.pack(fill="both", expand=True, padx=28, pady=28)
        self.show_welcome()

    def clear_panel(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

    def add_label(self, text, size, color=TEXT, bold=False, pady=8):
        label = tk.Label(
            self.panel,
            text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            fg=color,
            bg=PANEL,
            wraplength=540,
            justify="center",
        )
        label.pack(pady=pady)
        return label

    def make_button(self, text, command, primary=False):
        button = tk.Button(
            self.panel,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            fg=BACKGROUND if primary else TEXT,
            bg=ACCENT if primary else "#293846",
            activeforeground=BACKGROUND if primary else TEXT,
            activebackground=ACCENT if primary else "#3A4C5C",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=11,
        )
        button.pack(fill="x", pady=6)
        return button

    def show_welcome(self):
        self.clear_panel()
        self.add_label("COMPUTER KNOWLEDGE QUIZ", 21, ACCENT, bold=True, pady=10)
        self.add_label("Welcome!", 18, bold=True)
        self.add_label(
            "Answer 10 multiple-choice questions about computers. "
            "Choose an answer to see whether you were right, then continue.",
            11,
            MUTED,
        )
        self.add_label("Your best score is saved on this computer.", 10, MUTED)
        self.make_button("Start quiz", self.load_questions, primary=True)

    def load_questions(self):
        try:
            response = requests.get(API_URL, params=API_PARAMS, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("response_code") != 0 or not data.get("results"):
                raise ValueError("No questions are available right now.")
            self.questions = data["results"]
        except (requests.RequestException, ValueError) as error:
            self.clear_panel()
            self.add_label("Could not load the quiz", 18, bold=True)
            self.add_label(str(error), 11, MUTED)
            self.make_button("Try again", self.show_welcome, primary=True)
            return

        self.question_index = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        self.clear_panel()
        question = self.questions[self.question_index]
        self.correct_answer = html.unescape(question["correct_answer"])
        self.answers = [html.unescape(answer) for answer in question["incorrect_answers"]]
        self.answers.append(self.correct_answer)
        random.shuffle(self.answers)
        self.answered = False

        self.add_label(
            f"QUESTION {self.question_index + 1} OF {len(self.questions)}     SCORE {self.score}",
            10,
            ACCENT,
            bold=True,
        )
        self.add_label(html.unescape(question["question"]), 15, bold=True, pady=14)

        self.answer_buttons = []
        for answer in self.answers:
            button = self.make_button(answer, lambda choice=answer: self.check_answer(choice))
            self.answer_buttons.append(button)

        self.feedback = tk.Label(
            self.panel, text="", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=PANEL
        )
        self.feedback.pack(pady=8)
        self.next_button = self.make_button("Next question", self.next_question, primary=True)
        self.next_button.pack_forget()

    def check_answer(self, choice):
        if self.answered:
            return
        self.answered = True
        for button in self.answer_buttons:
            button.configure(state="disabled")

        if choice == self.correct_answer:
            self.score += 1
            self.feedback.configure(text="Correct!", fg=ACCENT)
        else:
            self.feedback.configure(
                text=f"Not quite. The correct answer is: {self.correct_answer}", fg="#FFB4A9"
            )
        self.next_button.pack(fill="x", pady=6)

    def next_question(self):
        self.question_index += 1
        if self.question_index < len(self.questions):
            self.show_question()
        else:
            self.show_results()

    def show_results(self):
        self.clear_panel()
        best_score = self.load_best_score()
        new_record = self.score > best_score
        if new_record:
            self.save_best_score(self.score)
            best_score = self.score

        self.add_label("QUIZ COMPLETE", 20, ACCENT, bold=True, pady=12)
        self.add_label(f"You got {self.score} out of {len(self.questions)} right.", 17, bold=True)
        self.add_label(f"Best score: {best_score}", 12, MUTED)
        if new_record:
            self.add_label("New personal best!", 12, ACCENT, bold=True)
        self.make_button("Play again", self.show_welcome, primary=True)
        self.make_button("Close", self.root.destroy)

    @staticmethod
    def load_best_score():
        try:
            with SCORE_FILE.open("r", encoding="utf-8") as file:
                return json.load(file).get("best_score", 0)
        except (OSError, json.JSONDecodeError):
            return 0

    @staticmethod
    def save_best_score(score):
        with SCORE_FILE.open("w", encoding="utf-8") as file:
            json.dump({"best_score": score}, file, indent=2)
            file.write("\n")


if __name__ == "__main__":
    window = tk.Tk()
    QuizApp(window)
    window.mainloop()
