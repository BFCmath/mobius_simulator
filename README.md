# Mobius Simulator

## How to run the simulator

Put questions and images into [problems folder](problems/).

The format of the question file is:

```css
{
    "questions": [
        {"square": 1, "question": "What is 2 + 2?", "answer": "4"},
        {"square": 2, "question": "What is the capital of France?", "answer": "Paris"},
        {"square": 3, "question": "What is 3 squared?", "answer": "9"},
        {"square": 4, "question": "What is the largest planet?", "answer": "Jupiter"},
        {"square": 5, "question": "What is 10 - 6?", "answer": "4"},
        {"square": 6, "question": "What gas do plants need?", "answer": "Carbon dioxide"},
        {"square": 7, "question": "What is 5 x 3?", "answer": "15"},
        {"square": 8, "question": "What is H2O?", "answer": "Water"},
        {"square": 9, "question": "What is 12 / 3?", "answer": "4"},
        {"square": 10, "question": "What color is the sky?", "answer": "Blue"},
        {"square": 11, "question": "What is 7 + 8?", "answer": "15"},
        {"square": 12, "question": "What is the smallest prime?", "answer": "2"},
        {"square": 13, "question": "What is a binary search?", "answer": "A search algorithm", "hint": "Think about data structures."},
        {"square": 14, "question": "What is a loop?", "answer": "Repeated execution", "hint": "Related to algorithms."},
        {"square": 15, "question": "What is 2 to the power 3?", "answer": "8", "hint": "Involves numbers."},
        {"square": 16, "question": "What is recursion?", "answer": "A function calling itself", "hint": "Common in informatics."}
    ],
    "obstacle_answer": "Binary Search",
    "final_hint": "Final Hint: A method to find something efficiently."
}
```

Then run the simulator with:

```bash
python challenge.py
```
