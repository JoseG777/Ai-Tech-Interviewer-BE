import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_API_KEY")


def generate_problem(
    user_level_description,
    current_goal,
    easy_ratio,
    medium_ratio,
    hard_ratio,
    overall_ratio,
    language,
    upcoming_interview,
):
    interview_info = (
        f"This problem is tailored for an upcoming interview with {upcoming_interview}."
        if upcoming_interview != "N/A"
        else ""
    )

    gpt_prompt = f"""
        Generate a {language} coding problem tailored to a user's profile and skill level, following this structure:

        Problem Description: A detailed description of the problem.

        Example 1:
        Input: [input example]
        Output: [expected output]

        Example 2:
        Input: [input example]
        Output: [expected output]

        Constraints: List all constraints.

        Function Signature: Provide the function signature.

        User Profile:
        Level: {user_level_description}
        Goal: {current_goal}
        Easy LeetCode Success Rate: {easy_ratio * 100}%
        Medium LeetCode Success Rate: {medium_ratio * 100}%
        Hard LeetCode Success Rate: {hard_ratio * 100}%
        Overall LeetCode Success Rate: {overall_ratio * 100}%

        Ensure the problem fits their skill set. If specific data structures or custom objects are needed, provide necessary class definitions or additional code. Only include the specified structure; do not add any notes or markdown.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": gpt_prompt}]
    )
    recommendation = response.choices[0].message["content"].strip()

    return recommendation
