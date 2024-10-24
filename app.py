from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Assignments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)

db.session.add(User(name='a',email='b'))
db.session.add(Courses(name='a',description='b',price=1))
db.session.add(Assignments(name='a',description='b',course_id=1))
db.session.add(Grades(grade=1,assignment_id=1))
db.session.commit()

@app.route('/')
def home():
    return "<h1>Default Page</h1>"

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if name not in User.query.all():
            user = User(name=name, email=email)
            db.session.add(user)
            db.session.commit()
            courses = Courses.query.all()
            assignments = Assignments.query.all()
            grades = Grades.query.all()
        else:
            if email != User.query.filter_by(name=name).first().email:
                return render_template('nouser.html')
            user = User.query.filter_by(name=name).first()
            courses = Courses.query.all()
            assignments = Assignments.query.all()
            grades = Grades.query.all()
        return render_template('login.html', user=user, courses=courses, assignments=assignments, grades=grades)


if __name__ == "__main__":
    app.run(debug=True, port=8000)