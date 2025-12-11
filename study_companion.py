# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import messagebox


from Final_Project_Part_I import run_interactive_scenario
from Final_Project_Part_II import  launch_pomodoro_session, PomodoroConfig
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

def main(): # Displays the main menu GUI with buttons to navigate to different tools
    def show_main_menu():
        root = tk.Tk()
        root.title("🐱 Study Companion")
        root.geometry("500x500")
        root.config(bg="#f5f5f5") # background

        ascii_label = tk.Label(root, text=ASCII_ART, font=("Courier", 12), bg="#f5f5f5", justify="left")
        ascii_label.pack(pady=10)

        button_frame = tk.Frame(root, bg="#f5f5f5")
        button_frame.pack(pady=10) # Container for all buttons
# Opens the Study Planner (Part I)
        def run_planner():
            root.withdraw()
            run_interactive_scenario(root_window=root, show_main_menu=show_main_menu)
# Opens a form to configure and start a Pomodoro session
        def run_pomodoro():
            root.withdraw() # hide main window
            config_win = tk.Toplevel()
            config_win.title("Pomodoro Setup")
            config_win.geometry("350x300")
            # Form fields for user input
            tk.Label(config_win, text="Task Name:").pack()
            task_entry = tk.Entry(config_win)
            task_entry.insert(0, "Focus Session")
            task_entry.pack()
 
            tk.Label(config_win, text="Work Minutes:").pack()
            work_entry = tk.Entry(config_win)
            work_entry.insert(0, "25")
            work_entry.pack()

            tk.Label(config_win, text="Break Minutes:").pack()
            break_entry = tk.Entry(config_win)
            break_entry.insert(0, "5")
            break_entry.pack()

            tk.Label(config_win, text="Number of Cycles:").pack()
            cycles_entry = tk.Entry(config_win)
            cycles_entry.insert(0, "4")
            cycles_entry.pack()

            demo_var = tk.BooleanVar()
            tk.Checkbutton(config_win, text="Demo Mode (fast)", variable=demo_var).pack(pady=5)
# Launch Pomodoro after validating input
            def start():
                try:
                    config = PomodoroConfig(
                        task_name=task_entry.get(),
                        work_minutes=int(work_entry.get()),
                        break_minutes=int(break_entry.get()),
                        cycles=int(cycles_entry.get()),
                        demo_mode=demo_var.get()
                        )
                except ValueError:
                        messagebox.showerror("Error", "Please enter valid numbers.")
                        return

                config_win.destroy()
                launch_pomodoro_session(config, show_main_menu)
 # Buttons to start or cancel
            tk.Button(config_win, text="Start Pomodoro", command=start).pack(pady=10)
            tk.Button(config_win, text="Cancel", command=config_win.destroy).pack()

# Opens the analytics dashboard (Part III)

        def run_analytics():
            root.withdraw()  # hide main menu window
            try:
                run_analytics_gui(show_main_menu=show_main_menu)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                root.deiconify()
                
                
 # Opens the quiz generator using clipboard text (Part IV)
        def run_quiz():
            root.withdraw()  
            run_quiz_gui(show_main_menu=show_main_menu)
# Opens the virtual pet dashboard
        def run_pet():
            root.withdraw()  
            run_pet_dashboard_gui(root_window=root, show_main_menu=show_main_menu)

        # main menu buttons
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


