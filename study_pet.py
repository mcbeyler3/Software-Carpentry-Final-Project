# -*- coding: utf-8 -*-


# study_pet.py

import os
from Final_Project_Part_III import load_sessions, calculate_study_streak
import tkinter as tk
from tkinter import messagebox

def run_pet_dashboard_gui(root_window=None, show_main_menu=None):
    if not os.path.exists("sessions.csv"):
        messagebox.showinfo("Virtual Pet", "No session data found.\nDo some studying first!")
        return

    sessions = load_sessions()
    total_minutes = sum(s["work_minutes"] for s in sessions)
    streak = calculate_study_streak(sessions)
    level = 1 + total_minutes // 120
    mood = "😴" if total_minutes < 30 else "😊" if streak < 3 else "😺"

    pet_ascii = r"""
     /\_/\
    ( o.o )
     > ^ <
    """

    message = f"""
Your pet's current level: {level}
Mood: {mood}
Study streak: {streak} day(s)
"""

    # Create a new popup window
    pet_window = tk.Toplevel(root_window)
    pet_window.title("🐱 Your Study Pet")
    pet_window.geometry("400x350")

    tk.Label(pet_window, text=pet_ascii, font=("Courier", 12)).pack(pady=5)
    tk.Label(pet_window, text=message.strip(), justify="left").pack(pady=10)

    # Add button to return to main menu
    def return_to_main():
        pet_window.destroy()
        if show_main_menu:
            show_main_menu()

    tk.Button(pet_window, text="Return to Main Menu", command=return_to_main).pack(pady=10)
