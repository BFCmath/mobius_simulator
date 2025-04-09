import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import json
import os

class ObstacleCourseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Obstacle Course Round")
        
        # Load configuration
        self.load_config()
        self.load_image_parts()
        
        # Game state
        self.answered_squares = []
        self.score = 0
        self.hints = []
        
        # GUI setup
        self.create_widgets()
        self.setup_grids()
        
    def load_config(self):
        """Load questions and configuration from JSON file"""
        try:
            with open('config.json') as f:
                self.config = json.load(f)
            
            self.correct_obstacle = self.config['metadata']['obstacle_term']
            self.image_path = self.config['metadata']['image_path']
            
            # Validate questions
            self.questions = {}
            for square in self.config['questions']:
                self.questions[int(square)] = self.config['questions'][square]
            
            # Load hints
            self.hint_data = self.config['hints']
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
            self.root.destroy()
    
    def load_image_parts(self):
        """Load and split the obstacle image into parts"""
        try:
            if not os.path.exists(self.image_path):
                raise FileNotFoundError(f"Image file {self.image_path} not found")
            
            original_image = Image.open(self.image_path)
            width, height = original_image.size
            self.part_width = width // 4
            self.part_height = height // 4
            
            self.image_parts = {}
            for i in range(4):
                for j in range(4):
                    part_number = i * 4 + j + 1
                    left = j * self.part_width
                    upper = i * self.part_height
                    right = left + self.part_width
                    lower = upper + self.part_height
                    part = original_image.crop((left, upper, right, lower))
                    photo = ImageTk.PhotoImage(part)
                    self.image_parts[part_number] = photo
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.root.destroy()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Score display
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}")
        self.score_label.pack()
        
        # Hints display
        self.hints_label = tk.Label(self.root, text="Hints will appear here.")
        self.hints_label.pack()
        
        # Guess Obstacle button
        self.guess_btn = tk.Button(self.root, text="Guess Obstacle", 
                                 command=self.guess_obstacle)
        self.guess_btn.pack()
        
        # Grid frames
        self.button_grid_frame = tk.Frame(self.root)
        self.button_grid_frame.pack(side=tk.LEFT)
        
        self.image_grid_frame = tk.Frame(self.root)
        self.image_grid_frame.pack(side=tk.RIGHT)
    
    def setup_grids(self):
        """Initialize button and image grids"""
        grid_numbers = [
            [1, 2, 3, 4],
            [12, 13, 14, 5],
            [11, 16, 15, 6],
            [10, 9, 8, 7]
        ]
        
        # Create buttons
        self.buttons = []
        for i in range(4):
            row_buttons = []
            for j in range(4):
                number = grid_numbers[i][j]
                btn = tk.Button(self.button_grid_frame, text=str(number),
                              command=lambda num=number: self.on_square_click(num))
                btn.grid(row=i, column=j, padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        # Create image labels
        self.image_labels = []
        for i in range(4):
            row_labels = []
            for j in range(4):
                label = tk.Label(self.image_grid_frame, bg='black', 
                               width=self.part_width//10, height=self.part_height//10)
                label.grid(row=i, column=j, padx=2, pady=2)
                row_labels.append(label)
            self.image_labels.append(row_labels)
    
    def on_square_click(self, number):
        if number in self.answered_squares:
            return
        self.open_question_window(number)
    
    def open_question_window(self, square_number):
        window = tk.Toplevel(self.root)
        window.title(f"Question for Square {square_number}")
        
        # Get question from config
        question_data = self.questions.get(square_number)
        if not question_data:
            messagebox.showerror("Error", "Question not found!", parent=window)
            window.destroy()
            return
            
        question = question_data['question']
        correct_answer = question_data['answer']
        
        tk.Label(window, text=question).pack(padx=20, pady=10)
        answer_entry = tk.Entry(window)
        answer_entry.pack(padx=20, pady=5)
        
        def submit():
            user_answer = answer_entry.get()
            if user_answer.strip().lower() == correct_answer.lower():
                self.handle_correct_answer(square_number)
                window.destroy()
            else:
                messagebox.showerror("Incorrect", "Try again!", parent=window)
        
        tk.Button(window, text="Submit", command=submit).pack(pady=5)
    
    def handle_correct_answer(self, square_number):
        self.answered_squares.append(square_number)
        
        # Update score
        if 1 <= square_number <= 12:
            self.score += 10
        else:
            self.score += 15
        self.score_label.config(text=f"Score: {self.score}")
        
        # Reveal image part
        self.reveal_image_part(square_number)
        
        # Add hint if applicable
        if 13 <= square_number <= 16:
            self.add_hint(square_number)
        
        # Disable button
        for i in range(4):
            for j in range(4):
                if grid_numbers[i][j] == square_number:
                    self.buttons[i][j].config(state=tk.DISABLED)
                    break
        
        if len(self.answered_squares) == 16:
            self.handle_all_answered()
    
    def reveal_image_part(self, square_number):
        row = (square_number - 1) // 4
        col = (square_number - 1) % 4
        self.image_labels[row][col].config(image=self.image_parts[square_number])
        self.image_labels[row][col].image = self.image_parts[square_number]
    
    def add_hint(self, square_number):
        hint_index = square_number - 13
        if 0 <= hint_index < len(self.hint_data):
            self.hints.append(self.hint_data[hint_index])
            self.hints_label.config(text="\n".join(self.hints))
    
    def guess_obstacle(self):
        answered_count = len(self.answered_squares)
        if answered_count == 0:
            messagebox.showinfo("Info", "Answer at least one square to guess.")
            return
        # Calculate points
        points = 90 - 5 * (answered_count - 1)
        if points < 10:
            points = 10
        guess = simpledialog.askstring("Guess Obstacle", "Enter the Obstacle term:")
        if guess and guess.lower() == self.correct_obstacle.lower():
            self.score += points
            self.score_label.config(text=f"Score: {self.score}")
            messagebox.showinfo("Correct", f"Correct! You earned {points} points.")
        elif guess:
            messagebox.showerror("Incorrect", "Wrong guess. Try again.")
    
    def handle_all_answered(self):
        # Add final hint
        self.hints.append("Final hint: Related to mathematics and informatics.")
        self.hints_label.config(text="\n".join(self.hints))
        # Prompt for final guess
        guess = simpledialog.askstring("Final Guess", "Enter your guess (5 points):")
        if guess and guess.lower() == self.correct_obstacle.lower():
            self.score += 5
            self.score_label.config(text=f"Score: {self.score}")
            messagebox.showinfo("Correct", "Correct! +5 points.")
        elif guess:
            messagebox.showerror("Incorrect", "Wrong answer.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ObstacleCourseApp(root)
    root.mainloop()