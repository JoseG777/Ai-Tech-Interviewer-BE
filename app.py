from flask import Flask, request, jsonify
from flask_cors import CORS
from database.models import User, UserHistory
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
# Function Imports
from APIs.getLeetCode import getLeetCodeInfo
from APIs.generateProblems import generate_problem
from APIs.evaluateResponse import evaluate_response

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


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
    # print(f"Recieved data: {data}")
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

    # print(f"Updating user: {uid}, {leetcode_username}, {coding_level}, {goal}, {upcoming_interview}, {overall_ratio}, {easy_ratio}, {medium_ratio}, {hard_ratio}")

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

    if problem and response and uid:
        evaluation = evaluate_response(problem, response)
        UserHistory.update_history(uid, problem, response, evaluation)
        return jsonify({"evaluation": evaluation})

    return jsonify({"evaluation": "error"})


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
