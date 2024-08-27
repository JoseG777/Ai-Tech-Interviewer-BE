sample_questions = {
    1: {"category": "Arrays", "difficulty": "Easy", "answer": "O(n)"},
    2: {"category": "Arrays", "difficulty": "Medium", "answer": "Use a hash set to track duplicates"},
    3: {"category": "Arrays", "difficulty": "Hard", "answer": "Use a min-heap of size k"},
    4: {"category": "HashMaps", "difficulty": "Easy", "answer": "Constant time lookups"},
    5: {"category": "HashMaps", "difficulty": "Medium", "answer": "Linked list chaining"},
    6: {"category": "HashMaps", "difficulty": "Hard", "answer": "Combine multiple hash functions and apply them sequentially"},
    7: {"category": "Linked Lists", "difficulty": "Easy", "answer": "Dynamic size"},
    8: {"category": "Linked Lists", "difficulty": "Medium", "answer": "Iteratively using two pointers"},
    9: {"category": "Linked Lists", "difficulty": "Hard", "answer": "Using two pointers moving at different speeds"},
    10: {"category": "Two Pointers", "difficulty": "Easy", "answer": "Improves time complexity by avoiding nested loops"},
    11: {"category": "Two Pointers", "difficulty": "Medium", "answer": "Merging two sorted arrays"},
    12: {"category": "Two Pointers", "difficulty": "Hard", "answer": "Sort the array and use two pointers, one at the start and one at the end"},
    13: {"category": "Stacks", "difficulty": "Easy", "answer": "Popping the top element"},
    14: {"category": "Stacks", "difficulty": "Medium", "answer": "Stack"},
    15: {"category": "Stacks", "difficulty": "Hard", "answer": "Using an auxiliary stack"},
    16: {"category": "Queues", "difficulty": "Easy", "answer": "Popping the front element"},
    17: {"category": "Queues", "difficulty": "Medium", "answer": "Priority Queue"},
    18: {"category": "Queues", "difficulty": "Hard", "answer": "By using one stack for enqueue operations and another for dequeue operations"},
    19: {"category": "Heaps", "difficulty": "Easy", "answer": "A binary tree where the root is the smallest element"},
    20: {"category": "Heaps", "difficulty": "Medium", "answer": "Finding the maximum element in a min-heap"},
    21: {"category": "Heaps", "difficulty": "Hard", "answer": "Use one min-heap and one max-heap"},
    22: {"category": "Trees", "difficulty": "Easy", "answer": "A tree where the left child is always smaller than the parent and the right child is always larger"},
    23: {"category": "Trees", "difficulty": "Medium", "answer": "O(log n)"},
    24: {"category": "Trees", "difficulty": "Hard", "answer": "Using AVL rotations"},
    25: {"category": "Graphs", "difficulty": "Easy", "answer": "A data structure that consists of vertices connected by edges"},
    26: {"category": "Graphs", "difficulty": "Medium", "answer": "Dijkstra's Algorithm"},
    27: {"category": "Graphs", "difficulty": "Hard", "answer": "Using Depth-First Search with a recursion stack"},
    28: {"category": "Dynamic Programming", "difficulty": "Easy", "answer": "A method for solving complex problems by breaking them down into simpler subproblems"},
    29: {"category": "Dynamic Programming", "difficulty": "Medium", "answer": "Knapsack problem"},
    30: {"category": "Dynamic Programming", "difficulty": "Hard", "answer": "Use dynamic programming with a memoization table"}
}

def evaluate_technical_exam(answers):
    difficulty_weights = {
        "Easy": 0.2,
        "Medium": 0.3,
        "Hard": 0.5
    }

    scores = {category: 0 for category in {q['category'] for q in sample_questions.values()}}

    for question_id, user_answer in answers.items():
        question_id = int(question_id)
        question = sample_questions.get(question_id)

        if question and user_answer == question['answer']:
            category = question['category']
            difficulty = question['difficulty']
            scores[category] += difficulty_weights[difficulty] * 100

    skill_levels = {"Beginner": [], "Intermediate": [], "Advanced": []}
    for category, score in scores.items():
        if score < 40:
            skill_levels["Beginner"].append(category)
        elif score < 80:
            skill_levels["Intermediate"].append(category)
        else:
            skill_levels["Advanced"].append(category)

    return skill_levels

