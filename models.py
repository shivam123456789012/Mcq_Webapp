from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define the Candidate model
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