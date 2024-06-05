from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
from werkzeug.utils import secure_filename
from models import db, Question, Candidate
import tempfile
import pandas as pd
import uuid
import secrets


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mcq_database.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Path where uploaded files will be stored

db.init_app(app)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['pdfFile']
        if file:
            filename = secure_filename(file.filename)
            file.save(app.config['UPLOAD_FOLDER'] + filename)
            # Parse the uploaded file and save questions to the database
            parse_and_save_questions(app.config['UPLOAD_FOLDER'] + filename)
            return redirect(url_for('admin_dashboard'))
    return render_template('upload.html')

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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)