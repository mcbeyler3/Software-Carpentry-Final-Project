import tkinter as tk
from tkinter import messagebox, scrolledtext
from dataclasses import dataclass
from typing import List, Tuple
import re
import pyperclip

# ---------- Data model ----------

@dataclass
class QuizQuestion:
    prompt: str
    answer: str


# ---------- Utilities ----------

def clean_text(text: str) -> str:
    return " ".join(text.split())

def split_sentences(text: str) -> List[str]:
    text = clean_text(text)
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def pick_keywords(sentence: str, max_keywords: int = 3) -> List[str]:
    stopwords = {
        "the", "and", "or", "but", "a", "an", "to", "of", "in", "on", "for",
        "with", "by", "is", "are", "was", "were", "this", "that", "it",
        "as", "at", "from", "be", "can", "will", "not", "have", "has",
    }
    words = re.findall(r"[A-Za-z][A-Za-z\-']*", sentence)
    candidates = [w for w in words if len(w) >= 4 and w.lower() not in stopwords]
    candidates = sorted(set(candidates), key=lambda w: -len(w))
    return candidates[:max_keywords]

def generate_summary_and_questions(text: str, n_bullets=3, n_cloze=3) -> Tuple[List[str], List[QuizQuestion]]:
    sentences = split_sentences(text)
    if not sentences:
        return [], []

    scored = []
    for idx, sent in enumerate(sentences):
        keywords = pick_keywords(sent)
        score = len(keywords) + max(0, 5 - idx)
        scored.append((score, sent, keywords))
    scored.sort(reverse=True, key=lambda t: t[0])

    bullets = [s for _, s, _ in scored[:n_bullets]]

    questions: List[QuizQuestion] = []
    cloze_sources = scored[:n_cloze * 2]
    for _, sent, keywords in cloze_sources:
        if len(questions) >= n_cloze:
            break
        if not keywords:
            continue
        target = keywords[0]
        cloze_sent = re.compile(re.escape(target)).sub("____", sent, count=1)
        questions.append(QuizQuestion(prompt=f"Fill in the blank:\n{cloze_sent}", answer=target))

    return bullets, questions

def export_to_text(bullets: List[str], questions: List[QuizQuestion], filename="quiz_summary.txt") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Summary Bullet Points:\n")
        for b in bullets:
            f.write(f" - {b}\n")
        f.write("\nQuestions:\n")
        for i, q in enumerate(questions, start=1):
            f.write(f"\nQ{i}: {q.prompt}\n")
            f.write(f"Answer: {q.answer}\n")


# ---------- GUI Quiz Generator ----------

def run_interactive(show_main_menu=None):
    def generate_quiz():
        raw_text = input_box.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Input Required", "Please enter or paste some text.")
            return

        bullets, questions = generate_summary_and_questions(raw_text)

        if not bullets and not questions:
            messagebox.showerror("Error", "Could not generate questions from text.")
            return

        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)

        output_box.insert(tk.END, "Summary:\n")
        for b in bullets:
            output_box.insert(tk.END, f" - {b}\n")

        output_box.insert(tk.END, "\nQuestions:\n")
        for i, q in enumerate(questions, 1):
            output_box.insert(tk.END, f"\nQ{i}: {q.prompt}\n")
            output_box.insert(tk.END, f"Answer: {q.answer}\n")

        output_box.config(state="disabled")
        export_to_text(bullets, questions)

    def paste_clipboard():
        try:
            text = pyperclip.paste()
            input_box.delete("1.0", tk.END)
            input_box.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("Clipboard Error", str(e))

    def return_to_main():
        win.destroy()
        if show_main_menu:
            show_main_menu()

    win = tk.Tk()
    win.title("🧠 Clipboard Quiz Generator")
    win.geometry("700x600")

    tk.Label(win, text="📋 Paste or write a passage below:").pack(pady=5)

    input_box = scrolledtext.ScrolledText(win, height=10, width=85)
    input_box.pack(pady=5)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="📋 Paste from Clipboard", command=paste_clipboard).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🧠 Generate Quiz", command=generate_quiz).pack(side="left", padx=5)
    tk.Button(btn_frame, text="⬅ Return to Main Menu", command=return_to_main).pack(side="left", padx=5)

    tk.Label(win, text="📝 Output:").pack(pady=5)

    output_box = scrolledtext.ScrolledText(win, height=15, width=85, state="disabled")
    output_box.pack(pady=5)

    win.mainloop()
