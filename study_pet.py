# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:18:31 2025

@author: hp
"""


import os
from Final_Project_Part_III import load_sessions, calculate_study_streak

def run_pet_dashboard():
    print("\n🐾 Your Virtual Study Pet 🐾")

    if not os.path.exists("sessions.csv"):
        print("No session data found. Do some studying first!")
        return

    sessions = load_sessions()
    total_minutes = sum(s["work_minutes"] for s in sessions)
    streak = calculate_study_streak(sessions)

    level = 1 + total_minutes // 120  # +1 level every 2 hours
    mood = "😴" if total_minutes < 30 else "😊" if streak < 3 else "😺"

    print(f"\nYour pet's current level: {level}")
    print(f"Mood: {mood}")
    print("Keep studying to make them happy!")

    # print ASCII pet
    print("\n     /\\_/\\ ")
    print("    ( o.o )")
    print("     > ^ <")

