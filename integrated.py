from flask import Flask, request, redirect, url_for, render_template, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.utils import secure_filename
import pandas as pd
from random import shuffle
import secrets
import tempfile
import re
from flask import send_file

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

# Initialize mail
mail = Mail(app)

# Set the secret key for the session
app.secret_key = secrets.token_hex(16)  # Generates a secure 16-byte hex string

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mcq_database.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

s = URLSafeTimedSerializer('Thisisasecret!')

# Define your database models
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(10), nullable=False)
    alt_phone_number = db.Column(db.String(10))
    semester = db.Column(db.Integer, nullable=False)
    stream = db.Column(db.String(100), nullable=False)
    college_name = db.Column(db.String(100), nullable=False)
    placement_officer_name = db.Column(db.String(100))
    placement_officer_email = db.Column(db.String(100))
    placement_officer_phone = db.Column(db.String(10))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    # Fields to store test results
    test_score = db.Column(db.Integer, default=0)
    correct_responses = db.Column(db.Integer, default=0)
    incorrect_responses = db.Column(db.Integer, default=0)

# Define the Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    level = db.Column(db.Integer, nullable=False)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['pdfFile']
        if file:
            filename = secure_filename(file.filename)
            file.save(app.config['UPLOAD_FOLDER'] + filename)
            # Parse the uploaded file and save questions to the database
            parse_and_save_questions(app.config['UPLOAD_FOLDER'] + filename)

            email = request.form['email']
            token = s.dumps(email, salt='email-confirm')

            msg = Message('Test Link Email', sender='justfun1394@gmail.com', recipients=[email])

            link = url_for('test', token=token, _external=True)

            msg.body = ' Greeting form scifor Technologies Please attend the test from the given link. Your test link is {} /n/n Regards/n/n Scifor Technologies'.format(link)

            mail.send(msg)
            return redirect(url_for('admin_dashboard'))
    return render_template('upload.html')

# Function to parse and save questions from the uploaded file
def parse_and_save_questions(file_path):
    Question.query.delete()
    df = pd.read_csv(file_path, delimiter=',', header=0, encoding='latin1')
    for index, row in df.iterrows():
        question = Question(
            question_text=row['question_text'],
            option_a=row['option_a'],
            option_b=row['option_b'],
            option_c=row['option_c'],
            option_d=row['option_d'],
            correct_answer=row['correct_answer'],
            level=row['level']
        )
        db.session.add(question)
    db.session.commit()


@app.route('/admin_dashboard')
def admin_dashboard():
    # Logic to render admin dashboard
    return render_template('admin_dashboard.html')


@app.route('/export_results')
def export_results():
    candidates = Candidate.query.all()
    data = []

    for candidate in candidates:
        data.append({
            'Name': candidate.name,
            'Email': candidate.email,
            'Phone Number': candidate.phone_number,
            'Semester': candidate.semester,
            'Stream': candidate.stream,
            'College Name': candidate.college_name,
            'City': candidate.city,
            'State': candidate.state,
            'Test Score': candidate.test_score,
            'Correct Responses': candidate.correct_responses,
            'Incorrect Responses': candidate.incorrect_responses
        })

    df = pd.DataFrame(data)
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        excel_path = temp_file.name
        df.to_excel(excel_path, index=False)
    return send_file(excel_path, as_attachment=True)



@app.route('/test/<token>', methods=['GET', 'POST'])
def test(token):
    try:
        return render_template('candidate_form.html')
    
    except SignatureExpired:
        return '<h1>The Link is expired!</h1>'
    
@app.route('/submit', methods=['POST'])
def submit_candidate():
    # Process candidate form submission
    name = request.form['name']
    email = request.form['email']
    phone_number = request.form['phone_number']
    alt_phone_number = request.form.get('alt_phone_number', '')
    semester = request.form['semester']
    stream = request.form['stream']
    college_name = request.form['college_name']
    placement_officer_name = request.form.get('placement_officer_name', '')
    placement_officer_email = request.form.get('placement_officer_email', '')
    placement_officer_phone = request.form.get('placement_officer_phone', '')
    city = request.form['city']
    state = request.form['state']
    
    # Validate phone number format (10 digits)
    if not phone_number.isdigit() or len(phone_number) != 10:
        return "Invalid phone number. Please enter a 10-digit number."
    
    # Validate email format using regular expression
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email address. Please enter a valid email address."
    
    # Create a new candidate instance and add it to the database
    new_candidate = Candidate(
        name=name, email=email, phone_number=phone_number, 
        alt_phone_number=alt_phone_number, semester=semester, 
        stream=stream, college_name=college_name, 
        placement_officer_name=placement_officer_name, 
        placement_officer_email=placement_officer_email, 
        placement_officer_phone=placement_officer_phone, 
        city=city, state=state
    )
    db.session.add(new_candidate)
    db.session.commit()
    
    # Store the candidate ID in session
    session['candidate_id'] = new_candidate.id
    
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')



@app.route('/submit_mcq', methods=['POST'])
def submit_mcq():
    # Initialize the score and response counters
    score = 0
    correct_responses = 0
    incorrect_responses = 0
    
    # Retrieve candidate ID from the session
    candidate_id = session.get('candidate_id')
    if candidate_id is None:
        return "Invalid candidate ID."

    # Retrieve the candidate object from the database
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return "Candidate not found."

    # Iterate through each question and check the user's answer
    for question in Question.query.all():
        # Get the user's answer for the current question
        user_answer = request.form.get(f"question{question.id}")

        # Check if the user's answer is correct
        if user_answer == question.correct_answer:
            score += 1
            correct_responses += 1
        else:
            incorrect_responses += 1
    
    # Update the candidate's record with the new test results
    candidate.test_score = score
    candidate.correct_responses = correct_responses
    candidate.incorrect_responses = incorrect_responses
    
    # Commit the changes to the database
    db.session.commit()
    
    # Redirect to the results page with the score as a parameter
    return redirect(url_for('results', score=score))

@app.route('/mcq', methods=['GET', 'POST'])
def mcq():
    if request.method == 'POST':
        # Process MCQ form submission
        score = 0
        for question_id in request.form:
            question = Question.query.get(question_id)
            if question and request.form[question_id] == question.correct_answer:
                score += 1
        return redirect(url_for('results', score=score))

    # Fetch all questions from the database
    questions = Question.query.all()
    # Shuffle the questions to provide a different order each time
    shuffle(questions)
    return render_template('mcq.html', questions=questions)

@app.route('/results')
def results():
    # Handle displaying results
    # score = request.args.get('score', default=0, type=int)
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True, port=5052)
