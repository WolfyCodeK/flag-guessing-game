import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import csv
import pygame  # Import pygame for sound effects
import webbrowser  # Import webbrowser to open Wikipedia links
import time  # Import time to track elapsed time

class FlagGuessingGame:
    def __init__(self, master):
        self.bg_colour = "#222222"
        
        self.master = master
        self.master.title("Flag Guesser")
        self.master.geometry("525x525")
        self.master.configure(bg=self.bg_colour)  # Dark background color
        
        self.game_ended = False

        # Create a frame for the main game area
        self.game_frame = tk.Frame(master, bg=self.bg_colour, bd=10, relief=tk.FLAT)
        self.game_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.valid_answers_path = "csv/valid_answers.csv"
        self.flags = self.load_flags("flags", self.valid_answers_path)
        self.initial_flags = self.load_flags("flags", self.valid_answers_path)
        self.score = 0
        self.total_flags = len(self.flags)
        self.current_question = 0  # Initialize the current question counter

        # Initialize pygame mixer for sound effects
        pygame.mixer.init()
        
        # Load sound effects
        self.correct_sound = pygame.mixer.Sound("res/correct_answer.wav")
        self.wrong_sound = pygame.mixer.Sound("res/wrong_answer.wav")

        self.flag_label = tk.Label(self.game_frame, bg=self.bg_colour)
        self.flag_label.pack(pady=10)

        self.entry = tk.Entry(self.game_frame, font=("Arial", 14), justify='center', bg="#4A4A4A", fg="white", insertbackground='white')
        self.entry.pack(pady=10, padx=10, fill=tk.X)
        
        # Add key release event binding to check for valid answer
        self.entry.bind('<KeyRelease>', self.auto_submit_if_correct)

        self.submit_button = tk.Button(self.game_frame, text="Submit Guess", command=self.check_guess,
                                        font=("Arial", 12), bg="#6B8E23", fg="white", padx=10, pady=5)
        self.submit_button.pack(pady=10)

        self.score_label = tk.Label(self.game_frame, text=f"Score: {self.score}/{self.total_flags}",
                                     font=("Arial", 12), bg=self.bg_colour, fg="white")
        self.score_label.pack(pady=10)

        self.question_label = tk.Label(self.game_frame, text=f"Question: {self.current_question}/{self.total_flags}",
                                        font=("Arial", 12), bg=self.bg_colour, fg="white")
        self.question_label.pack(pady=10)

        # Timer label to display elapsed time
        self.timer_label = tk.Label(self.game_frame, text="Time: 0s", font=("Arial", 12), bg=self.bg_colour, fg="white")
        self.timer_label.pack(pady=10)

        self.start_time = time.time()  # Store the start time
        self.update_timer()  # Start updating the timer

        self.next_flag()
        
        self.entry.focus_set()

        # Bind the Enter key to the check_guess method
        self.entry.bind('<Return>', lambda event: self.check_guess())
        
        # Mute button
        self.is_muted = False  # Track mute state
        self.mute_button = tk.Button(self.game_frame, text="Mute", command=self.toggle_mute,
                                      font=("Arial", 10), bg="red", fg="white", padx=10, pady=5)
        self.mute_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)  # Place in the bottom right of the frame

    def update_timer(self):
        if not self.game_ended:
            elapsed_time = int(time.time() - self.start_time)  # Calculate elapsed time in seconds
            minutes, seconds = divmod(elapsed_time, 60)  # Convert seconds to minutes and seconds
            self.time_formatted = f"{minutes:02}:{seconds:02}"  # Format the time as MM:SS
            self.timer_label.config(text=f"Time Elapsed: {self.time_formatted}")  # Update the timer label
            
            self.master.after(1000, self.update_timer)  # Call this function again after 1 second

    def load_flags(self, folder, answers_file):
        flags = {}
        
        # Check if the valid_answers.csv file exists; if not, create it
        if not os.path.exists(answers_file):
            with open(answers_file, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)

        # Load valid answers from the CSV file
        with open(answers_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                flag_name = row[0].strip()  # Get the flag name
                valid_answers = [answer.strip() for answer in row[1:]] if len(row) > 1 else []
                # Remove duplicates by converting to a set and back to a list
                unique_answers = list(set(valid_answers))
                # Add the flag name itself as a valid answer
                flags[flag_name] = unique_answers  # Include the flag name

        # Load flags from the folder
        for filename in os.listdir(folder):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                flag_name = os.path.splitext(filename)[0]
                if flag_name not in flags:
                    flags[flag_name] = [flag_name]  # Initialize with the flag name if not found

        return flags

    def save_valid_answers(self):
        with open(self.valid_answers_path, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for flag_name, answers in self.initial_flags.items():
                writer.writerow([flag_name] + answers)

    def next_flag(self):
        if not self.flags:
            self.end_game()
            return

        self.flag_name, valid_answers = random.choice(list(self.flags.items()))
        self.show_flag_image(os.path.join("flags", f"{self.flag_name}.png"))

        # Update the question counter
        self.current_question += 1
        self.question_label.config(text=f"Question: {self.current_question}/{self.total_flags}")  # Update question label

        # Clear the text box for the next flag
        self.entry.delete(0, tk.END)

    def show_flag_image(self, flag_path):
        img = Image.open(flag_path)
        img = img.resize((300, 150))  # Resize for display
        self.flag_image = ImageTk.PhotoImage(img)
        self.flag_label.config(image=self.flag_image)
        self.flag_label.image = self.flag_image

    def check_guess(self):
        guess = self.entry.get().strip()  # Get user input
        valid_answers = self.flags[self.flag_name] + [self.flag_name]  # Get valid answers for the current flag

        # Check if the guess matches any valid answers in a case-insensitive manner
        if (guess.lower() in [answer.lower() for answer in valid_answers]) and guess != "":
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}/{self.total_flags}")
            if not self.is_muted:  # Check mute state
                self.correct_sound.play()  # Play correct answer sound
            self.next_flag()
        else:
            # Only show the register dialog if the user has written something
            if guess:
                self.show_register_dialog(guess)  # Show the register dialog
            else:
                self.wrong_message_box("Result", f"Wrong! The correct answer was: {self.flag_name}")
                if not self.is_muted:  # Check mute state
                    self.wrong_sound.play() 

    def auto_submit_if_correct(self, event):
        guess = self.entry.get().strip()
        valid_answers = self.flags[self.flag_name] + [self.flag_name]

        if guess.lower() in [answer.lower() for answer in valid_answers]:
            self.submit_button.invoke()

    def open_wikipedia_link(self, event):
        webbrowser.open(self.wiki_link)  # Open the Wikipedia link in the browser
        
    def on_link_hover(self, event):
        # Change link color to red when hovered
        event.widget.config(fg="white")

    def on_link_leave(self, event):
        # Change link color back to blue when not hovered
        event.widget.config(fg="blue")

    def wrong_message_box(self, title, message):
        self.msg_box = tk.Toplevel(self.master)
        self.msg_box.title(title)
        self.msg_box.configure(bg=self.bg_colour)

        # Set the size of the message box
        self.msg_box.geometry("300x200")

        # Center the message box relative to the main window
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 150
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 50
        self.msg_box.geometry(f"+{x}+{y}")

        msg_label = tk.Label(self.msg_box, text=message, bg=self.bg_colour, fg="white", font=("Arial", 12), wraplength=250)
        msg_label.pack(pady=20)

        ok_button = tk.Button(self.msg_box, text="OK", command=self.next_and_destroy_msg,
                              font=("Arial", 10), bg="#6B8E23", fg="white")
        ok_button.pack(pady=5)
        
        # Create a label for the Wikipedia link (styled like a hyperlink)
        self.link_label = tk.Label(self.msg_box, text="Learn more on Wikipedia", font=("Arial", 12), fg="blue", bg=self.bg_colour, cursor="hand2")
        self.link_label.pack(pady=10)

        # Bind the link to the Wikipedia URL
        self.link_label.bind("<Button-1>", lambda event: self.open_wikipedia_link(event))

        # Bind hover events to change color when hovering over the link
        self.link_label.bind("<Enter>", self.on_link_hover)
        self.link_label.bind("<Leave>", self.on_link_leave)
        
        # Generate Wikipedia link for the current flag
        self.wiki_link = f"https://en.wikipedia.org/wiki/{self.flag_name.replace(' ', '_')}"
        self.link_label.config(text=f"Learn more on Wikipedia", fg="blue", cursor="hand2")

        self.msg_box.transient(self.master)  # Keep it on top of the main window
        self.msg_box.grab_set()  # Block interaction with the main window
        self.msg_box.focus_force()  # Force focus to this message box

        # Bind Enter key to dismiss the message box
        self.msg_box.bind('<Return>', lambda event: self.next_and_destroy_msg())
        self.msg_box.protocol("WM_DELETE_WINDOW", self.next_and_destroy_msg)  # Allow window close via the window manager
        
    def game_finished_message_box(self, title, message):
        self.msg_box = tk.Toplevel(self.master)
        self.msg_box.title(title)
        self.msg_box.configure(bg=self.bg_colour)

        # Set the size of the message box
        self.msg_box.geometry("300x150")

        # Center the message box relative to the main window
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 150
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 50
        self.msg_box.geometry(f"+{x}+{y}")

        msg_label = tk.Label(self.msg_box, text=message, bg=self.bg_colour, fg="white", font=("Arial", 12), wraplength=250)
        msg_label.pack(pady=20)

        ok_button = tk.Button(self.msg_box, text="OK", command=self.master.destroy,
                              font=("Arial", 10), bg="#6B8E23", fg="white")
        ok_button.pack(pady=5)

        self.msg_box.transient(self.master)  # Keep it on top of the main window
        self.msg_box.grab_set()  # Block interaction with the main window
        self.msg_box.focus_force()  # Force focus to this message box

        # Bind Enter key to dismiss the message box
        self.msg_box.bind('<Return>', lambda event: self.master.destroy())
        self.msg_box.protocol("WM_DELETE_WINDOW", self.master.destroy)  # Allow window close via the window manager

    def show_register_dialog(self, guess):
        # Create a top-level window for the registration dialog
        self.register_dialog = tk.Toplevel(self.master)
        self.register_dialog.title("Register Alternative Answer")
        self.register_dialog.configure(bg=self.bg_colour)

        # Set the size of the dialog
        self.register_dialog.geometry("300x175")

        # Center the dialog relative to the main window
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 150
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 75
        self.register_dialog.geometry(f"+{x}+{y}")

        msg_label = tk.Label(self.register_dialog, 
                             text=f"Would you like to register '{guess}' for {self.flag_name} as an alternative answer for this flag?", 
                             bg=self.bg_colour, 
                             fg="white", 
                             font=("Arial", 12), 
                             wraplength=250)
        msg_label.pack(pady=20)

        yes_button = tk.Button(self.register_dialog, 
                               text="Yes", 
                               command=lambda: self.register_answer(guess),
                               font=("Arial", 10), 
                               bg="#6B8E23", 
                               fg="white")
        yes_button.pack(side=tk.LEFT, padx=20, pady=10)

        no_button = tk.Button(self.register_dialog, 
                              text="No", 
                              command=self.stop_register,
                              font=("Arial", 10), 
                              bg="#6B8E23", 
                              fg="white")
        no_button.pack(side=tk.RIGHT, padx=20, pady=10)

        self.register_dialog.transient(self.master)  # Keep it on top of the main window
        self.register_dialog.grab_set()  # Block interaction with the main window
        self.register_dialog.focus_force()  # Force focus to this dialog
        
        # Bind Enter key to dismiss the message box
        self.register_dialog.bind('<Return>', lambda event: self.stop_register())
        self.register_dialog.protocol("WM_DELETE_WINDOW", self.stop_register)  # Allow window close via the window manager
        
    def next_and_destroy_msg(self):
        self.msg_box.destroy()
        
        self.entry.delete(0, tk.END)  # Clear entry field
        del self.flags[self.flag_name]  # Remove the flag from the game
        
        self.next_flag() 

    def stop_register(self):
        self.register_dialog.destroy()
        self.wrong_message_box("Result", f"Wrong! The correct answer was: {self.flag_name}")
        self.wrong_sound.play()

    def register_answer(self, guess):
        self.register_alternative(guess)  # Register the alternative answer
        self.correct_sound.play()  # Play correct answer sound
        self.register_dialog.destroy()
        self.wrong_message_box("Answer Registered", "A new answer has been registered! You receive 1 point.")
        self.score += 1  # Increment score for registering an answer
        self.score_label.config(text=f"Score: {self.score}/{self.total_flags}")  # Update score display

    def register_alternative(self, guess):
        if self.flag_name in self.initial_flags:
            self.initial_flags[self.flag_name].append(guess)  # Add to the existing answers
        else:
            self.initial_flags[self.flag_name] = [guess]  # Create a new entry

        # Save the updated valid answers to the CSV file
        self.save_valid_answers()

    def end_game(self):
        self.game_finished_message_box("Game Over", f"Your final score is: {self.score}/{self.total_flags}\n\nTime player for: {self.time_formatted}")
        self.game_ended = True

    def toggle_mute(self):
        self.is_muted = not self.is_muted  # Toggle mute state
        # Update the button text based on mute state
        if self.is_muted:
            self.mute_button.config(text="Unmute")
        else:
            self.mute_button.config(text="Mute")

# Create the main application window
root = tk.Tk()
game = FlagGuessingGame(root)
root.mainloop()
