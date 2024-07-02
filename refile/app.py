from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from pyresparser import ResumeParser
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumes.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(100))

db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'doc', 'docx']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Parse the resume
        data = ResumeParser(os.path.join(app.config['UPLOAD_FOLDER'], filename)).get_extracted_data()
        # Save the resume data to the database
        user = User(name=data.get('name'), email=data.get('email'))
        db.session.add(user)
        db.session.commit()
        resume = Resume(user_id=user.id, filename=filename)
        db.session.add(resume)
        db.session.commit()
        # Recommend jobs
        recommended_jobs = recommend_jobs(data)
        return render_template('result.html', jobs=recommended_jobs)
    return redirect(request.url)

def recommend_jobs(data):
    # Mock job recommendations based on extracted skills
    jobs = [
        {"title": "Software Engineer", "skills": ["Python", "Flask", "SQL"]},
        {"title": "Data Scientist", "skills": ["Python", "Machine Learning", "Data Analysis"]},
    ]
    user_skills = set(data.get('skills', []))
    recommended_jobs = []
    for job in jobs:
        job_skills = set(job['skills'])
        if user_skills & job_skills:
            recommended_jobs.append(job)
    return recommended_jobs

if __name__ == '__main__':
    app.run(debug=True)
