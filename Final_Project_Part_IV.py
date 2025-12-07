# clipboard_quiz.py
"""
Study Companion - Clipboard Quiz Generator (Part IV)

This module takes a short passage of text and turns it into a mini study aid.
When you run it, you can choose:

  1) Demo mode (a built-in sample passage), or
  2) Your own text (from the clipboard if available, or typed/pasted in)

For the chosen passage, the program:

  - Cleans and splits the text into sentences
  - Picks a few key sentences to use as "summary bullet points"
  - Builds cloze (fill-in-the-blank) questions by hiding important words
  - Builds simple True/False questions that are all true statements
  - Lets the user take the quiz in the terminal and get feedback
  - Saves the summary and all questions/answers to quiz_summary.txt

This is a small, text-based prototype of a quiz helper that could later
be connected to a GUI in the Study Companion app.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import re
import textwrap

# Try to import pyperclip for clipboard access (optional)
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


# ---------- Data model ----------

@dataclass
class QuizQuestion:
    prompt: str   # question text shown to the user
    answer: str   # correct answer ("guanxi", "True", etc.)
    qtype: str    # "cloze" or "tf"


# ---------- Text utilities ----------

def clean_text(text: str) -> str:
    """Basic cleanup: collapse multiple spaces and newlines."""
    return " ".join(text.split())


def split_sentences(text: str) -> List[str]:
    """
    Very simple sentence splitter based on ., !, ?.
    This does not handle every edge case, but it is enough here.
    """
    text = clean_text(text)
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def pick_keywords(sentence: str, max_keywords: int = 3) -> List[str]:
    """
    Pick some candidate keywords from a sentence:
    - words that are not very short
    - not in a small list of common stopwords

    This is a heuristic and just meant to find "important looking" words.
    """
    stopwords = {
        "the", "and", "or", "but", "a", "an", "to", "of", "in", "on", "for",
        "with", "by", "is", "are", "was", "were", "this", "that", "it",
        "as", "at", "from", "be", "can", "will", "not", "have", "has",
    }
    words = re.findall(r"[A-Za-z][A-Za-z\-']*", sentence)
    candidates = [
        w for w in words
        if len(w) >= 4 and w.lower() not in stopwords
    ]
    # Choose up to max_keywords, preferring longer words
    candidates = sorted(set(candidates), key=lambda w: -len(w))
    return candidates[:max_keywords]


# ---------- Summary + question generation ----------

def generate_summary_and_questions(
    text: str,
    n_bullets: int = 3,
    n_cloze: int = 3,
    n_tf: int = 2,
) -> Tuple[List[str], List[QuizQuestion]]:
    """
    Given a text passage, produce:
      - a short list of summary bullet sentences
      - a list of QuizQuestion objects (cloze + True/False)

    Notes:
    - Cloze questions are built by hiding one keyword with "____".
    - True/False questions are all true statements based on the passage.
    """

    sentences = split_sentences(text)
    if not sentences:
        return [], []

    # Score each sentence based on position and number of keywords.
    scored = []
    for idx, sent in enumerate(sentences):
        keywords = pick_keywords(sent)
        score = len(keywords) + max(0, 5 - idx)  # favor earlier sentences
        scored.append((score, sent, keywords))

    scored.sort(reverse=True, key=lambda t: t[0])

    # Take top sentences as summary bullets
    bullets = [s for _, s, _ in scored[:n_bullets]]

    questions: List[QuizQuestion] = []

    # --- Cloze questions (fill in the blank) ---
    cloze_sources = scored[:max(len(scored), n_cloze)]
    cloze_sentences_used = set()
    for _, sent, keywords in cloze_sources:
        if len([q for q in questions if q.qtype == "cloze"]) >= n_cloze:
            break
        if not keywords:
            continue
        target = keywords[0]
        pattern = re.compile(re.escape(target))
        cloze_sent = pattern.sub("____", sent, count=1)
        questions.append(QuizQuestion(
            prompt=f"Fill in the blank:\n{cloze_sent}",
            answer=target,
            qtype="cloze",
        ))
        cloze_sentences_used.add(sent)

    # --- T/F questions (true statements from the passage) ---
    tf_count = 0
    for _, sent, _ in scored:
        if tf_count >= n_tf:
            break
        # Prefer sentences not already used for cloze, but allow reuse if needed.
        if sent in cloze_sentences_used and len(sentences) > n_cloze:
            continue
        questions.append(QuizQuestion(
            prompt=f"True or False:\nAccording to the passage, {sent}",
            answer="True",
            qtype="tf",
        ))
        tf_count += 1

    return bullets, questions


# ---------- Quiz interaction ----------

def run_quiz(questions: List[QuizQuestion]) -> None:
    """
    Ask each question in the terminal, accept user input,
    and show whether the answer is correct.
    """
    if not questions:
        print("No questions were generated.")
        return

    print("\n=== Quiz Time ===")
    correct_count = 0

    for i, q in enumerate(questions, start=1):
        print(f"\nQuestion {i}:")
        print(textwrap.fill(q.prompt, width=80))

        if q.qtype == "cloze":
            user = input("Your answer: ").strip()
            if user.lower() == q.answer.lower():
                print("Correct.")
                correct_count += 1
            else:
                print(f"Incorrect. Correct answer: {q.answer}")

        elif q.qtype == "tf":
            user = input("Your answer (T/F): ").strip().lower()
            is_true = user in ("t", "true", "y", "yes")
            correct_is_true = (q.answer.lower() == "true")
            if is_true == correct_is_true:
                print("Correct.")
                correct_count += 1
            else:
                print(f"Incorrect. Correct answer: {q.answer}")

        else:
            print(f"(Unknown question type: {q.qtype})")

    print(f"\nYou answered {correct_count} out of {len(questions)} questions correctly.")


# ---------- Export ----------

def export_to_text(
    bullets: List[str],
    questions: List[QuizQuestion],
    filename: str = "quiz_summary.txt",
) -> None:
    """
    Save summary bullets and questions/answers to a text file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Summary Bullet Points:\n")
        for b in bullets:
            f.write(f" - {b}\n")

        f.write("\nQuestions:\n")
        for i, q in enumerate(questions, start=1):
            f.write(f"\nQ{i}: {q.prompt}\n")
            f.write(f"Answer: {q.answer}\n")

    print(f"\nSaved summary and questions to: {filename}")


