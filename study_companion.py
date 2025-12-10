# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:16:26 2025

@author: hp
"""

import tkinter as tk
from tkinter import messagebox


from Final_Project_Part_I import run_interactive_scenario
from Final_Project_Part_II import run_interactive
from Final_Project_Part_III import run_analytics_gui, load_sessions, generate_demo_sessions
from Final_Project_Part_IV import  run_interactive  as run_quiz_gui
from study_pet import run_pet_dashboard_gui
import os


# ASCII art
ASCII_ART = r"""
     /\_/\  
    ( o.o )  Your Study Companion
     > ^ <   Let's be productive!
"""

def main():
    def show_main_menu():
        root = tk.Tk()
        root.title("🐱 Study Companion")
        root.geometry("500x500")
        root.config(bg="#f5f5f5")

        ascii_label = tk.Label(root, text=ASCII_ART, font=("Courier", 12), bg="#f5f5f5", justify="left")
        ascii_label.pack(pady=10)

        button_frame = tk.Frame(root, bg="#f5f5f5")
        button_frame.pack(pady=10)

        def run_planner():
            root.withdraw()
            run_interactive_scenario(root_window=root, show_main_menu=show_main_menu)

        def run_pomodoro():
            root.destroy()
            run_interactive(show_main_menu=show_main_menu)

        def run_analytics():
            root.withdraw()  # hide main menu window
            try:
                run_analytics_gui(show_main_menu=show_main_menu)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                root.deiconify()
                
                

        def run_quiz():
            root.withdraw()  # Hide the main menu window
            run_quiz_gui(show_main_menu=show_main_menu)

        def run_pet():
            root.withdraw()  # hide main window, don't destroy it
            run_pet_dashboard_gui(root_window=root, show_main_menu=show_main_menu)

        # Buttons
        tk.Button(button_frame, text="📆 Study Planner", command=run_planner, width=30).pack(pady=5)
        tk.Button(button_frame, text="⏱️ Pomodoro Timer", command=run_pomodoro, width=30).pack(pady=5)
        tk.Button(button_frame, text="📊 View Analytics", command=run_analytics, width=30).pack(pady=5)
        tk.Button(button_frame, text="🧠 Quiz from Clipboard", command=run_quiz, width=30).pack(pady=5)
        tk.Button(button_frame, text="🐱 Virtual Study Pet", command=run_pet, width=30).pack(pady=5)
        tk.Button(button_frame, text="❌ Exit", command=root.quit, width=30).pack(pady=20)

        root.mainloop()

    # Start the menu
    show_main_menu()


if __name__ == "__main__":
    main()

