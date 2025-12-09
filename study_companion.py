# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:16:26 2025

@author: hp
"""



from Final_Project_Part_I import run_interactive_scenario
from Final_Project_Part_II import run_interactive
from Final_Project_Part_III import run_analytics_dashboard, load_sessions, generate_demo_sessions
from Final_Project_Part_IV import main as quiz_main
from study_pet import run_pet_dashboard
import os

def main_menu():
    while True:
        print("\n🐱📚 Welcome to Study Companion 📚🐱")
        print("1) Plan my study schedule (calendar-aware)")
        print("2) Run a Pomodoro timer")
        print("3) View productivity analytics")
        print("4) Generate a quiz from clipboard")
        print("5) Visit my virtual study pet")
        print("6) Quit")

        choice = input("Choose an option (1–6): ").strip()

        if choice == "1":
            run_interactive_scenario()
        elif choice == "2":
            run_interactive()
        elif choice == "3":
            if os.path.exists("sessions.csv"):
                sessions = load_sessions()
                run_analytics_dashboard(sessions, mode_label="REAL DATA")
            else:
                demo = generate_demo_sessions()
                run_analytics_dashboard(demo, mode_label="DEMO DATA")
        elif choice == "4":
            quiz_main()
        elif choice == "5":
            run_pet_dashboard()
        elif choice == "6":
            print("Goodbye! 🎓")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
