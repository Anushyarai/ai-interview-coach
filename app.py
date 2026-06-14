from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import PyPDF2
import os

from skills import skills_list
from question_generator import generate_questions
from answer_evaluator import evaluate_answer
from adaptive_questions import get_adaptive_question
from resume_analyzer import analyze_resume
from role_detector import detect_role
from topic_detector import detect_weak_topics

app = Flask(__name__)

# DATABASE CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview.db'
app.config['SECRET_KEY'] = 'secretkey'

# INITIALIZE DATABASE + BCRYPT
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# USER TABLE
class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


# INTERVIEW RESULT TABLE
class InterviewResult(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    question = db.Column(
        db.String(500)
    )

    answer = db.Column(
        db.Text
    )

    score = db.Column(
        db.Integer
    )

    performance = db.Column(
        db.String(100)
    )
    interview_id = db.Column(
    db.Integer
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )


# HOME PAGE
@app.route('/')
def home():

    return render_template('index.html')


# SIGNUP PAGE
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # HASH PASSWORD
        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

        # CREATE USER
        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        # SAVE USER
        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('signup.html')


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # FIND USER
        user = User.query.filter_by(
            email=email
        ).first()

        # CHECK PASSWORD
        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            # SAVE SESSION
            session['user_id'] = user.id
            session['user_name'] = user.name

            # RESET INTERVIEW SESSION

            session.pop('next_question', None)

            session.pop('question_count', None)

            session.pop('weak_topics', None)

            session.pop('asked_questions', None)

            return redirect('/dashboard')

        else:

            return "<h1>Invalid Email or Password</h1>"

    return render_template('login.html')


# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# DASHBOARD PAGE
@app.route('/dashboard')
def dashboard():

    # CHECK LOGIN
    if 'user_id' not in session:

        return redirect('/login')

    # GET USER RESULTS
    results = InterviewResult.query.filter_by(
        user_id=session['user_id']
    ).all()

    unique_interviews = set()

    for result in results:

        unique_interviews.add(
            result.interview_id
        )

    total_interviews = len(unique_interviews)

# GROUP SCORES BY INTERVIEW

    interview_scores = {}

    for result in results:

        interview_id = result.interview_id

        if interview_id not in interview_scores:

            interview_scores[interview_id] = []

        interview_scores[interview_id].append(
            result.score
        )

    # CALCULATE INTERVIEW AVERAGES

    all_interview_averages = []

    for scores in interview_scores.values():

        avg = sum(scores) / len(scores)

        all_interview_averages.append(avg)

    # FINAL DASHBOARD AVERAGE

# FINAL DASHBOARD AVERAGE

    if len(all_interview_averages) > 0:

        average_score = round(

            sum(all_interview_averages)
            / len(all_interview_averages),

            2
        )

    else:

        average_score = 0

    # BEST PERFORMANCE
    if total_interviews == 0:

        best_performance = "--"

    else:

        best_performance = results[0].performance

        for result in results:

            if result.performance == "Excellent":

                best_performance = "Excellent"
                break

            elif result.performance == "Average":

                best_performance = "Average"


    # AI INSIGHTS

    if total_interviews == 0:

        ai_insight = (
            "No interview data available yet. "
            "Start an interview to receive AI insights."
        )

    elif average_score >= 7:

        ai_insight = (
            "Strong interview performance detected. "
            "You demonstrate good technical understanding."
        )

    elif average_score >= 4:

        ai_insight = (
            "Average performance detected. "
            "Focus more on detailed technical explanations."
        )

    else:

        ai_insight = (
            "Interview performance needs improvement. "
            "Practice core technical concepts regularly."
        )
    return render_template(
        'dashboard.html',
        name=session['user_name'],
        total_interviews=total_interviews,
        average_score=average_score,
        best_performance=best_performance,
        ai_insight=ai_insight
    )



# RESUME UPLOAD PAGE

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    # CHECK LOGIN
    if 'user_id' not in session:

        return redirect('/login')

    if request.method == 'POST':

        extracted_text = ""

        file = request.files['resume']

        if file:

            # CREATE UPLOAD FOLDER
            upload_folder = os.path.join(

                app.root_path,

                'static',

                'uploads'
            )

            os.makedirs(

                upload_folder,

                exist_ok=True
            )

            # FILE PATH
            filepath = os.path.join(

                upload_folder,

                file.filename
            )

            # SAVE FILE
            file.save(filepath)

            # READ PDF
            with open(filepath, 'rb') as pdf_file:

                reader = PyPDF2.PdfReader(pdf_file)

                for page in reader.pages:

                    extracted_text += page.extract_text()

            # SKILL EXTRACTION
            found_skills = []

            for skill in skills_list:

                if skill.lower() in extracted_text.lower():

                    found_skills.append(skill)

            # DETECT ROLE
            role = detect_role(
                extracted_text
            )

            # GENERATE QUESTIONS
            questions = generate_questions(

                role,

                found_skills,

                extracted_text
            )

            # CREATE INTERVIEW SESSION ID
            if 'interview_id' not in session:

                session['interview_id'] = 1

            else:

                session['interview_id'] += 1

            # SAVE SESSION DATA
            session['questions'] = questions

            session['role'] = role

            session['question_count'] = 0

            session['next_question'] = None

            session['asked_questions'] = []

            session['weak_topics'] = []

            # REDIRECT TO INTERVIEW
            return redirect('/interview')

    return render_template('upload.html')






# INTERVIEW PAGE
@app.route('/interview')
def interview():

    # CHECK LOGIN
    if 'user_id' not in session:

        return redirect('/login')

    # CHECK QUESTIONS EXIST
    if 'questions' not in session:

        return redirect('/upload')

    # QUESTION COUNT
    if 'question_count' not in session:

        session['question_count'] = 0

    # INTERVIEW COMPLETE
    if session['question_count'] >= 5:

        return redirect('/final_report')

    # NEXT QUESTION
    question = session.get('next_question')

    # FIRST QUESTION
    if not question:

        questions = session.get('questions')

        if questions and len(questions) > 0:

            question = questions[0]

        else:

            question = "Tell me about yourself."

    return render_template(

        'interview.html',

        question=question
    )




# ANSWER EVALUATION
@app.route('/evaluate', methods=['POST'])
def evaluate():

    # CHECK LOGIN
    if 'user_id' not in session:

        return redirect('/login')

    question = request.form['question']

    answer = request.form['answer']

    # EVALUATE ANSWER
    score, feedback, performance = evaluate_answer(
        answer
    )
    weak_topics = detect_weak_topics(
        question,
        score
    )

    # SAVE RESULT
    result = InterviewResult(
        question=question,
        answer=answer,
        score=score,
        performance=performance,
        user_id=session['user_id'],
        interview_id=session['interview_id']
    )

    db.session.add(result)
    db.session.commit()

    # TRACK QUESTION COUNT

    if 'question_count' not in session:

        session['question_count'] = 1

    else:

        session['question_count'] += 1

    # GET NEXT ADAPTIVE QUESTION
    next_question = get_adaptive_question(

        performance,

        question,

        answer,

        session.get('role')
    )
    # STORE ASKED QUESTIONS

    if 'asked_questions' not in session:

        session['asked_questions'] = []

    session['asked_questions'].append(
        question
    )

    # SAVE NEXT QUESTION
    session['next_question'] = next_question

    # STORE WEAK TOPICS

    if 'weak_topics' not in session:

        session['weak_topics'] = []

    session['weak_topics'].extend(
        weak_topics
    )

    # INTERVIEW COMPLETE



    return render_template(
        'feedback.html',
        question=question,
        answer=answer,
        score=score,
        feedback=feedback,
        performance=performance,
        next_question=next_question
    )


# FINAL REPORT
@app.route('/final_report')
def final_report():

    # CHECK LOGIN
    if 'user_id' not in session:

        return redirect('/login')

    # GET CURRENT INTERVIEW RESULTS
    results = InterviewResult.query.filter_by(

        user_id=session['user_id'],

        interview_id=session.get('interview_id')
    ).all()

    # TOTAL SCORE
    total_score = 0

    for result in results:

        total_score += result.score

    # AVERAGE SCORE
    if len(results) > 0:

        average_score = round(

            total_score / len(results),

            2
        )

    else:

        average_score = 0

    # OVERALL PERFORMANCE
    if average_score >= 7:

        overall = "Excellent"

        strengths = [

            "Strong technical understanding",

            "Good answer structuring",

            "Confident interview performance"
        ]

        weaknesses = [

            "Can improve advanced concepts"
        ]

    elif average_score >= 4:

        overall = "Average"

        strengths = [

            "Basic technical knowledge present",

            "Decent communication"
        ]

        weaknesses = [

            "Need more detailed explanations",

            "Improve technical depth"
        ]

    else:

        overall = "Needs Improvement"

        strengths = [

            "Attempted all questions"
        ]

        weaknesses = [

            "Answers lacked technical depth",

            "Need better conceptual clarity"
        ]

    # GET UNIQUE WEAK TOPICS
    weak_topics = list(

        set(

            session.get(
                'weak_topics',
                []
            )
        )
    )

    # RESET INTERVIEW SESSION
    session.pop('next_question', None)

    session.pop('question_count', None)

    session.pop('asked_questions', None)

    session.pop('weak_topics', None)

    return render_template(

        'final_report.html',

        average_score=average_score,

        overall=overall,

        strengths=strengths,

        weaknesses=weaknesses,

        weak_topics=weak_topics
    )




# MAIN DRIVER
if __name__ == '__main__':

    # CREATE DATABASE TABLES
    with app.app_context():

        db.create_all()

    app.run(debug=True)