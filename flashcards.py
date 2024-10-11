import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import csv

class FlagGuessingGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Flag Guessing Game")
        self.master.geometry("500x500")
        self.master.configure(bg="#2E2E2E")  # Dark background color

        # Create a frame for the main game area
        self.game_frame = tk.Frame(master, bg="#3A3A3A", bd=10, relief=tk.FLAT)
        self.game_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.flags = self.load_flags("flags", "valid_answers.csv")
        self.save_valid_answers()
        self.score = 0
        self.total_flags = len(self.flags)
        self.current_question = 0  # Initialize the current question counter

        self.flag_label = tk.Label(self.game_frame, bg="#3A3A3A")
        self.flag_label.pack(pady=20)

        self.entry = tk.Entry(self.game_frame, font=("Arial", 14), justify='center', bg="#4A4A4A", fg="white", insertbackground='white')
        self.entry.pack(pady=10, padx=10, fill=tk.X)

        self.submit_button = tk.Button(self.game_frame, text="Submit Guess", command=self.check_guess,
                                        font=("Arial", 12), bg="#6B8E23", fg="white", padx=10, pady=5)
        self.submit_button.pack(pady=10)

        self.score_label = tk.Label(self.game_frame, text=f"Score: {self.score}/{self.total_flags}",
                                     font=("Arial", 12), bg="#3A3A3A", fg="white")
        self.score_label.pack(pady=20)

        self.question_label = tk.Label(self.game_frame, text=f"Question: {self.current_question}/{self.total_flags}",
                                        font=("Arial", 12), bg="#3A3A3A", fg="white")
        self.question_label.pack(pady=10)

        self.next_flag()
        
        self.entry.focus_set()

        # Bind the Enter key to the check_guess method
        self.entry.bind('<Return>', lambda event: self.check_guess())

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
        with open("valid_answers.csv", mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for flag_name, answers in self.flags.items():
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
        if guess.lower() in [answer.lower() for answer in valid_answers]:
            self.score += 1
            result_message = "Correct!"
            self.score_label.config(text=f"Score: {self.score}/{self.total_flags}")
            messagebox.showinfo("Result", result_message)  # Show result message
        else:
            result_message = f"Wrong! The correct answer was: {self.flag_name}"
            messagebox.showinfo("Result", result_message)  # Show result message
            # Ask user if they want to register an alternative answer if they entered something
            if guess:  # Only ask if the guess is not empty
                self.ask_register_alternative(guess)

        self.entry.delete(0, tk.END)  # Clear entry field
        del self.flags[self.flag_name]  # Remove the flag from the game
        self.next_flag()  # Load next flag

    def ask_register_alternative(self, guess):
        # Prompt for registering alternative answer
        answer = messagebox.askyesno("Register Alternative Answer", 
            "Would you like to register your answer as an alternative answer for this flag?")
        
        if answer:
            self.register_alternative(guess)

    def register_alternative(self, alt_answer):
        if alt_answer:
            if alt_answer not in self.flags[self.flag_name]:
                self.flags[self.flag_name].append(alt_answer)
                self.score += 1  # Increment score for registering an alternative answer
                messagebox.showinfo("Success", f"'{alt_answer}' has been registered as an alternative answer. You earned a point!")
                self.score_label.config(text=f"Score: {self.score}/{self.total_flags}")  # Update score label
                self.save_valid_answers()  # Save updated answers
            else:
                messagebox.showinfo("Info", f"'{alt_answer}' is already a valid answer.")
        else:
            messagebox.showwarning("Warning", "Please enter an alternative answer.")

    def end_game(self):
        messagebox.showinfo("Game Over", f"Your final score: {self.score}/{self.total_flags}")
        self.save_valid_answers()  # Save any remaining answers
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game = FlagGuessingGame(root)
    root.mainloop()
