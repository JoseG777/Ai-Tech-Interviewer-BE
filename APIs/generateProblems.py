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
        f"Upcoming Interview: This problem should be tailored for an upcoming interview with {upcoming_interview}. PRIORITIZE THIS"
        if upcoming_interview != "N/A"
        else ""
    )
    
    easy_percentage = float(easy_ratio) * 100
    medium_percentage = float(medium_ratio) * 100
    hard_percentage = float(hard_ratio) * 100
    overall_percentage = float(overall_ratio) * 100

    gpt_prompt = f"""
    
        Generate a {language} coding problem tailored to a user's profile and skill level detailed below:
        
        Level: {user_level_description}
        Goal: {current_goal}
        Easy LeetCode Success Rate: {easy_percentage}%
        Medium LeetCode Success Rate: {medium_percentage}%
        Hard LeetCode Success Rate: {hard_percentage}%
        Overall LeetCode Success Rate: {overall_percentage}%
        {interview_info}

        Ensure the problem fits their skill set. If specific data structures or custom objects are needed, provide necessary class definitions or additional code. Only include the specified structure; do not add any notes or markdown. Output your response in the following this structure:

        Problem Description: A detailed description of the problem.

        Example 1:
        Input: [input example]
        Output: [expected output]

        Example 2:
        Input: [input example]
        Output: [expected output]

        Constraints: List all constraints.

        Function Signature: Provide the function signature. ONLY RETURN FUNCTION SIGNATURE. DO NOT RETURN ANYTHING FROM THIS POINT ON

    """

    response = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": gpt_prompt}]
    )
    recommendation = response.choices[0].message["content"].strip()

    return recommendation
