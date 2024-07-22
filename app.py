import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from database.models import User, UserHistory
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
# Function Imports
import openai

# Function Imports 
from APIs.getLeetCode import getLeetCodeInfo
from APIs.generateProblems import generate_problem
from APIs.evaluateResponse import evaluate_response, parse_evaluation

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

openai.api_key = os.getenv("OPEN_AI_API_KEY")

def send_email(to_email, subject, body):
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return "Email sent successfully"
    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"


@app.route("/api/message", methods=["GET"])
def get_message():
    return jsonify({"message": "Hello from Flask!"})

def get_ai_response(prompt, problem):
    system_prompt = (
        f"""
        You are an interview assistant. You are presenting a coding problem to the user and helping them through the problem. 
        
        You must not give away the solution directly. If the user asks for hints, provide only subtle hints that guide them in the right direction. Only give hints if the user provides context about their current progress or what they have tried so far. Also, don't answer more than what is needed. If a user asks something that can be answered in a yes or no response, return just yes or no
        
        Make your answers short and concise. No more than 2 sentences
        
        Here is the problem: \n\n"
        {problem}\n\n"
        User: {prompt}\n\n"
        Remember, do not give the solution directly.
        """
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"].strip()

@app.route("/api/createUser", methods=["POST"])
def create_user():
    data = request.get_json()
    uid = data["uid"]
    email = data["email"]
    leetcode_username = None
    user_level_description = "N/A"


    User.add_user(uid, email, leetcode_username, user_level_description)


    #Sends welcome email
    try:
        send_email(
            to_email=email,
            subject="Welcome to Interviewer AI!",
            body="Thank you for signing up. We're excited to apart of your technical interviewing journy!"
        )
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


    return jsonify({"message": "User created successfully"}), 201

@app.route("/api/newUser", methods=["POST"])
def new_user():
    data = request.get_json()
    uid = data["uid"]
    leetcode_username = data["leetcode_username"]
    coding_level = data["coding_level"]
    goal = data["goal"]
    upcoming_interview = data["upcoming_interview"]

    overall_ratio, easy_ratio, medium_ratio, hard_ratio = None, None, None, None

    if leetcode_username != "N/A":
        overall_ratio, easy_ratio, medium_ratio, hard_ratio = getLeetCodeInfo(
            leetcode_username
        )

    User.update_user(
        uid,
        leetcode_username,
        coding_level,
        goal,
        upcoming_interview,
        overall_ratio,
        easy_ratio,
        medium_ratio,
        hard_ratio,
    )

    return jsonify({"message": "New user info received"}), 201

@app.route("/api/generateProblem", methods=["POST"])
def generate_problem_endpoint():
    data = request.get_json()
    uid = data["uid"]
    language = data["language"]

    user = User.get_user_id(uid)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_level_description = user[3]
    easy_ratio = user[4]
    medium_ratio = user[5]
    hard_ratio = user[6]
    overall_ratio = user[7]

    problem = generate_problem(
        user_level_description,
        easy_ratio,
        medium_ratio,
        hard_ratio,
        overall_ratio,
        language,
    )
    return jsonify({"problem": problem})

@app.route("/api/evaluateResponse", methods=["POST"])
def evaluate_response_endpoint():
    data = request.get_json()
    problem = data["problem"]
    response = data["userResponse"]
    uid = data["uid"]
    
    # print(problem, response, "\n\n\n", uid)

    if problem and response and uid:
        # print("\n\n\n\n\n\n\nREACHED\n\n\n\n\n\n\n")
        evaluation = evaluate_response(problem, response)
        evaluation2, feedback, final_grade = parse_evaluation(evaluation)
        # print(problem, response, uid, evaluation2, feedback, final_grade)
        UserHistory.update_history(uid, problem, response, evaluation2, feedback, int(final_grade))
        return jsonify({"evaluation": evaluation})

    return jsonify({"evaluation": "error"})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    problem = data.get('problem')
    ai_response = get_ai_response(user_message, problem)
    return jsonify({"ai_response": ai_response})


@app.route("/api/sendEmail", methods=["POST"])
def send_email_endpoint():
    data = request.get_json()
    to_email = data["to_email"]
    subject = data["subject"]
    body = data["body"]
    result = send_email(to_email, subject, body)
    return jsonify({"message": result})

if __name__ == "__main__":
    from database.initialization import initialize_database

    initialize_database()
    app.run(debug=True, port=5000)
