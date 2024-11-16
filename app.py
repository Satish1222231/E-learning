from flask import Flask, render_template, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

# Initializations

app = Flask(__name__)
CORS(app, support_credentials=True)
app.secret_key = '1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Enable cross-site cookies
app.config['SESSION_COOKIE_SECURE'] = True     # Required for HTTPS
db = SQLAlchemy(app)

# Table schemas

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80), nullable=False)

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    no_of_enrollments = db.Column(db.Integer, default=0)

class Registered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    completion_status = db.Column(db.Float, default=0.0)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    topic = db.Column(db.String(80))

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Float)

@app.route('/create_db')
def create_db():
    db.create_all()
    # courses = ['MongoDB', 'Flask', 'R Software']
    # for i in courses:
    #     course = Courses(name=i)
    #     db.session.add(course)
    # db.session.commit()
    return 'Database created successfully'

# Home page

@app.route('/')
def home():
    return render_template('home.html')

# Login Page

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')  # Extract 'name' for new user registration

    user = User.query.filter_by(name = name, email=email, password=password).first()

    if user:  # If user exists
        userdata = {'id': user.id, 'name': user.name}
        return jsonify(userdata)
    else:  # Register a new user
        if name:  # Ensure 'name' is provided for new user creation
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            userdata = {'id': new_user.id, 'name': new_user.name}
            return jsonify(userdata)
        else:
            return jsonify({"error": "Invalid credentials or missing name for registration"}), 400
    
@app.route('/get_courses', methods=['POST'])
def get_courses():
    courses = Courses.query.all()
    courses_list = [{'id': course.id, 'name': course.name, 'no_of_enrollments': course.no_of_enrollments} for course in courses]
    return jsonify({"courses": courses_list})

@app.route('/get_registered_courses', methods=['POST'])
def get_registered_courses():
    user = request.get_json()
    registered = Registered.query.filter_by(user_id=user.get('id')).all()
    registered_courses = [{'course_id': course.course_id, 'completion_status': course.completion_status} for course in registered]
    return jsonify({"registered_courses": registered_courses})

    
@app.route('/register_course/<int:course_id>', methods=['POST', 'GET'])
def register_course(course_id):
    user = request.get_json()
    course = Courses.query.filter_by(id=course_id).first()
    course.no_of_enrollments += 1
    db.session.commit()
    registered_course = Registered(user_id=user.get('id'), course_id=course_id)
    db.session.add(registered_course)
    db.session.commit()
    return jsonify({"message": "Course registered successfully"})

@app.route('/get_assignments/<int:course_id>', methods=['POST'])
def get_assignments(course_id):
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    assignments_list = [{'id': assignment.id, 'name': assignment.name, 'topic': assignment.topic} for assignment in assignments]
    return jsonify({"assignments": assignments_list})

@app.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
def submit_assignment(assignment_id):
    data = request.get_json()
    score = Scores(assignment_id=assignment_id, user_id=data.get('id'), score=data.get('score'))
    db.session.add(score)
    db.session.commit()
    scores = Scores.query.filter_by(assignment_id=assignment_id).all()
    highest = max([score.score for score in scores])
    return jsonify({'highest': highest})

@app.route('/delete_registration/<int:course_id>', methods=['POST'])
def delete_registration(course_id):
    data = request.get_json()
    registered = Registered.query.filter_by(user_id=data.get('id'), course_id=course_id).first()
    course = Courses.query.filter_by(id=course_id).first()
    course.no_of_enrollments -= 1
    db.session.delete(registered)
    db.session.commit()
    return jsonify({"message": "Course unregistered successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5500)