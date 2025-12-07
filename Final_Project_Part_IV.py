# clipboard_quiz.py
"""
Study Companion - Clipboard Quiz Generator (Part IV)

This module turns a short passage into a simple self-quiz.

Features:
  - Demo mode with a built-in sample passage
  - Custom mode using clipboard text (if available) or pasted text
  - Produces a short bullet-point summary
  - Generates fill-in-the-blank (cloze) questions based on key words
  - Lets the user take the quiz in the terminal and get feedback
  - Saves summary and questions to quiz_summary.txt
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
    prompt: str   # what you show to the user
    answer: str   # correct answer (e.g., "guanxi")


# ---------- Text utilities ----------

def clean_text(text: str) -> str:
    """Basic cleanup: normalize whitespace."""
    return " ".join(text.split())


def split_sentences(text: str) -> List[str]:
    """
    Very simple sentence splitter based on ., !, ?.
    Good enough for short passages in this project.
    """
    text = clean_text(text)
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def pick_keywords(sentence: str, max_keywords: int = 3) -> List[str]:
    """
    Pick some candidate keywords from a sentence:
    - words that are not super short
    - skip a small set of common stopwords
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
    # Choose up to max_keywords, bias toward longer words
    candidates = sorted(set(candidates), key=lambda w: -len(w))
    return candidates[:max_keywords]


# ---------- Summary + question generation ----------

def generate_summary_and_questions(
    text: str,
    n_bullets: int = 3,
    n_cloze: int = 3,
) -> Tuple[List[str], List[QuizQuestion]]:
    """
    Given a text, produce:
      - a short bullet-point summary (list of sentences)
      - a list of QuizQuestion objects (fill-in-the-blank only)
    """
    sentences = split_sentences(text)
    if not sentences:
        return [], []

    # Simple "importance": earlier sentences are slightly more important,
    # plus we reward sentences that have more "keywords".
    scored = []
    for idx, sent in enumerate(sentences):
        keywords = pick_keywords(sent)
        score = len(keywords) + max(0, 5 - idx)  # favor early sentences
        scored.append((score, sent, keywords))

    scored.sort(reverse=True, key=lambda t: t[0])

    # Take top sentences as summary bullets
    bullets = [s for _, s, _ in scored[:n_bullets]]

    questions: List[QuizQuestion] = []

    # Cloze questions (fill in the blank)
    cloze_sources = scored[:n_cloze * 2]  # pick from top sentences
    for _, sent, keywords in cloze_sources:
        if len(questions) >= n_cloze:
            break
        if not keywords:
            continue
        target = keywords[0]
        # Replace first occurrence of the target with a blank
        pattern = re.compile(re.escape(target))
        cloze_sent = pattern.sub("____", sent, count=1)
        questions.append(QuizQuestion(
            prompt=f"Fill in the blank:\n{cloze_sent}",
            answer=target,
        ))

    return bullets, questions


# ---------- Quiz interaction ----------

def run_quiz(questions: List[QuizQuestion]) -> None:
    """
    Ask each question in the terminal, accept user input,
    and print whether it is correct.
    """
    if not questions:
        print("No questions were generated.")
        return

    print("\n=== Quiz Time ===")
    correct_count = 0

    for i, q in enumerate(questions, start=1):
        print(f"\nQuestion {i}:")
        print(textwrap.fill(q.prompt, width=80))
        user = input("Your answer: ").strip()

        if user.lower() == q.answer.lower():
            print("Correct.")
            correct_count += 1
        else:
            print(f"Incorrect. Correct answer: {q.answer}")

    print(f"\nYou answered {correct_count} out of {len(questions)} correctly.")


# ---------- Export ----------

def export_to_text(
    bullets: List[str],
    questions: List[QuizQuestion],
    filename: str = "quiz_summary.txt",
) -> None:
    """
    Save summary bullets and cloze questions/answers to a text file.
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
    Try to get text from clipboard using pyperclip.
    If that fails, prompt the user to paste text manually.
    """
    if HAS_PYPERCLIP:
        clip = pyperclip.paste().strip()
        if clip:
            print("\nUsing text from clipboard.")
            return clip

    print("\nNo clipboard text available (or pyperclip not installed).")
    print("Please paste or type the text you want to use, then press Enter.")
    print("(You can paste multiple lines; finish with an empty line.)\n")

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
