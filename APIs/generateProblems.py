import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_API_KEY")


def generate_problem(
    user_level_description, easy_ratio, medium_ratio, hard_ratio, overall_ratio
):
    gpt_prompt = f"""
    Generate a coding problem for a user based on the following profile and skill level. The problem should be tailored to match the user's expertise and challenge them appropriately. Ensure the problem is clear, concise, and structured as follows:

    Problem Description:
    - A detailed description of the problem the user needs to solve.

    Examples:
    - Provide at two examples with input and output.

    Constraints:
    - List all constraints that the user needs to consider.

    Function Signature:
    - Provide the function signature at the end.

    User Profile:
    - Level Description: {user_level_description}
    - Easy LeetCode Problem Success Ratio: {easy_ratio * 100}%
    - Medium LeetCode Problem Success Ratio: {medium_ratio * 100}%
    - Hard LeetCode Problem Success Ratio: {hard_ratio * 100}%
    - Overall LeetCode Problem Success Ratio: {overall_ratio * 100}%

    Based on the users level description and success ratios, create a problem that fits their skill set. If the problem involves specific data structures or custom objects (e.g., linked list nodes, tree nodes), provide the necessary class definitions or any additional code required to understand and solve the problem. Ensure the problem is similar to a standard LeetCode problem and is appropriately challenging for the user's level.

    Make sure the output follows this structure strictly, with NO MARKDOWN:

    Problem Description:
    - [Detailed problem description]

    Examples:
    - Example 1: 
    - Input: [input example]
    - Output: [expected output]
    - Example 2: 
    - Input: [input example]
    - Output: [expected output]

    Constraints:
    - [List of constraints]

    Function Signature:
    - [Function signature]
    """


    response = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": gpt_prompt}]
    )
    recommendation = response.choices[0].message["content"].strip()

    return recommendation
