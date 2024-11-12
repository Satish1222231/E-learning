from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)

class Assignments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    questions = db.Column(db.String(100), nullable=False)

class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)

@app.route('/populate_database')
def populate_database():
    with app.app_context():
        # Drop all existing tables (optional, for a fresh start)
        db.drop_all()
        db.create_all()

        # Populate Users
        users = [
            User(name='Alice', password='alice_password'),
            User(name='Bob', password='bob_password'),
            User(name='Charlie', password='charlie_password'),
            User(name='Diana', password='diana_password')
        ]
        db.session.bulk_save_objects(users)
        courses = [
            Courses(name='Python Programming', description='Learn the basics of Python.'),
            Courses(name='Web Development', description='Build websites with HTML, CSS, and JavaScript.'),
            Courses(name='Data Science', description='Introduction to data analysis and visualization.'),
            Courses(name='Machine Learning', description='Fundamentals of machine learning algorithms.')
        ]
        db.session.bulk_save_objects(courses)
        assignments = [
            Assignments(name='Python Assignment 1', description='Basic Python exercises.', course_id=1, questions='What is a variable?; What is a function?'),
            Assignments(name='Web Development Assignment 1', description='Create a simple webpage.', course_id=2, questions='What is HTML?; What is CSS?'),
            Assignments(name='Data Science Assignment 1', description='Analyze a dataset.', course_id=3, questions='What is Pandas?; How do you visualize data?'),
            Assignments(name='Machine Learning Assignment 1', description='Implement a linear regression model.', course_id=4, questions='What is supervised learning?; What is overfitting?')
        ]
        db.session.bulk_save_objects(assignments)
        grades = [
            Grades(grade=85, assignment_id=1),
            Grades(grade=90, assignment_id=2),
            Grades(grade=75, assignment_id=3),
            Grades(grade=95, assignment_id=4)
        ]
        db.session.bulk_save_objects(grades)
        db.session.commit()
        print("Database populated successfully!")
        return "Database populated successfully!"


@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-learning Platform</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
        }
        h1 {
            font-size: 3em;
            color: #333;
            margin-bottom: 20px;
        }
        .button-container {
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            font-size: 1em;
            color: #fff;
            background-color: #007bff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>E-learning Platform</h1>
    <div class="button-container">
        <form action="/home" method="get">
            <button type="submit">Home</button>
        </form>
    </div>
</body>
</html>'''

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()
        if user is None:
            user = User(name=name, password=password)
            db.session.add(user)
            db.session.commit()
        else:
            if password != user.password:
                return render_template('nouser.html')
        courses = Courses.query.all()
        assignments = Assignments.query.all()
        grades = Grades.query.all()

        return render_template('login.html', user=user, courses=courses, assignments=assignments, grades=grades)
    
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    course = Courses.query.all()
    return render_template('courses.html', course=course)

@app.route('/course/<int:course_name>')
def course(course_name):
    course = Courses.query.filter_by(id=course_name).first()
    if course:
        assignments = Assignments.query.filter_by(course_id=course.id).all()
        return render_template('course.html', course=course, assignments=assignments)
    return "Course not found", 404

@app.route('/submit_assignment', methods=['POST'])
def submit_assignment():
    assignment_id = request.form['assignment_id']
    grade_value = request.form['grade']
    grade = Grades(grade=grade_value, assignment_id=assignment_id)
    db.session.add(grade)
    db.session.commit()
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Submission Status</title>
    <style>
        body {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: #ffffff;
            overflow: hidden;
        }
        .container {
            text-align: center;
            padding: 40px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            animation: fadeIn 1.5s ease-in-out;
        }
        h1 {
            font-size: 2.5em;
            margin: 0;
        }
        p {
            font-size: 1.2em;
            margin-top: 15px;
            color: #e0e0e0;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Answer Submitted Successfully</h1>
        <p>Your response has been recorded. Thank you!</p>
    </div>
</body>
</html>

'''

@app.route('/grades')
def grades():
    grades = Grades.query.all()
    return render_template('grades.html', grades=grades)
    

if __name__ == "__main__":
    app.run(debug=True, port=8000)
