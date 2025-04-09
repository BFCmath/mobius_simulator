import tkinter as tk
from tkinter import messagebox, simpledialog, Entry, Button, Label
from PIL import Image, ImageTk, ImageDraw
import json
import os

class ObstacleCourse:
    def __init__(self, root):
        self.root = root
        self.root.title("Obstacle Course Round - Math Competition Practice")
        
        # Grid arrangement as per the rules
        self.grid_order = [
            [1, 2, 3, 4],
            [12, 13, 14, 5],
            [11, 16, 15, 6],
            [10, 9, 8, 7]
        ]
        
        # Create ID selection UI first
        self.setup_id_selection()
    
    def setup_id_selection(self):
        """Create UI for selecting the question set ID."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create frame for ID selection
        select_frame = tk.Frame(self.root)
        select_frame.pack(pady=20, padx=20)
        
        # Label
        label = Label(select_frame, text="Enter Question Set ID (e.g., 001):", font=("Arial", 12))
        label.grid(row=0, column=0, padx=5, pady=10)
        
        # Entry for ID input
        self.id_entry = Entry(select_frame, width=10, font=("Arial", 12))
        self.id_entry.grid(row=0, column=1, padx=5, pady=10)
        self.id_entry.insert(0, "001")  # Default value
        
        # Load button
        load_btn = Button(select_frame, text="Load Question Set", 
                         command=self.load_question_set, font=("Arial", 12))
        load_btn.grid(row=1, column=0, columnspan=2, pady=10)
    
    def load_question_set(self):
        """Load the question set with the specified ID."""
        question_id = self.id_entry.get().strip()
        
        # Validate ID format
        if not question_id.isdigit():
            messagebox.showerror("Invalid ID", "Please enter a valid numeric ID.")
            return
        
        # Define file paths with the ID
        questions_file = os.path.join("problems", f"questions_{question_id}.json")
        image_file = os.path.join("problems", f"image_{question_id}.png")
        
        # Check if files exist
        if not os.path.exists(questions_file):
            messagebox.showerror("Error", f"Questions file '{questions_file}' not found.")
            return
            
        if not os.path.exists(image_file):
            messagebox.showerror("Error", f"Image file '{image_file}' not found.")
            return
        
        # Load questions, answers, hints, obstacle answer, and final hint from JSON
        try:
            with open(questions_file, 'r') as f:
                data = json.load(f)
                questions_data = data['questions']
                self.obstacle_answer = data['obstacle_answer']
                self.final_hint = data['final_hint']
        except KeyError:
            messagebox.showerror("Error", "Invalid format in questions file.")
            return
        
        # Populate questions, answers, and hints from the loaded data
        self.questions = {}
        self.answers = {}
        self.hints = {}
        for q in questions_data:
            square = q['square']
            self.questions[square] = q['question']
            self.answers[square] = q['answer']
            if 'hint' in q:
                self.hints[square] = q['hint']
        
        # Ensure all 16 squares are present
        if set(self.questions.keys()) != set(range(1, 17)):
            messagebox.showerror("Error", "Questions file must contain exactly squares 1 to 16.")
            return
        
        # Save the image path for loading later
        self.image_file = image_file
        
        # Initialize the game after successful loading
        self.initialize_game()
    
    def initialize_game(self):
        """Initialize the game after loading questions and image."""
        # Game state
        self.revealed = [[False for _ in range(4)] for _ in range(4)]
        self.correct_answers = [[False for _ in range(4)] for _ in range(4)]  # Track correct vs incorrect
        self.current_team = 0  # 0 = Team 1, 1 = Team 2, 2 = Team 3, 3 = Team 4
        self.turns_taken = [0, 0, 0, 0]  # Turns per team
        self.scores = [0, 0, 0, 0]  # Scores per team
        self.team_colors = ["red", "blue", "green", "purple"]  # Colors for each team
        
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Load and split the image
        self.load_image()
        
        # Create GUI components
        self.create_grid()
        self.create_ui_elements()
    
    def load_image(self):
        """Load and split the hidden image into 16 parts."""
        try:
            img = Image.open(self.image_file)
            
            # Resize the image to a fixed size (400x400 pixels)
            img = img.resize((400, 400), Image.LANCZOS)
            
            width, height = img.size
            part_width = width // 4
            part_height = height // 4
            
            # Create a black image for incorrect answers
            black_img = Image.new('RGB', (part_width, part_height), color='black')
            self.black_tile = ImageTk.PhotoImage(black_img)
            
            self.image_parts = []
            for i in range(4):
                row = []
                for j in range(4):
                    left = j * part_width
                    top = i * part_height
                    right = left + part_width
                    bottom = top + part_height
                    part = img.crop((left, top, right, bottom))
                    row.append(ImageTk.PhotoImage(part))
                self.image_parts.append(row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.setup_id_selection()  # Return to ID selection
    
    def create_grid(self):
        """Create the 4x4 grid of buttons."""
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=10)
        
        self.buttons = [[None for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                num = self.grid_order[i][j]
                btn = tk.Button(self.grid_frame, text=str(num), width=10, height=5,
                                command=lambda x=i, y=j: self.square_clicked(x, y))
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[i][j] = btn
    
    def create_ui_elements(self):
        """Create additional UI elements."""
        # Team and turn info
        self.team_label = tk.Label(self.root, text="Team 1's Turn", 
                                  font=("Arial", 12), fg=self.team_colors[0])
        self.team_label.pack()
        
        # Score display frame
        score_frame = tk.Frame(self.root)
        score_frame.pack(pady=5)
        
        # Score labels for each team
        self.score_labels = []
        for i in range(4):
            label = tk.Label(score_frame, text=f"Team {i+1}: 0", 
                           font=("Arial", 12), fg=self.team_colors[i])
            label.grid(row=0, column=i, padx=10)
            self.score_labels.append(label)
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        # Guess Obstacle button
        self.guess_btn = tk.Button(button_frame, text="Guess Obstacle", command=self.guess_obstacle)
        self.guess_btn.grid(row=0, column=0, padx=10)
        
        # Change question set button
        change_btn = tk.Button(button_frame, text="Change Question Set", 
                              command=self.setup_id_selection)
        change_btn.grid(row=0, column=1, padx=10)
        
        # Create hint boxes frame
        hints_frame = tk.Frame(self.root)
        hints_frame.pack(pady=10)
        
        # Create labeled hint boxes for squares 13-16
        self.hint_entries = {}
        for i, square in enumerate([13, 14, 15, 16]):
            # Label for the hint
            label = tk.Label(hints_frame, text=f"Hint {square}:", font=("Arial", 10, "bold"))
            label.grid(row=0, column=i, padx=5, sticky="w")
            
            # Entry widget to display the hint
            entry = tk.Entry(hints_frame, width=20, state="readonly")
            entry.grid(row=1, column=i, padx=5, pady=2)
            self.hint_entries[square] = entry
    
    def square_clicked(self, i, j):
        """Handle a square being clicked."""
        if self.revealed[i][j] or self.turns_taken[self.current_team] >= 4:
            return  # Square already revealed or team out of turns
        
        num = self.grid_order[i][j]
        question = self.questions[num]
        correct_answer = self.answers[num]
        
        # Simulate thinking time (no timer implemented for simplicity)
        answer = simpledialog.askstring(f"Square {num}", question,
                                        parent=self.root)
        
        # Mark square as revealed regardless of answer correctness
        self.revealed[i][j] = True
        
        if answer and answer.lower() == correct_answer.lower():
            self.reveal_correct_square(i, j)
            points = 15 if num >= 13 else 10
            self.scores[self.current_team] += points
            self.update_score()
            if num in self.hints and num in [13, 14, 15, 16]:
                # Update the specific hint box
                entry = self.hint_entries[num]
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, self.hints[num])
                entry.config(state="readonly")
            messagebox.showinfo("Correct", f"Correct! You earned {points} points.")
        else:
            self.reveal_incorrect_square(i, j)
            messagebox.showinfo("Incorrect", "Incorrect answer. Square revealed as black.")
        
        self.next_turn()
    
    def reveal_correct_square(self, i, j):
        """Reveal the image part for a correctly answered square."""
        self.correct_answers[i][j] = True
        self.buttons[i][j].destroy()
        label = tk.Label(self.grid_frame, image=self.image_parts[i][j])
        label.grid(row=i, column=j, padx=2, pady=2)
        self.buttons[i][j] = label
    
    def reveal_incorrect_square(self, i, j):
        """Reveal a black square for an incorrectly answered square."""
        self.buttons[i][j].destroy()
        label = tk.Label(self.grid_frame, image=self.black_tile)
        label.grid(row=i, column=j, padx=2, pady=2)
        self.buttons[i][j] = label
    
    def display_hint(self, hint):
        """Display a hint when a square 13-16 is revealed."""
        # Extract the square number from the surrounding code
        for i in range(4):
            for j in range(4):
                if self.revealed[i][j] and self.correct_answers[i][j]:
                    square = self.grid_order[i][j]
                    if square in [13, 14, 15, 16] and square in self.hints:
                        # Enable the entry, set the hint, then make it readonly again
                        entry = self.hint_entries[square]
                        entry.config(state="normal")
                        entry.delete(0, tk.END)
                        entry.insert(0, self.hints[square])
                        entry.config(state="readonly")
    
    def guess_obstacle(self):
        """Allow the current team to guess the Obstacle."""
        if self.turns_taken[self.current_team] >= 4:
            messagebox.showinfo("No Turns", "Your team has no turns left.")
            return
        
        guess = simpledialog.askstring("Guess Obstacle", "What is the Obstacle?",
                                       parent=self.root)
        if guess and guess.lower() == self.obstacle_answer.lower():
            # Count only correctly revealed squares for points calculation
            revealed_correct_count = sum(sum(row) for row in self.correct_answers)
            points = max(10, 90 - (revealed_correct_count * 5))  # Minimum 10 points
            self.scores[self.current_team] += points
            self.update_score()
            messagebox.showinfo("Correct!", f"Correct! You earned {points} points.")
            self.root.quit()  # End game on correct guess
        else:
            messagebox.showinfo("Incorrect", "Incorrect guess.")
            self.next_turn()
    
    def next_turn(self):
        """Switch to the next team's turn."""
        self.turns_taken[self.current_team] += 1
        self.current_team = (self.current_team + 1) % 4  # Cycle through 4 teams
        self.team_label.config(text=f"Team {self.current_team + 1}'s Turn", 
                              fg=self.team_colors[self.current_team])
        
        # Check if game should end or trigger final hint
        if all(all(row) for row in self.revealed):
            self.final_guess()
        elif all(t >= 4 for t in self.turns_taken):
            messagebox.showinfo("Game Over", "All turns used. Game ends.")
            self.root.quit()
    
    def final_guess(self):
        """Provide final hint if all squares are revealed."""
        messagebox.showinfo("Final Hint", self.final_hint)
        guess = simpledialog.askstring("Final Guess", "What is the Obstacle?",
                                       parent=self.root)
        if guess and guess.lower() == self.obstacle_answer.lower():
            self.scores[self.current_team] += 5
            self.update_score()
            messagebox.showinfo("Correct!", "Correct! You earned 5 points.")
        else:
            messagebox.showinfo("Incorrect", "Incorrect guess.")
        self.root.quit()
    
    def update_score(self):
        """Update the score display."""
        for i, label in enumerate(self.score_labels):
            label.config(text=f"Team {i+1}: {self.scores[i]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ObstacleCourse(root)
    root.mainloop()