# ---------- Input sources (demo vs user text) ----------

SAMPLE_TEXT = """
Guanxi is a Chinese term that refers to the network of relationships a person
builds and maintains over time. In many contexts, guanxi can help individuals
access resources, opportunities, or services more quickly. However, reliance
on guanxi can also create inequality, because people without strong
connections may be left out or receive lower-quality treatment.
"""


def get_text_demo() -> str:
    """Return the built-in sample text for demo mode."""
    print("\nUsing built-in demo passage about guanxi.")
    return SAMPLE_TEXT.strip()


def get_text_from_user() -> str:
    """
    Try to get text from the clipboard.
    If that fails, prompt the user to paste or type the text.
    """
    if HAS_PYPERCLIP:
        clip = pyperclip.paste().strip()
        if clip:
            print("\nUsing text from clipboard.")
            return clip

    print("\nNo clipboard text available (or pyperclip not installed).")
    print("Please paste or type the text you want to use, then press Enter.")
    print("You can enter multiple lines; finish with an empty line.\n")

    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    return "\n".join(lines)


# ---------- Main entry ----------

def main() -> None:
    print("Study Companion - Clipboard Quiz Generator")
    print("1) Demo mode (sample passage)")
    print("2) Use my own text (clipboard or paste)")
    choice = input("Choose 1 or 2 (default 1): ").strip()

    if choice == "2":
        raw_text = get_text_from_user()
    else:
        raw_text = get_text_demo()

    if not raw_text.strip():
        print("No text provided. Exiting.")
        return

    bullets, questions = generate_summary_and_questions(raw_text)
    print("\n=== Summary Bullet Points ===")
    for b in bullets:
        print(f" - {b}")

    run_quiz(questions)
    export_to_text(bullets, questions)


if __name__ == "__main__":
    main()
