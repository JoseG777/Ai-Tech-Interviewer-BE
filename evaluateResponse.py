import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPEN_AI_API_KEY')


def evaluate_response(prompt, user_response):
    gpt_prompt = f"""
    Here is a coding problem and a user's response. Evaluate the response and provide feedback on a scale from 1-5, with 1 being "Needs a lot of work" to 5 being "Excellent"

    Problem:
    {prompt}

    User's Response:
    {user_response}

    Provide detailed feedback on the correctness and quality of the user's response.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": gpt_prompt}]
    )
    evaluation = response.choices[0].message["content"].strip()

    return evaluation

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