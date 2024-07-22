import os
import re
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_API_KEY")


def evaluate_response(prompt, user_response):
    gpt_prompt = f"""
    Here is a coding problem and a user's response. Evaluate the response and provide feedback on a scale from 1-10, with 1 being "Needs a lot of work" to 10 being "Excellent". 

    Do not grade on function signature or class structure as those are given to the user. 

    Structure your feedback as follows:
    Evaluation: [Describe how they did overall]
    Feedback: [Provide detailed feedback on how they can improve]
    Final Grade: [Give a single number out of 10. JUST THE NUMBER AS A WHOLE NUMBER]

    Problem:
    {prompt}

    User's Response:
    {user_response}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": gpt_prompt}]
    )
    evaluation = response.choices[0].message["content"].strip()

    return evaluation

def parse_evaluation(response):
    evaluation_pattern = r"Evaluation:\s*(.*?)\s*Feedback:"
    feedback_pattern = r"Feedback:\s*(.*?)\s*Final Grade:"
    grade_pattern = r"Final Grade:\s*(\d+)"

    evaluation_match = re.search(evaluation_pattern, response, re.DOTALL)
    feedback_match = re.search(feedback_pattern, response, re.DOTALL)
    grade_match = re.search(grade_pattern, response)

    evaluation = evaluation_match.group(1).strip() if evaluation_match else ''
    feedback = feedback_match.group(1).strip() if feedback_match else ''
    final_grade = int(grade_match.group(1)) if grade_match else 0

    return evaluation, feedback, final_grade
# Example for proof of concept


p = f"""
    You are given a list of words. Your task is to find the top k most frequent words in the list. If two words have the same frequency, the word with the lower alphabetical order comes first.

Specifications:

- Input: A list of strings 'words' and an integer 'k'.
- Output: A list of strings representing the top k most frequent words sorted by frequency and then by alphabetical order.

Function Signature:

def top_k_frequent_words(words: list[str], k: int) -> list[str]

Examples:

Example 1:
Input: words = ["apple", "banana", "apple", "apple", "banana", "orange", "banana", "orange", "kiwi"], k = 2
Output: ["apple", "banana"]

Example 2:
Input: words = ["the", "daily", "daily", "coding", "coding", "coding", "problem", "daily"], k = 3
Output: ["daily", "coding", "the"]

Constraints:

1. The list 'words' will contain at least 1 word and at most 10^5 words.
2. The length of each word will be at most 100 characters.
3. The integer 'k' will be a positive integer and will always be less than or equal to the number of unique words in the list.

Note: Make sure your solution handles tie-breaker rules efficiently. Avoid brute force solutions as much as possible.

Function definition to start with:

def top_k_frequent_words(words: list[str], k: int) -> list[str]:
    # Your code here

Sample Usage:
 
 
print(top_k_frequent_words(["the", "daily", "daily", "coding", "coding", "coding", "problem", "daily"], 3))

"""

a = f"""
from collections import Counter
import heapq

def top_k_frequent_words(words: list[str], k: int) -> list[str]:
    # Step 1: Count the frequency of each word
    word_count = Counter(words)
    
    # Step 2: Use a heap to keep track of the top k frequent words
    # The heap will store tuples in the form (-frequency, word)
    # The negative frequency is used to create a max-heap based on frequency
    heap = []
    for word, freq in word_count.items():
        heapq.heappush(heap, (-freq, word))
    
    # Step 3: Extract the top k elements from the heap
    result = []
    for _ in range(k):
        result.append(heapq.heappop(heap)[1])
    
    return result

"""

# print(evaluate_response(p, a))

